"""
调度器模块 - 产品级主循环调度系统
"""

import asyncio
import signal
from typing import Optional
from ..core.config import get_settings
from ..core.logging import get_logger, setup_logging
from ..core.database import init_database, create_tables
from ..core.models import Mode, EvolutionPhase
from ..modules.task_service import TaskService
from ..modules.evolution_engine import EvolutionEngine

logger = get_logger(__name__)


class AgentScheduler:
    """主调度器，负责工作模式和进化模式的协调"""

    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.task_service = TaskService()
        self.evolution_engine = EvolutionEngine()
        self.current_mode = Mode.IDLE
        self.current_phase_index = 0

    async def start(self) -> None:
        """启动调度器"""
        logger.info("starting_agent_scheduler")
        
        setup_logging()
        init_database()
        await create_tables()
        
        self.running = True
        self._setup_signal_handlers()
        
        logger.info("agent_scheduler_started")
        
        await self._main_loop()

    def stop(self) -> None:
        """停止调度器"""
        logger.info("stopping_agent_scheduler")
        self.running = False

    def _setup_signal_handlers(self) -> None:
        """设置信号处理"""
        loop = asyncio.get_running_loop()
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, self.stop)

    async def _main_loop(self) -> None:
        """主循环"""
        while self.running:
            try:
                pending_tasks = await self.task_service.get_pending_tasks()
                
                if pending_tasks:
                    await self._handle_working_mode(pending_tasks[0])
                else:
                    await self._handle_evolution_mode()
                
                await asyncio.sleep(self.settings.poll_interval)
                
            except Exception as e:
                logger.error(
                    "main_loop_error",
                    error=str(e),
                    exc_info=True,
                )
                await asyncio.sleep(1)

    async def _handle_working_mode(self, task) -> None:
        """处理工作模式"""
        if self.current_mode != Mode.WORKING:
            logger.info("switching_to_working_mode")
            self.current_mode = Mode.WORKING
        
        logger.info("executing_task", task_id=task.task_id)
        await self.task_service.run_task(task)

    async def _handle_evolution_mode(self) -> None:
        """处理进化模式"""
        if not self.settings.enable_evolution:
            if self.current_mode != Mode.IDLE:
                self.current_mode = Mode.IDLE
            return

        if self.current_mode != Mode.EVOLUTION:
            logger.info("switching_to_evolution_mode")
            self.current_mode = Mode.EVOLUTION

        phases = self.evolution_engine.phases
        if self.current_phase_index >= len(phases):
            self.current_phase_index = 0

        current_phase = phases[self.current_phase_index]
        
        # 检查是否有新任务到达，如果有则中断进化
        pending_tasks = await self.task_service.get_pending_tasks()
        if pending_tasks:
            logger.info("new_task_arrived_interrupting_evolution")
            return

        await self.evolution_engine.run_phase(current_phase)
        self.current_phase_index += 1
