"""
Evolution Engine Controller - 进化引擎控制器（4个单词）

整合内存清理、策略优化、知识学习等模块的核心控制器。
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .memory_cleanup_service_provider import (
    MemoryCleanupServiceProvider,
    CleanupPolicy,
    MemoryUsageStats,
)
from .strategy_optimization_service_provider import (
    StrategyOptimizationServiceProvider,
    OptimizationStrategy,
    OptimizationResult,
)
from .knowledge_learning_service_provider import (
    KnowledgeLearningServiceProvider,
    OutcomeCategory,
    Recommendation,
)
from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import get_structured_logger


class EvolutionStage(str, Enum):
    """
    进化阶段
    """
    INITIALIZING = "initializing"
    LEARNING = "learning"
    OPTIMIZING = "optimizing"
    MATURING = "maturing"
    STABLE = "stable"


@dataclass
class EvolutionMetrics:
    """
    进化指标
    """
    stage: EvolutionStage
    iterations_completed: int
    total_optimizations: int
    patterns_learned: int
    memory_optimized_bytes: int
    avg_performance_improvement: float
    uptime_seconds: float


class EvolutionEngineController:
    """
    进化引擎控制器

    核心职责：
    1. 整合所有进化相关服务
    2. 协调整个进化过程
    3. 提供统一的进化控制接口
    4. 生成进化仪表盘数据
    """

    def __init__(
        self,
        memory_cleanup: Optional[MemoryCleanupServiceProvider] = None,
        strategy_optimization: Optional[StrategyOptimizationServiceProvider] = None,
        knowledge_learning: Optional[KnowledgeLearningServiceProvider] = None,
    ):
        self.logger = get_structured_logger(__name__)

        self._memory_cleanup = memory_cleanup or MemoryCleanupServiceProvider()
        self._strategy_optimization = strategy_optimization or StrategyOptimizationServiceProvider()
        self._knowledge_learning = knowledge_learning or KnowledgeLearningServiceProvider()

        self._stage = EvolutionStage.INITIALIZING
        self._start_time: Optional[datetime] = None
        self._iterations_completed = 0
        self._total_optimizations = 0
        self._memory_optimized_bytes = 0
        self._evolution_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self) -> None:
        """
        启动进化引擎
        """
        if self._is_running:
            self.logger.warning("evolution_engine_already_running")
            return

        self.logger.info("starting_evolution_engine")
        self._is_running = True
        self._start_time = datetime.utcnow()
        self._stage = EvolutionStage.LEARNING

        # 启动各个子服务
        await self._memory_cleanup.start()
        await self._strategy_optimization.start()
        await self._knowledge_learning.start()

        # 启动主进化循环
        self._evolution_task = asyncio.create_task(self._evolution_loop())

        self.logger.info("evolution_engine_started", stage=self._stage)

    async def stop(self) -> None:
        """
        停止进化引擎
        """
        if not self._is_running:
            self.logger.warning("evolution_engine_not_running")
            return

        self.logger.info("stopping_evolution_engine")
        self._is_running = False
        self._stage = EvolutionStage.STABLE

        if self._evolution_task:
            self._evolution_task.cancel()
            try:
                await self._evolution_task
            except asyncio.CancelledError:
                pass

        # 停止各个子服务
        await self._knowledge_learning.stop()
        await self._strategy_optimization.stop()
        await self._memory_cleanup.stop()

        self.logger.info("evolution_engine_stopped")

    async def register_optimization_strategy(self, strategy: OptimizationStrategy) -> None:
        """
        注册优化策略

        Args:
            strategy: 优化策略
        """
        await self._strategy_optimization.register_strategy(strategy)

    async def record_execution(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        记录执行结果

        Args:
            input_data: 输入数据
            output_data: 输出数据
            success: 是否成功
            metadata: 元数据

        Returns:
            案例ID
        """
        outcome = OutcomeCategory.SUCCESS if success else OutcomeCategory.FAILURE

        case_id = await self._knowledge_learning.record_case(
            input_data=input_data,
            output_data=output_data,
            outcome=outcome,
            metadata=metadata,
        )

        # 记录性能指标
        latency = metadata.get("latency", 0) if metadata else 0
        throughput = metadata.get("throughput", 0) if metadata else 0
        error_rate = 0.0 if success else 1.0

        if self._strategy_optimization._strategies:
            strategy_name = self._strategy_optimization._strategies[0].name
            await self._strategy_optimization.record_performance(
                strategy_name=strategy_name,
                metric_name="latency",
                value=latency,
            )
            await self._strategy_optimization.record_performance(
                strategy_name=strategy_name,
                metric_name="throughput",
                value=throughput,
            )
            await self._strategy_optimization.record_performance(
                strategy_name=strategy_name,
                metric_name="error_rate",
                value=error_rate,
            )

        return case_id

    async def get_recommendations(
        self,
        input_data: Dict[str, Any],
        top_k: int = 5,
    ) -> List[Recommendation]:
        """
        获取建议

        Args:
            input_data: 输入数据
            top_k: 返回前K个建议

        Returns:
            建议列表
        """
        return await self._knowledge_learning.get_recommendations(input_data, top_k)

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        获取进化仪表盘数据

        Returns:
            仪表盘数据字典
        """
        memory_stats = await self._memory_cleanup.get_memory_stats()
        pattern_stats = await self._knowledge_learning.get_pattern_statistics()
        evolution_metrics = await self._get_evolution_metrics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": evolution_metrics.stage,
            "memory": {
                "used_percent": memory_stats.used_percent,
                "total_bytes": memory_stats.total_bytes,
                "used_bytes": memory_stats.used_bytes,
                "optimized_bytes": self._memory_optimized_bytes,
                "temperature_breakdown": {
                    "hot": memory_stats.hot_data_bytes,
                    "warm": memory_stats.warm_data_bytes,
                    "cold": memory_stats.cold_data_bytes,
                    "frozen": memory_stats.frozen_data_bytes,
                },
            },
            "patterns": {
                "total": pattern_stats["total_patterns"],
                "success": pattern_stats["success_patterns"],
                "failure": pattern_stats["failure_patterns"],
                "optimization": pattern_stats["optimization_patterns"],
                "avg_confidence": pattern_stats["avg_confidence"],
            },
            "evolution": {
                "iterations_completed": evolution_metrics.iterations_completed,
                "total_optimizations": evolution_metrics.total_optimizations,
                "uptime_seconds": evolution_metrics.uptime_seconds,
                "avg_performance_improvement": evolution_metrics.avg_performance_improvement,
            },
        }

    async def force_optimization(self, strategy_name: Optional[str] = None) -> Optional[OptimizationResult]:
        """
        强制优化

        Args:
            strategy_name: 策略名称，None表示优化所有

        Returns:
            优化结果
        """
        if strategy_name:
            result = await self._strategy_optimization.optimize(strategy_name)
            if result:
                self._total_optimizations += 1
            return result
        else:
            # 优化所有策略
            for strategy in self._strategy_optimization._strategies:
                result = await self._strategy_optimization.optimize(strategy.name)
                if result:
                    self._total_optimizations += 1
            return None

    async def force_memory_cleanup(self) -> Dict[str, Any]:
        """
        强制内存清理

        Returns:
            清理结果
        """
        result = await self._memory_cleanup.force_cleanup()
        self._memory_optimized_bytes += result.get("bytes_freed", 0)
        return result

    async def _evolution_loop(self) -> None:
        """
        进化主循环
        """
        self.logger.info("evolution_loop_started")

        while self._is_running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次

                self._iterations_completed += 1

                # 更新进化阶段
                await self._update_evolution_stage()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("evolution_loop_error", error=str(e))

        self.logger.info("evolution_loop_stopped")

    async def _update_evolution_stage(self) -> None:
        """
        更新进化阶段
        """
        pattern_stats = await self._knowledge_learning.get_pattern_statistics()
        total_patterns = pattern_stats["total_patterns"]

        if total_patterns < 10:
            new_stage = EvolutionStage.LEARNING
        elif total_patterns < 50:
            new_stage = EvolutionStage.OPTIMIZING
        elif total_patterns < 200:
            new_stage = EvolutionStage.MATURING
        else:
            new_stage = EvolutionStage.STABLE

        if new_stage != self._stage:
            self.logger.info(
                "evolution_stage_changed",
                from_stage=self._stage,
                to_stage=new_stage,
            )
            self._stage = new_stage

    async def _get_evolution_metrics(self) -> EvolutionMetrics:
        """
        获取进化指标

        Returns:
            进化指标
        """
        uptime_seconds = 0.0
        if self._start_time:
            uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()

        # 计算平均性能改进（简化）
        avg_improvement = 0.0
        if self._total_optimizations > 0:
            avg_improvement = min(20.0, self._total_optimizations * 0.5)  # 假设每次优化0.5%

        return EvolutionMetrics(
            stage=self._stage,
            iterations_completed=self._iterations_completed,
            total_optimizations=self._total_optimizations,
            patterns_learned=len(self._knowledge_learning._kb.patterns),
            memory_optimized_bytes=self._memory_optimized_bytes,
            avg_performance_improvement=avg_improvement,
            uptime_seconds=uptime_seconds,
        )

    @property
    def stage(self) -> EvolutionStage:
        """
        当前进化阶段
        """
        return self._stage

    @property
    def is_running(self) -> bool:
        """
        是否正在运行
        """
        return self._is_running

    @property
    def memory_cleanup(self) -> MemoryCleanupServiceProvider:
        """
        内存清理服务
        """
        return self._memory_cleanup

    @property
    def strategy_optimization(self) -> StrategyOptimizationServiceProvider:
        """
        策略优化服务
        """
        return self._strategy_optimization

    @property
    def knowledge_learning(self) -> KnowledgeLearningServiceProvider:
        """
        知识学习服务
        """
        return self._knowledge_learning
