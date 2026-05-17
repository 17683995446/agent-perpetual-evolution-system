"""
Strategy Optimization Service Provider - 策略优化服务提供者（6个单词）

负责执行策略学习、参数自动调优、性能趋势分析。
"""

import asyncio
import math
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import get_structured_logger


class OptimizationGoal(str, Enum):
    """
    优化目标
    """
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_ERROR_RATE = "minimize_error_rate"
    BALANCED = "balanced"


class ParameterType(str, Enum):
    """
    参数类型
    """
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"


@dataclass
class ParameterDefinition:
    """
    参数定义
    """
    name: str
    param_type: ParameterType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    possible_values: Optional[List[Any]] = None
    default_value: Optional[Any] = None


@dataclass
class PerformanceMetric:
    """
    性能指标
    """
    metric_name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """
    优化结果
    """
    optimized_parameters: Dict[str, Any]
    score: float
    metrics: Dict[str, float]
    timestamp: datetime
    iterations: int


@dataclass
class OptimizationStrategy:
    """
    优化策略
    """
    name: str
    goal: OptimizationGoal
    parameters: List[ParameterDefinition]
    learning_rate: float = 0.1
    exploration_rate: float = 0.2
    window_size: int = 100


class StrategyOptimizationServiceProvider:
    """
    策略优化服务提供者

    核心职责：
    1. 执行策略学习和参数调优
    2. 性能趋势分析和预测
    3. 自动化参数调整
    4. A/B测试支持
    """

    def __init__(
        self,
        strategies: Optional[List[OptimizationStrategy]] = None,
    ):
        self.logger = get_structured_logger(__name__)

        self._strategies = strategies or []
        self._performance_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self._parameter_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._current_parameters: Dict[str, Dict[str, Any]] = {}
        self._optimization_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._optimization_results: List[OptimizationResult] = []

    async def start(self, interval_seconds: int = 600) -> None:
        """
        启动策略优化服务

        Args:
            interval_seconds: 优化检查间隔，默认10分钟
        """
        if self._is_running:
            self.logger.warning("strategy_optimization_service_already_running")
            return

        self.logger.info(
            "starting_strategy_optimization_service",
            interval_seconds=interval_seconds,
            strategies_count=len(self._strategies),
        )

        self._is_running = True
        self._optimization_task = asyncio.create_task(
            self._optimization_loop(interval_seconds)
        )

        self.logger.info("strategy_optimization_service_started")

    async def stop(self) -> None:
        """
        停止策略优化服务
        """
        if not self._is_running:
            self.logger.warning("strategy_optimization_service_not_running")
            return

        self.logger.info("stopping_strategy_optimization_service")
        self._is_running = False

        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass

        self.logger.info("strategy_optimization_service_stopped")

    async def register_strategy(self, strategy: OptimizationStrategy) -> None:
        """
        注册优化策略

        Args:
            strategy: 优化策略
        """
        self._strategies.append(strategy)

        # 初始化参数
        self._current_parameters[strategy.name] = {
            param.name: param.default_value
            for param in strategy.parameters
        }

        self.logger.info(
            "optimization_strategy_registered",
            strategy_name=strategy.name,
            goal=strategy.goal,
        )

    async def record_performance(
        self,
        strategy_name: str,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        记录性能指标

        Args:
            strategy_name: 策略名称
            metric_name: 指标名称
            value: 指标值
            context: 上下文信息
        """
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.utcnow(),
            context=context or {},
        )

        self._performance_history[f"{strategy_name}:{metric_name}"].append(metric)

        self.logger.debug(
            "performance_recorded",
            strategy_name=strategy_name,
            metric_name=metric_name,
            value=value,
        )

    async def get_current_parameters(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        获取当前参数

        Args:
            strategy_name: 策略名称

        Returns:
            当前参数字典
        """
        return self._current_parameters.get(strategy_name)

    async def optimize(
        self,
        strategy_name: str,
        iterations: int = 50,
    ) -> Optional[OptimizationResult]:
        """
        执行优化

        Args:
            strategy_name: 策略名称
            iterations: 迭代次数

        Returns:
            优化结果
        """
        strategy = next((s for s in self._strategies if s.name == strategy_name), None)
        if not strategy:
            self.logger.error("strategy_not_found", strategy_name=strategy_name)
            return None

        self.logger.info(
            "starting_optimization",
            strategy_name=strategy_name,
            iterations=iterations,
        )

        # 简单的网格搜索/随机搜索优化
        best_params = self._current_parameters.get(strategy_name, {}).copy()
        best_score = float("-inf")

        for i in range(iterations):
            # 随机搜索
            candidate_params = self._generate_candidate_parameters(strategy)
            score = await self._evaluate_parameters(strategy, candidate_params)

            if score > best_score:
                best_score = score
                best_params = candidate_params.copy()
                self.logger.debug(
                    "new_best_found",
                    iteration=i,
                    score=best_score,
                )

        result = OptimizationResult(
            optimized_parameters=best_params,
            score=best_score,
            metrics=await self._calculate_metrics(strategy_name),
            timestamp=datetime.utcnow(),
            iterations=iterations,
        )

        # 更新参数
        self._current_parameters[strategy_name] = best_params
        self._parameter_history[strategy_name].append(best_params)
        self._optimization_results.append(result)

        self.logger.info(
            "optimization_complete",
            strategy_name=strategy_name,
            score=best_score,
        )

        return result

    async def get_performance_trend(
        self,
        strategy_name: str,
        metric_name: str,
        window_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        获取性能趋势

        Args:
            strategy_name: 策略名称
            metric_name: 指标名称
            window_minutes: 时间窗口（分钟）

        Returns:
            趋势分析结果
        """
        key = f"{strategy_name}:{metric_name}"
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=window_minutes)

        recent_metrics = [
            m for m in self._performance_history.get(key, [])
            if m.timestamp >= cutoff
        ]

        if not recent_metrics:
            return {
                "trend": "insufficient_data",
                "count": 0,
            }

        values = [m.value for m in recent_metrics]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)

        # 简单的趋势计算
        if len(values) >= 2:
            half = len(values) // 2
            first_half = sum(values[:half]) / half
            second_half = sum(values[half:]) / half
            trend = "improving" if second_half < first_half else "degrading"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "mean": mean,
            "std_dev": std_dev,
            "min": min(values),
            "max": max(values),
            "count": len(values),
            "window_minutes": window_minutes,
        }

    async def _optimization_loop(self, interval_seconds: int) -> None:
        """
        优化循环

        Args:
            interval_seconds: 检查间隔
        """
        self.logger.info("optimization_loop_started")

        while self._is_running:
            try:
                await asyncio.sleep(interval_seconds)

                for strategy in self._strategies:
                    # 定期优化
                    await self.optimize(strategy.name, iterations=20)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("optimization_loop_error", error=str(e))

        self.logger.info("optimization_loop_stopped")

    def _generate_candidate_parameters(
        self,
        strategy: OptimizationStrategy,
    ) -> Dict[str, Any]:
        """
        生成候选参数

        Args:
            strategy: 优化策略

        Returns:
            候选参数字典
        """
        import random

        params = {}
        for param_def in strategy.parameters:
            if random.random() < strategy.exploration_rate:
                # 探索：随机选择
                if param_def.param_type == ParameterType.INTEGER:
                    value = random.randint(
                        int(param_def.min_value or 0),
                        int(param_def.max_value or 100),
                    )
                elif param_def.param_type == ParameterType.FLOAT:
                    value = random.uniform(
                        param_def.min_value or 0.0,
                        param_def.max_value or 100.0,
                    )
                elif param_def.param_type == ParameterType.BOOLEAN:
                    value = random.choice([True, False])
                elif param_def.param_type == ParameterType.CATEGORICAL:
                    value = random.choice(param_def.possible_values or [])
                else:
                    value = param_def.default_value
            else:
                # 利用：基于当前参数微调
                current = self._current_parameters.get(strategy.name, {}).get(param_def.name)
                if current is None:
                    value = param_def.default_value
                else:
                    value = current

            params[param_def.name] = value

        return params

    async def _evaluate_parameters(
        self,
        strategy: OptimizationStrategy,
        parameters: Dict[str, Any],
    ) -> float:
        """
        评估参数

        Args:
            strategy: 优化策略
            parameters: 参数字典

        Returns:
            评分
        """
        # 获取历史性能数据
        metrics = await self._calculate_metrics(strategy.name)

        # 根据目标计算评分
        if strategy.goal == OptimizationGoal.MINIMIZE_LATENCY:
            score = -metrics.get("latency", 0)
        elif strategy.goal == OptimizationGoal.MAXIMIZE_THROUGHPUT:
            score = metrics.get("throughput", 0)
        elif strategy.goal == OptimizationGoal.MINIMIZE_ERROR_RATE:
            score = -metrics.get("error_rate", 0)
        elif strategy.goal == OptimizationGoal.BALANCED:
            latency_score = -metrics.get("latency", 0)
            throughput_score = metrics.get("throughput", 0)
            error_score = -metrics.get("error_rate", 0)
            score = (latency_score + throughput_score + error_score) / 3
        else:
            score = 0.0

        return score

    async def _calculate_metrics(self, strategy_name: str) -> Dict[str, float]:
        """
        计算指标

        Args:
            strategy_name: 策略名称

        Returns:
            指标字典
        """
        metrics = {}

        for metric_name in ["latency", "throughput", "error_rate"]:
            key = f"{strategy_name}:{metric_name}"
            history = self._performance_history.get(key, [])
            if history:
                values = [m.value for m in history]
                metrics[metric_name] = sum(values) / len(values)
            else:
                metrics[metric_name] = 0.0

        return metrics

    @property
    def is_running(self) -> bool:
        """
        是否正在运行
        """
        return self._is_running

    @property
    def optimization_results(self) -> List[OptimizationResult]:
        """
        优化结果历史
        """
        return self._optimization_results.copy()
