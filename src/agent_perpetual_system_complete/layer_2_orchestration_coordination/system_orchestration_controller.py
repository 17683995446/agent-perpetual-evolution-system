"""
System Orchestration Controller - 系统编排控制器（4个单词）

管理系统生命周期、启动/停止控制和优雅关闭。
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .task_execution_orchestrator import TaskExecutionOrchestrator
from ..layer_3_business_service.task_management_service_provider import TaskManagementServiceProvider
from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import get_structured_logger


class SystemState(str, Enum):
    """
    系统状态枚举
    """
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class SystemHealthStatus:
    """
    系统健康状态
    """
    state: SystemState
    is_healthy: bool
    uptime_seconds: float
    task_stats: Dict[str, Any]
    error_message: Optional[str] = None
    last_heartbeat: Optional[datetime] = None


@dataclass
class SystemConfiguration:
    """
    系统配置
    """
    max_concurrent_tasks: int = 10
    default_timeout_seconds: int = 300
    health_check_interval_seconds: int = 30
    graceful_shutdown_timeout_seconds: int = 30
    enable_auto_restart: bool = True
    max_restart_attempts: int = 3
    restart_delay_seconds: float = 5.0


class SystemOrchestrationController:
    """
    系统编排控制器

    核心职责：
    1. 管理整个系统的生命周期
    2. 协调各个子系统的启动和关闭
    3. 提供系统健康检查
    4. 处理错误恢复和自动重启
    5. 收集系统级指标
    """

    def __init__(self, config: Optional[SystemConfiguration] = None):
        self.config = config or SystemConfiguration()
        self.logger = get_structured_logger(__name__)

        self._state: SystemState = SystemState.STOPPED
        self._task_service: Optional[TaskManagementServiceProvider] = None
        self._orchestrator: Optional[TaskExecutionOrchestrator] = None
        self._start_time: Optional[datetime] = None
        self._error_count: int = 0
        self._health_check_task: Optional[asyncio.Task] = None
        self._main_loop_task: Optional[asyncio.Task] = None

    async def start(self) -> bool:
        """
        启动系统

        Returns:
            是否成功启动
        """
        try:
            self.logger.info("system_starting")
            self._state = SystemState.INITIALIZING

            await self._initialize_subsystems()

            self._start_time = datetime.utcnow()
            self._state = SystemState.RUNNING

            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._main_loop_task = asyncio.create_task(self._main_execution_loop())

            self.logger.info(
                "system_started",
                state=self._state.value,
                start_time=self._start_time.isoformat(),
            )

            return True

        except Exception as e:
            self.logger.error("system_start_failed", error=str(e))
            self._state = SystemState.ERROR
            return False

    async def stop(self, graceful: bool = True) -> bool:
        """
        停止系统

        Args:
            graceful: 是否优雅关闭

        Returns:
            是否成功停止
        """
        try:
            self.logger.info("system_stopping", graceful=graceful)
            self._state = SystemState.STOPPING

            if graceful and self._orchestrator:
                await self._orchestrator.graceful_shutdown()

            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass

            if self._main_loop_task:
                self._main_loop_task.cancel()
                try:
                    await self._main_loop_task
                except asyncio.CancelledError:
                    pass

            await self._shutdown_subsystems()

            self._state = SystemState.STOPPED

            self.logger.info("system_stopped")
            return True

        except Exception as e:
            self.logger.error("system_stop_failed", error=str(e))
            self._state = SystemState.ERROR
            return False

    async def pause(self) -> bool:
        """
        暂停系统

        Returns:
            是否成功暂停
        """
        if self._state != SystemState.RUNNING:
            self.logger.warning("cannot_pause_system_not_running", current_state=self._state.value)
            return False

        self._state = SystemState.PAUSED
        self.logger.info("system_paused")
        return True

    async def resume(self) -> bool:
        """
        恢复系统

        Returns:
            是否成功恢复
        """
        if self._state != SystemState.PAUSED:
            self.logger.warning("cannot_resume_system_not_paused", current_state=self._state.value)
            return False

        self._state = SystemState.RUNNING
        self.logger.info("system_resumed")
        return True

    async def get_health_status(self) -> SystemHealthStatus:
        """
        获取系统健康状态

        Returns:
            系统健康状态
        """
        uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0.0

        task_stats = {}
        if self._task_service:
            try:
                task_stats = await self._task_service.get_task_statistics_report()
            except Exception as e:
                self.logger.warning("failed_to_get_task_statistics", error=str(e))

        is_healthy = self._state in [SystemState.RUNNING, SystemState.PAUSED] and self._error_count < 3

        return SystemHealthStatus(
            state=self._state,
            is_healthy=is_healthy,
            uptime_seconds=uptime_seconds,
            task_stats=task_stats,
            last_heartbeat=datetime.utcnow(),
        )

    async def restart(self) -> bool:
        """
        重启系统

        Returns:
            是否成功重启
        """
        self.logger.info("system_restarting")

        await self.stop(graceful=True)
        await asyncio.sleep(self.config.restart_delay_seconds)

        return await self.start()

    async def _initialize_subsystems(self) -> None:
        """
        初始化子系统
        """
        self.logger.info("initializing_subsystems")

        db_url = "sqlite+aiosqlite:///./agent_system.db"
        self._task_service = TaskManagementServiceProvider(db_url)
        await self._task_service.initialize()

        self._orchestrator = TaskExecutionOrchestrator(
            self._task_service,
        )
        await self._orchestrator.initialize()

        self.logger.info("subsystems_initialized")

    async def _shutdown_subsystems(self) -> None:
        """
        关闭子系统
        """
        self.logger.info("shutting_down_subsystems")

        if self._orchestrator:
            await self._orchestrator.graceful_shutdown()

        self.logger.info("subsystems_shutdown_complete")

    async def _health_check_loop(self) -> None:
        """
        健康检查循环
        """
        self.logger.info("health_check_loop_started")

        while self._state in [SystemState.RUNNING, SystemState.PAUSED]:
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)

                health = await self.get_health_status()

                self.logger.debug(
                    "health_check",
                    state=health.state.value,
                    is_healthy=health.is_healthy,
                    uptime_seconds=health.uptime_seconds,
                )

                if not health.is_healthy and self.config.enable_auto_restart:
                    self.logger.warning("system_unhealthy_initiating_restart")
                    await self.restart()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("health_check_failed", error=str(e))
                self._error_count += 1

        self.logger.info("health_check_loop_stopped")

    async def _main_execution_loop(self) -> None:
        """
        主执行循环
        """
        self.logger.info("main_execution_loop_started")

        while self._state == SystemState.RUNNING:
            try:
                if self._orchestrator and self._task_service:
                    pending_tasks = await self._task_service.get_pending_tasks_for_execution(limit=10)

                    if pending_tasks:
                        task_ids = [task.task_identifier for task in pending_tasks]
                        await self._orchestrator.execute_tasks_batch(task_ids)

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("main_loop_error", error=str(e))
                self._error_count += 1
                await asyncio.sleep(5)

        self.logger.info("main_execution_loop_stopped")

    @property
    def state(self) -> SystemState:
        """
        获取当前系统状态
        """
        return self._state

    @property
    def orchestrator(self) -> Optional[TaskExecutionOrchestrator]:
        """
        获取任务编排器
        """
        return self._orchestrator

    @property
    def task_service(self) -> Optional[TaskManagementServiceProvider]:
        """
        获取任务服务
        """
        return self._task_service
