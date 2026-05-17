"""
Agent Pool Manager - Agent池管理器（4个单词）

负责Agent的生命周期管理、注册发现、负载均衡和健康检查。
"""

import asyncio
import time
import psutil
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


class AgentStatus(str, Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    INITIALIZING = "initializing"
    FAILED = "failed"
    OFFLINE = "offline"


class AgentType(str, Enum):
    """Agent类型枚举"""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    MONITOR = "monitor"
    LEARNER = "learner"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentMetrics:
    """Agent性能指标"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    last_heartbeat: Optional[datetime] = None
    success_rate: float = 1.0


@dataclass
class AgentInstance:
    """Agent实例"""
    agent_id: str
    agent_type: AgentType
    name: str
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[str] = field(default_factory=list)
    current_task_id: Optional[str] = None
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

    def __post_init__(self):
        self.metrics.last_heartbeat = self.created_at


@dataclass
class AgentPoolConfiguration:
    """Agent池配置"""
    max_agents: int = 10
    min_agents: int = 2
    health_check_interval_seconds: int = 30
    heartbeat_timeout_seconds: int = 60
    max_task_queue_size: int = 100
    enable_auto_scaling: bool = True
    scaling_threshold_high: float = 0.8
    scaling_threshold_low: float = 0.2
    scale_up_cooldown_seconds: int = 60
    scale_down_cooldown_seconds: int = 300


class AgentPoolManager:
    """
    Agent池管理器
    
    核心职责：
    1. Agent生命周期管理（创建、启动、停止、重启）
    2. Agent注册与发现
    3. Agent负载均衡
    4. Agent健康检查
    5. 自动扩缩容
    """

    def __init__(self, config: Optional[AgentPoolConfiguration] = None):
        self.config = config or AgentPoolConfiguration()
        self.logger = get_structured_logger(__name__)

        self._agents: Dict[str, AgentInstance] = {}
        self._agents_by_type: Dict[AgentType, Set[str]] = defaultdict(set)
        self._agents_by_capability: Dict[str, Set[str]] = defaultdict(set)
        self._task_assignments: Dict[str, str] = {}
        self._is_running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._last_scale_up_time: Optional[datetime] = None
        self._last_scale_down_time: Optional[datetime] = None

    async def initialize(self) -> None:
        """初始化Agent池"""
        self.logger.info(
            "initializing_agent_pool_manager",
            max_agents=self.config.max_agents,
            min_agents=self.config.min_agents,
            auto_scaling=self.config.enable_auto_scaling,
        )

        self._is_running = True
        await self._create_initial_agents()

        self._health_check_task = asyncio.create_task(self._health_check_loop())

        self.logger.info("agent_pool_manager_initialized", agent_count=len(self._agents))

    async def _create_initial_agents(self) -> None:
        """创建初始Agent"""
        initial_agents = [
            AgentInstance(
                agent_id="agent-orchestrator-1",
                agent_type=AgentType.ORCHESTRATOR,
                name="Orchestrator Agent 1",
                capabilities=["orchestration", "workflow_management", "task_scheduling"],
            ),
            AgentInstance(
                agent_id="agent-executor-1",
                agent_type=AgentType.EXECUTOR,
                name="Executor Agent 1",
                capabilities=["task_execution", "data_processing"],
            ),
            AgentInstance(
                agent_id="agent-executor-2",
                agent_type=AgentType.EXECUTOR,
                name="Executor Agent 2",
                capabilities=["task_execution", "computation"],
            ),
            AgentInstance(
                agent_id="agent-monitor-1",
                agent_type=AgentType.MONITOR,
                name="Monitor Agent 1",
                capabilities=["monitoring", "health_check", "metrics_collection"],
            ),
            AgentInstance(
                agent_id="agent-learner-1",
                agent_type=AgentType.LEARNER,
                name="Learner Agent 1",
                capabilities=["learning", "pattern_recognition", "optimization"],
            ),
        ]

        for agent in initial_agents:
            await self.register_agent(agent)

    async def register_agent(self, agent: AgentInstance) -> bool:
        """
        注册Agent到池中
        
        Args:
            agent: Agent实例
            
        Returns:
            注册是否成功
        """
        if len(self._agents) >= self.config.max_agents:
            self.logger.warning(
                "agent_registration_failed_pool_full",
                agent_id=agent.agent_id,
                max_agents=self.config.max_agents,
            )
            return False

        agent.status = AgentStatus.IDLE
        agent.last_updated = datetime.utcnow()

        self._agents[agent.agent_id] = agent
        self._agents_by_type[agent.agent_type].add(agent.agent_id)

        for capability in agent.capabilities:
            self._agents_by_capability[capability].add(agent.agent_id)

        self.logger.info(
            "agent_registered",
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            capabilities=agent.capabilities,
        )

        return True

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        从池中移除Agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            移除是否成功
        """
        if agent_id not in self._agents:
            self.logger.warning("agent_not_found", agent_id=agent_id)
            return False

        agent = self._agents[agent_id]

        if agent.status == AgentStatus.BUSY:
            self.logger.warning(
                "cannot_unregister_busy_agent",
                agent_id=agent_id,
                current_task=agent.current_task_id,
            )
            return False

        self._agents_by_type[agent.agent_type].discard(agent_id)
        for capability in agent.capabilities:
            self._agents_by_capability[capability].discard(agent_id)

        del self._agents[agent_id]

        self.logger.info("agent_unregistered", agent_id=agent_id)

        return True

    async def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """获取Agent实例"""
        return self._agents.get(agent_id)

    async def find_available_agent(
        self,
        agent_type: Optional[AgentType] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> Optional[AgentInstance]:
        """
        查找可用的Agent
        
        Args:
            agent_type: 指定的Agent类型
            required_capabilities: 必需的能力列表
            
        Returns:
            可用的Agent实例，如果没有则返回None
        """
        candidates = []

        if agent_type:
            agent_ids = self._agents_by_type.get(agent_type, set())
        else:
            agent_ids = set(self._agents.keys())

        if required_capabilities:
            capability_candidates = set()
            for capability in required_capabilities:
                capability_candidates.update(
                    self._agents_by_capability.get(capability, set())
                )
            agent_ids &= capability_candidates

        for agent_id in agent_ids:
            agent = self._agents[agent_id]
            if agent.status == AgentStatus.IDLE:
                candidates.append(agent)

        if not candidates:
            self.logger.warning(
                "no_available_agent",
                agent_type=agent_type,
                required_capabilities=required_capabilities,
            )
            return None

        selected = self._select_agent_by_load(candidates)

        self.logger.info(
            "agent_selected",
            agent_id=selected.agent_id,
            agent_type=selected.agent_type,
            selection_reason="load_balancing",
        )

        return selected

    def _select_agent_by_load(self, candidates: List[AgentInstance]) -> AgentInstance:
        """
        基于负载选择Agent
        
        使用加权评分选择负载最低的Agent
        """
        scores = []
        for agent in candidates:
            success_rate = agent.metrics.success_rate
            avg_time = agent.metrics.average_execution_time
            cpu_usage = agent.metrics.cpu_usage_percent

            score = (
                success_rate * 0.4 +
                (1.0 / (avg_time + 1.0)) * 0.3 +
                (1.0 - cpu_usage / 100.0) * 0.3
            )

            scores.append((score, agent))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[0][1]

    async def assign_task_to_agent(
        self,
        task_id: str,
        agent_id: Optional[str] = None,
        agent_type: Optional[AgentType] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> Optional[AgentInstance]:
        """
        为任务分配Agent
        
        Args:
            task_id: 任务ID
            agent_id: 指定Agent ID
            agent_type: Agent类型
            required_capabilities: 必需的能力
            
        Returns:
            被分配的Agent实例
        """
        if agent_id:
            agent = self._agents.get(agent_id)
            if not agent or agent.status != AgentStatus.IDLE:
                self.logger.warning(
                    "specified_agent_unavailable",
                    agent_id=agent_id,
                )
                return None
        else:
            agent = await self.find_available_agent(agent_type, required_capabilities)
            if not agent:
                return None

        agent.status = AgentStatus.BUSY
        agent.current_task_id = task_id
        agent.last_updated = datetime.utcnow()

        self._task_assignments[task_id] = agent.agent_id

        self.logger.info(
            "task_assigned_to_agent",
            task_id=task_id,
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
        )

        return agent

    async def release_agent(self, agent_id: str, task_success: bool = True) -> bool:
        """
        释放Agent回到空闲状态
        
        Args:
            agent_id: Agent ID
            task_success: 任务是否成功
            
        Returns:
            释放是否成功
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return False

        if agent.status != AgentStatus.BUSY:
            return False

        task_id = agent.current_task_id

        if task_id in self._task_assignments:
            del self._task_assignments[task_id]

        if task_success:
            agent.metrics.tasks_completed += 1
        else:
            agent.metrics.tasks_failed += 1

        total_tasks = agent.metrics.tasks_completed + agent.metrics.tasks_failed
        if total_tasks > 0:
            agent.metrics.success_rate = agent.metrics.tasks_completed / total_tasks

        agent.status = AgentStatus.IDLE
        agent.current_task_id = None
        agent.last_updated = datetime.utcnow()

        await self._update_agent_metrics(agent)

        self.logger.info(
            "agent_released",
            agent_id=agent_id,
            task_id=task_id,
            task_success=task_success,
            metrics=agent.metrics.__dict__,
        )

        if self.config.enable_auto_scaling:
            await self._check_auto_scaling()

        return True

    async def _update_agent_metrics(self, agent: AgentInstance) -> None:
        """更新Agent性能指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()

            agent.metrics.cpu_usage_percent = cpu_percent / len(self._agents)
            agent.metrics.memory_usage_mb = memory_info.used / (1024 * 1024)

            if agent.metrics.tasks_completed > 0:
                agent.metrics.average_execution_time = (
                    agent.metrics.total_execution_time / agent.metrics.tasks_completed
                )

        except Exception as e:
            self.logger.warning("failed_to_update_agent_metrics", error=str(e))

    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        self.logger.info("health_check_loop_started")

        while self._is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except Exception as e:
                self.logger.error(
                    "health_check_loop_error",
                    error=str(e),
                )

        self.logger.info("health_check_loop_stopped")

    async def _perform_health_check(self) -> None:
        """执行健康检查"""
        current_time = datetime.utcnow()
        timeout = timedelta(seconds=self.config.heartbeat_timeout_seconds)

        for agent_id, agent in list(self._agents.items()):
            time_since_heartbeat = current_time - agent.metrics.last_heartbeat

            if time_since_heartbeat > timeout:
                if agent.status == AgentStatus.BUSY:
                    self.logger.warning(
                        "agent_heartbeat_timeout_but_busy",
                        agent_id=agent_id,
                        last_heartbeat=agent.metrics.last_heartbeat,
                    )
                else:
                    self.logger.warning(
                        "agent_heartbeat_timeout",
                        agent_id=agent_id,
                        last_heartbeat=agent.metrics.last_heartbeat,
                    )
                    agent.status = AgentStatus.OFFLINE

            await self._update_agent_metrics(agent)

        healthy_count = sum(
            1 for agent in self._agents.values()
            if agent.status in [AgentStatus.IDLE, AgentStatus.BUSY]
        )

        self.logger.debug(
            "health_check_completed",
            total_agents=len(self._agents),
            healthy_agents=healthy_count,
            busy_agents=sum(1 for a in self._agents.values() if a.status == AgentStatus.BUSY),
        )

    async def _check_auto_scaling(self) -> None:
        """检查是否需要自动扩缩容"""
        if not self.config.enable_auto_scaling:
            return

        total_agents = len(self._agents)
        busy_agents = sum(1 for a in self._agents.values() if a.status == AgentStatus.BUSY)

        if total_agents == 0:
            return

        utilization = busy_agents / total_agents

        current_time = datetime.utcnow()

        if utilization > self.config.scaling_threshold_high:
            if self._can_scale_up(current_time):
                await self._scale_up()
                self._last_scale_up_time = current_time

        elif utilization < self.config.scaling_threshold_low:
            if self._can_scale_down(current_time) and total_agents > self.config.min_agents:
                await self._scale_down()
                self._last_scale_down_time = current_time

    def _can_scale_up(self, current_time: datetime) -> bool:
        """检查是否可以扩容"""
        if self._last_scale_up_time is None:
            return True

        cooldown = timedelta(seconds=self.config.scale_up_cooldown_seconds)
        return current_time - self._last_scale_up_time > cooldown

    def _can_scale_down(self, current_time: datetime) -> bool:
        """检查是否可以缩容"""
        if self._last_scale_down_time is None:
            return True

        cooldown = timedelta(seconds=self.config.scale_down_cooldown_seconds)
        return current_time - self._last_scale_down_time > cooldown

    async def _scale_up(self) -> None:
        """扩容Agent池"""
        if len(self._agents) >= self.config.max_agents:
            return

        agent_number = len(self._agents) + 1
        new_agent = AgentInstance(
            agent_id=f"agent-scaled-{agent_number}",
            agent_type=AgentType.EXECUTOR,
            name=f"Scaled Executor {agent_number}",
            capabilities=["task_execution", "data_processing"],
        )

        await self.register_agent(new_agent)

        self.logger.info(
            "agent_pool_scaled_up",
            new_agent_id=new_agent.agent_id,
            total_agents=len(self._agents),
        )

    async def _scale_down(self) -> None:
        """缩容Agent池"""
        if len(self._agents) <= self.config.min_agents:
            return

        idle_agents = [
            (agent_id, agent)
            for agent_id, agent in self._agents.items()
            if agent.status == AgentStatus.IDLE
        ]

        if not idle_agents:
            self.logger.warning("no_idle_agents_for_scale_down")
            return

        agent_id_to_remove = idle_agents[0][0]
        await self.unregister_agent(agent_id_to_remove)

        self.logger.info(
            "agent_pool_scaled_down",
            removed_agent_id=agent_id_to_remove,
            total_agents=len(self._agents),
        )

    async def get_pool_status(self) -> Dict[str, Any]:
        """获取Agent池状态"""
        status_by_type = {}
        for agent_type in AgentType:
            agents = [
                agent for agent in self._agents.values()
                if agent.agent_type == agent_type
            ]
            status_by_type[agent_type.value] = {
                "total": len(agents),
                "idle": sum(1 for a in agents if a.status == AgentStatus.IDLE),
                "busy": sum(1 for a in agents if a.status == AgentStatus.BUSY),
                "offline": sum(1 for a in agents if a.status == AgentStatus.OFFLINE),
            }

        return {
            "total_agents": len(self._agents),
            "max_agents": self.config.max_agents,
            "min_agents": self.config.min_agents,
            "status_by_type": status_by_type,
            "auto_scaling_enabled": self.config.enable_auto_scaling,
            "running": self._is_running,
        }

    async def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取Agent详细信息"""
        agent = self._agents.get(agent_id)
        if not agent:
            return None

        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type.value,
            "name": agent.name,
            "status": agent.status.value,
            "capabilities": agent.capabilities,
            "current_task_id": agent.current_task_id,
            "metrics": agent.metrics.__dict__,
            "config": agent.config,
            "created_at": agent.created_at.isoformat(),
            "last_updated": agent.last_updated.isoformat(),
            "version": agent.version,
        }

    async def shutdown(self) -> None:
        """关闭Agent池管理器"""
        self.logger.info("shutting_down_agent_pool_manager")
        self._is_running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        busy_agents = [
            agent_id for agent_id, agent in self._agents.items()
            if agent.status == AgentStatus.BUSY
        ]

        if busy_agents:
            self.logger.warning(
                "shutdown_with_busy_agents",
                busy_agents=busy_agents,
            )

        self.logger.info(
            "agent_pool_manager_shutdown",
            total_agents=len(self._agents),
            agents_unregistered=len(self._agents),
        )
