"""
Evolution Engine - 自主进化引擎

该模块是进化系统的核心，负责：
- 进化阶段调度
- 进化流程编排
- 进化状态管理
- 进化进度跟踪
"""

import asyncio
from typing import Dict, List, Any, Optional
from ...core.logger_config import get_structured_logger
from ...core.config_manager import get_application_settings
from ...core.database_models import EvolutionPhaseEnum, RunningModeEnum
from .memory_cleanup_manager import MemoryCleanupManager
from .strategy_optimizer import StrategyOptimizer
from .knowledge_learner import KnowledgeLearner

logger = get_structured_logger(__name__)


class EvolutionEngine:
    """
    自主进化引擎

    负责系统的自主进化流程：
    - 记忆整理与清理
    - 执行策略优化
    - 知识学习与补强

    进化过程在系统空闲时自动执行，不断提升系统能力。
    """

    def __init__(self):
        self.settings = get_application_settings()
        self.enabled = self.settings.evolution_enabled

        # 初始化各阶段管理器
        self.memory_cleanup_manager = MemoryCleanupManager()
        self.strategy_optimizer = StrategyOptimizer()
        self.knowledge_learner = KnowledgeLearner()

        # 进化阶段定义
        self.evolution_phases = [
            EvolutionPhaseEnum.MEMORY_CLEANUP,
            EvolutionPhaseEnum.STRATEGY_OPTIMIZE,
            EvolutionPhaseEnum.KNOWLEDGE_LEARNING,
        ]

        # 当前阶段索引
        self.current_phase_index = 0

        logger.info(
            "evolution_engine_initialized",
            enabled=self.enabled,
            phases_count=len(self.evolution_phases)
        )

    async def execute_evolution_cycle(self) -> Dict[str, Any]:
        """
        执行一个完整的进化周期

        按顺序执行所有进化阶段

        Returns:
            Dict: 包含进化结果的字典

        Example:
            >>> engine = EvolutionEngine()
            >>> result = await engine.execute_evolution_cycle()
            >>> print(f"Evolution completed: {result['status']}")
        """
        if not self.enabled:
            logger.info("evolution_disabled")
            return {
                "status": "skipped",
                "reason": "Evolution is disabled in configuration"
            }

        logger.info("evolution_cycle_started")

        phase_results = []
        total_time = 0

        # 执行所有进化阶段
        for phase in self.evolution_phases:
            phase_start = asyncio.get_event_loop().time()
            phase_result = await self._execute_single_phase(phase)
            phase_time = asyncio.get_event_loop().time() - phase_start

            phase_results.append({
                "phase": phase,
                "result": phase_result,
                "execution_time": phase_time
            })

            total_time += phase_time

            logger.info(
                "evolution_phase_completed",
                phase=phase,
                execution_time=phase_time,
                status=phase_result["status"]
            )

        # 重置阶段索引
        self.current_phase_index = 0

        logger.info(
            "evolution_cycle_completed",
            total_phases=len(self.evolution_phases),
            total_time=total_time
        )

        return {
            "status": "success",
            "phases_completed": len(self.evolution_phases),
            "phase_results": phase_results,
            "total_execution_time": total_time
        }

    async def _execute_single_phase(self, phase: str) -> Dict[str, Any]:
        """
        执行单个进化阶段

        Args:
            phase: 进化阶段名称

        Returns:
            Dict: 阶段执行结果
        """
        logger.info("evolution_phase_started", phase=phase)

        try:
            if phase == EvolutionPhaseEnum.MEMORY_CLEANUP:
                result = await self.memory_cleanup_manager.execute_memory_cleanup()
            elif phase == EvolutionPhaseEnum.STRATEGY_OPTIMIZE:
                result = await self.strategy_optimizer.execute_strategy_optimization()
            elif phase == EvolutionPhaseEnum.KNOWLEDGE_LEARNING:
                result = await self.knowledge_learner.execute_knowledge_learning()
            else:
                result = {
                    "status": "skipped",
                    "reason": f"Unknown phase: {phase}"
                }

            return {
                "status": "success",
                "phase": phase,
                "result": result
            }

        except Exception as e:
            logger.error(
                "evolution_phase_failed",
                phase=phase,
                error=str(e),
                exc_info=True
            )
            return {
                "status": "failed",
                "phase": phase,
                "error": str(e)
            }

    async def execute_single_phase_by_name(self, phase_name: str) -> Dict[str, Any]:
        """
        根据名称执行单个进化阶段

        Args:
            phase_name: 阶段名称

        Returns:
            Dict: 阶段执行结果

        Example:
            >>> result = await engine.execute_single_phase_by_name("memory_cleanup")
        """
        return await self._execute_single_phase(phase_name)

    async def get_evolution_status(self) -> Dict[str, Any]:
        """
        获取进化系统状态

        Returns:
            Dict: 包含状态信息的字典

        Example:
            >>> status = await engine.get_evolution_status()
            >>> print(f"Enabled: {status['enabled']}")
        """
        # 获取各子系统的状态
        memory_stats = await self.memory_cleanup_manager.get_memory_statistics()
        strategy_report = await self.strategy_optimizer.get_strategy_effectiveness_report()
        knowledge_stats = await self.knowledge_learner.get_knowledge_statistics()

        return {
            "enabled": self.enabled,
            "phases": self.evolution_phases,
            "current_phase_index": self.current_phase_index,
            "memory_statistics": memory_stats,
            "strategy_effectiveness": strategy_report,
            "knowledge_statistics": knowledge_stats,
        }

    async def run_continuous_evolution(self, stop_event: asyncio.Event = None):
        """
        运行持续进化循环

        在系统空闲时持续执行进化，直到被停止

        Args:
            stop_event: 停止事件，当被设置时停止进化

        Example:
            >>> stop_event = asyncio.Event()
            >>> await engine.run_continuous_evolution(stop_event)
        """
        if not self.enabled:
            logger.info("evolution_disabled_continuous_run")
            return

        logger.info("continuous_evolution_started")

        iteration = 0
        while not (stop_event and stop_event.is_set()):
            iteration += 1

            logger.info(
                "evolution_iteration_started",
                iteration=iteration
            )

            try:
                result = await self.execute_evolution_cycle()

                logger.info(
                    "evolution_iteration_completed",
                    iteration=iteration,
                    status=result["status"]
                )

            except Exception as e:
                logger.error(
                    "evolution_iteration_failed",
                    iteration=iteration,
                    error=str(e)
                )

            # 进化间隔
            await asyncio.sleep(self.settings.task_poll_interval)

        logger.info("continuous_evolution_stopped")
