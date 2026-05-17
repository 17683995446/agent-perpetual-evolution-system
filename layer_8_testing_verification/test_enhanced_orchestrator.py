"""
Test Enhanced Orchestrator - 测试增强型编排器（5个单词）

测试增强型任务执行编排器的完整功能。
"""

import asyncio
import pytest
from typing import Dict, Any
from datetime import datetime

from src.agent_perpetual_system_complete.layer_2_orchestration_coordination.task_execution_orchestrator import (
    EnhancedTaskExecutionOrchestrator,
    ExecutionConfiguration,
    TaskExecutionContext,
    ExecutionStatistics,
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
from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)

logger = get_structured_logger(__name__)


@pytest.mark.asyncio
async def test_basic_task_execution():
    """
    测试基本的任务执行
    """
    logger.info("test_basic_task_execution_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=2,
        default_timeout_seconds=10,
        retry_on_failure=False,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    task1 = await service.create_and_submit_task(
        {"type": "test", "data": "task1"},
        priority=TaskPriority.HIGH,
    )

    await orchestrator.submit_task_with_dependencies(task1)

    results = await orchestrator.execute_tasks_batch()

    assert len(results) == 1
    assert results[task1.task_identifier].success

    stats = orchestrator.get_execution_statistics()
    assert stats.total_tasks == 1
    assert stats.completed_tasks == 1
    assert stats.success_rate == 1.0

    logger.info("test_basic_task_execution_completed", stats=stats.__dict__)


@pytest.mark.asyncio
async def test_priority_scheduling():
    """
    测试优先级调度
    """
    logger.info("test_priority_scheduling_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=1,
        default_timeout_seconds=10,
        retry_on_failure=False,
        enable_priority_scheduling=True,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    execution_order = []

    async def test_executor(content: Dict[str, Any]) -> Dict[str, Any]:
        execution_order.append(content["data"])
        return {"status": "success", "data": content["data"]}

    task_low = await service.create_and_submit_task(
        {"type": "test", "data": "low"},
        priority=TaskPriority.LOW,
    )
    task_high = await service.create_and_submit_task(
        {"type": "test", "data": "high"},
        priority=TaskPriority.HIGH,
    )
    task_medium = await service.create_and_submit_task(
        {"type": "test", "data": "medium"},
        priority=TaskPriority.MEDIUM,
    )

    await orchestrator.submit_task_with_dependencies(task_low)
    await orchestrator.submit_task_with_dependencies(task_high)
    await orchestrator.submit_task_with_dependencies(task_medium)

    results = await orchestrator.execute_tasks_batch(executor_fn=test_executor)

    assert len(results) == 3
    assert all(r.success for r in results.values())

    logger.info("test_priority_scheduling_completed", execution_order=execution_order)


@pytest.mark.asyncio
async def test_task_dependencies():
    """
    测试任务依赖
    """
    logger.info("test_task_dependencies_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=5,
        default_timeout_seconds=10,
        retry_on_failure=False,
        enable_dependency_resolution=True,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    execution_order = []

    async def test_executor(content: Dict[str, Any]) -> Dict[str, Any]:
        execution_order.append(content["data"])
        return {"status": "success", "data": content["data"]}

    task_a = await service.create_and_submit_task(
        {"type": "test", "data": "A"},
        priority=TaskPriority.MEDIUM,
    )
    task_b = await service.create_and_submit_task(
        {"type": "test", "data": "B"},
        priority=TaskPriority.MEDIUM,
    )
    task_c = await service.create_and_submit_task(
        {"type": "test", "data": "C"},
        priority=TaskPriority.MEDIUM,
    )

    await orchestrator.submit_task_with_dependencies(task_a)
    await orchestrator.submit_task_with_dependencies(task_b, depends_on=[task_a.task_identifier])
    await orchestrator.submit_task_with_dependencies(task_c, depends_on=[task_b.task_identifier])

    results = await orchestrator.execute_tasks_batch(executor_fn=test_executor)

    assert len(results) == 3
    assert all(r.success for r in results.values())
    assert execution_order == ["A", "B", "C"]

    logger.info("test_task_dependencies_completed", execution_order=execution_order)


@pytest.mark.asyncio
async def test_retry_mechanism():
    """
    测试重试机制
    """
    logger.info("test_retry_mechanism_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=2,
        default_timeout_seconds=10,
        retry_on_failure=True,
        max_retries=2,
        retry_backoff_base=1.1,
        retry_backoff_max=5.0,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    fail_count = 0

    async def flaky_executor(content: Dict[str, Any]) -> Dict[str, Any]:
        nonlocal fail_count
        fail_count += 1
        if fail_count < 2:
            raise Exception("Simulated failure")
        return {"status": "success", "attempts": fail_count}

    task = await service.create_and_submit_task(
        {"type": "test", "data": "retry_test"},
        priority=TaskPriority.HIGH,
    )

    await orchestrator.submit_task_with_dependencies(task)
    results = await orchestrator.execute_tasks_batch(executor_fn=flaky_executor)

    assert len(results) == 1
    assert results[task.task_identifier].success

    stats = orchestrator.get_execution_statistics()
    assert stats.retried_tasks == 1

    logger.info("test_retry_mechanism_completed", stats=stats.__dict__, fail_count=fail_count)


@pytest.mark.asyncio
async def test_timeout_handling():
    """
    测试超时处理
    """
    logger.info("test_timeout_handling_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=2,
        default_timeout_seconds=1,
        retry_on_failure=False,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    async def slow_executor(content: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(5)
        return {"status": "success"}

    task = await service.create_and_submit_task(
        {"type": "test", "data": "timeout_test"},
        priority=TaskPriority.MEDIUM,
        timeout_seconds=1,
    )

    await orchestrator.submit_task_with_dependencies(task)
    results = await orchestrator.execute_tasks_batch()

    assert len(results) == 1
    assert not results[task.task_identifier].success
    assert "timed out" in results[task.task_identifier].error_message

    stats = orchestrator.get_execution_statistics()
    assert stats.timeout_tasks == 1

    logger.info("test_timeout_handling_completed", stats=stats.__dict__)


@pytest.mark.asyncio
async def test_concurrent_execution():
    """
    测试并发执行
    """
    logger.info("test_concurrent_execution_started")

    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=3,
        default_timeout_seconds=10,
        retry_on_failure=False,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    start_times = {}
    end_times = {}

    async def tracked_executor(content: Dict[str, Any]) -> Dict[str, Any]:
        task_id = content["data"]
        start_times[task_id] = datetime.utcnow()
        await asyncio.sleep(0.2)
        end_times[task_id] = datetime.utcnow()
        return {"status": "success"}

    tasks = []
    for i in range(5):
        task = await service.create_and_submit_task(
            {"type": "test", "data": f"task_{i}"},
            priority=TaskPriority.MEDIUM,
        )
        tasks.append(task)
        await orchestrator.submit_task_with_dependencies(task)

    results = await orchestrator.execute_tasks_batch()

    assert len(results) == 5
    assert all(r.success for r in results.values())

    stats = orchestrator.get_execution_statistics()
    logger.info("test_concurrent_execution_completed", stats=stats.__dict__)


if __name__ == "__main__":
    asyncio.run(test_basic_task_execution())
    asyncio.run(test_priority_scheduling())
    asyncio.run(test_task_dependencies())
    asyncio.run(test_retry_mechanism())
    asyncio.run(test_timeout_handling())
    asyncio.run(test_concurrent_execution())
    print("All tests passed!")
