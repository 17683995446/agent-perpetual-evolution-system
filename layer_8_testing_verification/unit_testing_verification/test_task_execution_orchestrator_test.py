"""
Test Task Execution Orchestrator - 测试任务执行编排器（7个单词）

测试任务执行编排器的功能，包括并发执行、依赖解析和优先级调度。
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from src.agent_perpetual_system_complete.layer_2_orchestration_coordination.task_execution_orchestrator import (
    TaskExecutionOrchestrator,
    TaskExecutionContext,
    ExecutionStatistics,
    ExecutionConfiguration,
    TaskDependencyType,
)
from src.agent_perpetual_system_complete.layer_3_business_service.task_management_service_provider import (
    TaskManagementServiceProvider,
    TaskExecutionResult,
)
from src.agent_perpetual_system_complete.layer_4_domain_model.task_domain_entity_definition import (
    TaskDomainEntity,
    TaskStatus,
    TaskPriority,
)


@pytest_asyncio.fixture
async def task_service():
    """
    测试夹具：创建任务管理服务
    """
    service = TaskManagementServiceProvider(db_url="sqlite+aiosqlite:///:memory:")
    await service.initialize()
    yield service


@pytest_asyncio.fixture
async def orchestrator(task_service):
    """
    测试夹具：创建任务执行编排器
    """
    config = ExecutionConfiguration(
        max_concurrent_tasks=5,
        default_timeout_seconds=60,
        enable_priority_scheduling=True,
        enable_dependency_resolution=True,
    )
    orch = TaskExecutionOrchestrator(task_service, config)
    await orch.initialize()
    yield orch


class TestExecutionConfigurationTest:
    """
    执行配置测试
    """

    def test_default_configuration(self) -> None:
        """
        测试默认配置
        """
        config = ExecutionConfiguration()

        assert config.max_concurrent_tasks == 10
        assert config.default_timeout_seconds == 300
        assert config.retry_on_failure is True
        assert config.max_retries == 3

    def test_custom_configuration(self) -> None:
        """
        测试自定义配置
        """
        config = ExecutionConfiguration(
            max_concurrent_tasks=20,
            enable_priority_scheduling=False,
        )

        assert config.max_concurrent_tasks == 20
        assert config.enable_priority_scheduling is False


class TestTaskExecutionContextTest:
    """
    任务执行上下文测试
    """

    def test_context_creation(self) -> None:
        """
        测试上下文创建
        """
        task = TaskDomainEntity(
            task_identifier="test_task_001",
            task_content={"type": "test"},
        )

        ctx = TaskExecutionContext(task=task)

        assert ctx.task.task_identifier == "test_task_001"
        assert ctx.started_at is None
        assert ctx.completed_at is None
        assert ctx.result is None
        assert ctx.dependencies_satisfied is False
        assert ctx.is_blocked is False

    def test_context_with_result(self) -> None:
        """
        测试带结果的上下文
        """
        task = TaskDomainEntity(
            task_identifier="test_task_001",
            task_content={"type": "test"},
        )

        result = TaskExecutionResult(
            success=True,
            result={"output": "test_output"},
            error_message=None,
            execution_duration_seconds=1.5,
            task_identifier="test_task_001",
        )

        ctx = TaskExecutionContext(
            task=task,
            result=result,
            dependencies_satisfied=True,
        )

        assert ctx.result.success is True
        assert ctx.result.execution_duration_seconds == 1.5
        assert ctx.dependencies_satisfied is True


@pytest.mark.asyncio
class TestTaskExecutionOrchestratorTest:
    """
    任务执行编排器测试
    """

    async def test_orchestrator_initialization(self, orchestrator) -> None:
        """
        测试编排器初始化
        """
        assert orchestrator is not None
        assert orchestrator._task_semaphore is not None
        assert orchestrator._is_shutting_down is False

    async def test_submit_task_without_dependencies(self, orchestrator, task_service) -> None:
        """
        测试提交无依赖的任务
        """
        task = await task_service.create_and_submit_task(
            task_content={"type": "test", "data": "test_data"},
            priority=TaskPriority.HIGH,
        )

        task_id = await orchestrator.submit_task_with_dependencies(task)

        assert task_id == task.task_identifier
        assert task_id in orchestrator._execution_contexts

    async def test_submit_task_with_dependencies(self, orchestrator, task_service) -> None:
        """
        测试提交带依赖的任务
        """
        task1 = await task_service.create_and_submit_task(
            task_content={"type": "test1"},
            priority=TaskPriority.MEDIUM,
        )

        task2 = await task_service.create_and_submit_task(
            task_content={"type": "test2"},
            priority=TaskPriority.HIGH,
        )

        task1_id = await orchestrator.submit_task_with_dependencies(task1)
        task2_id = await orchestrator.submit_task_with_dependencies(
            task2,
            depends_on=[task1_id],
        )

        assert task1_id in orchestrator._execution_contexts
        assert task2_id in orchestrator._execution_contexts
        assert task2_id in orchestrator._task_dependencies
        assert task1_id in orchestrator._task_dependencies[task2_id]

    async def test_check_dependencies_satisfied(self, orchestrator, task_service) -> None:
        """
        测试依赖满足检查
        """
        task1 = await task_service.create_and_submit_task(
            task_content={"type": "test1"},
        )
        task2 = await task_service.create_and_submit_task(
            task_content={"type": "test2"},
        )

        await orchestrator.submit_task_with_dependencies(task1)
        await orchestrator.submit_task_with_dependencies(
            task2,
            depends_on=[task1.task_identifier],
        )

        assert orchestrator._check_dependencies_satisfied(task1.task_identifier) is True
        assert orchestrator._check_dependencies_satisfied(task2.task_identifier) is False

    async def test_execution_statistics(self, orchestrator) -> None:
        """
        测试执行统计信息
        """
        stats = orchestrator.get_execution_statistics()

        assert isinstance(stats, ExecutionStatistics)
        assert stats.total_tasks == 0
        assert stats.completed_tasks == 0
        assert stats.running_tasks == 0


@pytest.mark.asyncio
class TestDependencyResolutionTest:
    """
    依赖解析测试
    """

    async def test_complex_dependency_chain(self, orchestrator, task_service) -> None:
        """
        测试复杂的依赖链
        """
        task_a = await task_service.create_and_submit_task(
            task_content={"type": "A"},
            priority=TaskPriority.HIGHEST,
        )

        task_b = await task_service.create_and_submit_task(
            task_content={"type": "B"},
            priority=TaskPriority.HIGH,
        )

        task_c = await task_service.create_and_submit_task(
            task_content={"type": "C"},
            priority=TaskPriority.MEDIUM,
        )

        await orchestrator.submit_task_with_dependencies(task_a)
        await orchestrator.submit_task_with_dependencies(
            task_b,
            depends_on=[task_a.task_identifier],
        )
        await orchestrator.submit_task_with_dependencies(
            task_c,
            depends_on=[task_b.task_identifier],
        )

        assert orchestrator._check_dependencies_satisfied(task_a.task_identifier) is True
        assert orchestrator._check_dependencies_satisfied(task_b.task_identifier) is False
        assert orchestrator._check_dependencies_satisfied(task_c.task_identifier) is False

    async def test_parallel_dependencies(self, orchestrator, task_service) -> None:
        """
        测试并行依赖
        """
        task_a = await task_service.create_and_submit_task(task_content={"type": "A"})
        task_b = await task_service.create_and_submit_task(task_content={"type": "B"})
        task_c = await task_service.create_and_submit_task(task_content={"type": "C"})

        await orchestrator.submit_task_with_dependencies(task_a)
        await orchestrator.submit_task_with_dependencies(task_b)
        await orchestrator.submit_task_with_dependencies(
            task_c,
            depends_on=[task_a.task_identifier, task_b.task_identifier],
        )

        assert orchestrator._check_dependencies_satisfied(task_a.task_identifier) is True
        assert orchestrator._check_dependencies_satisfied(task_b.task_identifier) is True
        assert orchestrator._check_dependencies_satisfied(task_c.task_identifier) is False
