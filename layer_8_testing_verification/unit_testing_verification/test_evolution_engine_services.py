"""
Test Evolution Engine Services - 测试进化引擎服务（6个单词）

测试内存清理、策略优化、知识学习等进化引擎模块。
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from src.agent_perpetual_system_complete.layer_3_business_service.memory_cleanup_service_provider import (
    MemoryCleanupServiceProvider,
    DataTemperature,
    CleanupPolicy,
    MemoryUsageStats,
    CleanupAction,
)
from src.agent_perpetual_system_complete.layer_3_business_service.strategy_optimization_service_provider import (
    StrategyOptimizationServiceProvider,
    OptimizationStrategy,
    ParameterDefinition,
    ParameterType,
    OptimizationGoal,
)
from src.agent_perpetual_system_complete.layer_3_business_service.knowledge_learning_service_provider import (
    KnowledgeLearningServiceProvider,
    OutcomeCategory,
    PatternType,
)
from src.agent_perpetual_system_complete.layer_3_business_service.evolution_engine_controller import (
    EvolutionEngineController,
    EvolutionStage,
)


class TestMemoryCleanupService:
    """
    内存清理服务测试
    """

    @pytest_asyncio.fixture
    async def service(self):
        """测试夹具：内存清理服务"""
        service = MemoryCleanupServiceProvider(max_memory_bytes=10 * 1024 * 1024)  # 10MB
        yield service

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        assert service._max_memory_bytes == 10 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_store_and_retrieve_data(self, service):
        """测试数据存储和检索"""
        await service.store_data("test_key", {"value": "test_data"})

        result = await service.retrieve_data("test_key")
        assert result is not None
        assert result["value"] == "test_data"

    @pytest.mark.asyncio
    async def test_memory_stats(self, service):
        """测试内存统计"""
        await service.store_data("key1", "data1")
        await service.store_data("key2", "data2")

        stats = await service.get_memory_stats()
        assert stats.used_bytes > 0
        assert stats.used_percent > 0

    @pytest.mark.asyncio
    async def test_temperature_promotion(self, service):
        """测试温度提升"""
        await service.store_data("test_key", "test_data")

        # 检索数据，应该提升到热数据
        await service.retrieve_data("test_key")

        entry = service._data_store.get("test_key")
        assert entry is not None
        assert entry.temperature == DataTemperature.HOT

    @pytest.mark.asyncio
    async def test_force_cleanup(self, service):
        """测试强制清理"""
        await service.store_data("key1", "data1")
        await service.store_data("key2", "data2")

        # 将数据标记为冻结
        for key in service._data_store:
            service._data_store[key].temperature = DataTemperature.FROZEN

        result = await service.force_cleanup()
        assert result["entries_removed"] > 0


class TestStrategyOptimizationService:
    """
    策略优化服务测试
    """

    @pytest_asyncio.fixture
    async def service(self):
        """测试夹具：策略优化服务"""
        service = StrategyOptimizationServiceProvider()
        yield service

    @pytest_asyncio.fixture
    async def test_strategy(self):
        """测试夹具：测试策略"""
        return OptimizationStrategy(
            name="test_strategy",
            goal=OptimizationGoal.BALANCED,
            parameters=[
                ParameterDefinition(
                    name="param1",
                    param_type=ParameterType.INTEGER,
                    min_value=1,
                    max_value=10,
                    default_value=5,
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None

    @pytest.mark.asyncio
    async def test_register_strategy(self, service, test_strategy):
        """测试策略注册"""
        await service.register_strategy(test_strategy)

        assert len(service._strategies) == 1
        assert test_strategy.name in service._current_parameters

    @pytest.mark.asyncio
    async def test_record_performance(self, service, test_strategy):
        """测试记录性能"""
        await service.register_strategy(test_strategy)

        await service.record_performance(
            strategy_name="test_strategy",
            metric_name="latency",
            value=100.0,
        )

        key = "test_strategy:latency"
        assert key in service._performance_history

    @pytest.mark.asyncio
    async def test_get_current_parameters(self, service, test_strategy):
        """测试获取当前参数"""
        await service.register_strategy(test_strategy)

        params = await service.get_current_parameters("test_strategy")
        assert params is not None
        assert "param1" in params

    @pytest.mark.asyncio
    async def test_performance_trend(self, service, test_strategy):
        """测试性能趋势"""
        await service.register_strategy(test_strategy)

        # 记录一些性能数据
        for i in range(10):
            await service.record_performance(
                strategy_name="test_strategy",
                metric_name="latency",
                value=100.0 - i * 5,
            )

        trend = await service.get_performance_trend(
            strategy_name="test_strategy",
            metric_name="latency",
            window_minutes=60,
        )

        assert "trend" in trend
        assert "mean" in trend


class TestKnowledgeLearningService:
    """
    知识学习服务测试
    """

    @pytest_asyncio.fixture
    async def service(self):
        """测试夹具：知识学习服务"""
        service = KnowledgeLearningServiceProvider()
        yield service

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None

    @pytest.mark.asyncio
    async def test_record_case(self, service):
        """测试记录案例"""
        case_id = await service.record_case(
            input_data={"param1": "value1"},
            output_data={"result": "success"},
            outcome=OutcomeCategory.SUCCESS,
            metadata={"latency": 100},
        )

        assert case_id is not None
        assert len(case_id) > 0

    @pytest.mark.asyncio
    async def test_get_recommendations(self, service):
        """测试获取建议"""
        # 先记录一些案例
        for i in range(10):
            await service.record_case(
                input_data={"param": "value"},
                output_data={"result": "ok"},
                outcome=OutcomeCategory.SUCCESS,
            )

        # 处理缓冲区
        await service._process_buffer()

        # 获取建议
        recommendations = await service.get_recommendations(
            input_data={"param": "value"},
            top_k=5,
        )

        # 可能返回空或有内容，取决于学习过程
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_pattern_statistics(self, service):
        """测试模式统计"""
        # 记录一些案例
        for i in range(5):
            await service.record_case(
                input_data={"test": "data"},
                output_data={"result": "ok"},
                outcome=OutcomeCategory.SUCCESS,
            )

        await service._process_buffer()

        stats = await service.get_pattern_statistics()

        assert "total_patterns" in stats
        assert "total_case_studies" in stats


class TestEvolutionEngineController:
    """
    进化引擎控制器测试
    """

    @pytest_asyncio.fixture
    async def controller(self):
        """测试夹具：进化引擎控制器"""
        controller = EvolutionEngineController()
        yield controller

    @pytest.mark.asyncio
    async def test_controller_initialization(self, controller):
        """测试控制器初始化"""
        assert controller is not None
        assert controller._stage == EvolutionStage.INITIALIZING

    @pytest.mark.asyncio
    async def test_record_execution(self, controller):
        """测试记录执行"""
        case_id = await controller.record_execution(
            input_data={"param": "value"},
            output_data={"result": "success"},
            success=True,
            metadata={"latency": 100},
        )

        assert case_id is not None

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, controller):
        """测试获取仪表盘数据"""
        dashboard_data = await controller.get_dashboard_data()

        assert "timestamp" in dashboard_data
        assert "stage" in dashboard_data
        assert "memory" in dashboard_data
        assert "patterns" in dashboard_data
        assert "evolution" in dashboard_data

    @pytest.mark.asyncio
    async def test_get_recommendations(self, controller):
        """测试获取建议"""
        # 记录一些执行
        await controller.record_execution(
            input_data={"test": "data"},
            output_data={"result": "ok"},
            success=True,
        )

        recommendations = await controller.get_recommendations(
            input_data={"test": "data"},
            top_k=5,
        )

        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_force_memory_cleanup(self, controller):
        """测试强制内存清理"""
        # 先存储一些数据
        await controller._memory_cleanup.store_data("key1", "data1")
        await controller._memory_cleanup.store_data("key2", "data2")

        result = await controller.force_memory_cleanup()

        assert isinstance(result, dict)
