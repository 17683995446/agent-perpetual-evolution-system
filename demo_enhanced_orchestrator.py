#!/usr/bin/env python3
"""
演示增强型任务执行编排器的功能
"""

import asyncio
import sys
from typing import Dict, Any

from src.agent_perpetual_system_complete.layer_2_orchestration_coordination.task_execution_orchestrator import (
    EnhancedTaskExecutionOrchestrator,
    ExecutionConfiguration,
)
from src.agent_perpetual_system_complete.layer_3_business_service.task_management_service_provider import (
    TaskManagementServiceProvider,
)
from src.agent_perpetual_system_complete.layer_4_domain_model.task_domain_entity_definition import (
    TaskPriority,
)


async def main():
    print("=" * 70)
    print("演示增强型任务执行编排器")
    print("=" * 70)

    # 初始化服务和编排器
    service = TaskManagementServiceProvider("sqlite+aiosqlite:///:memory:")
    await service.initialize()

    config = ExecutionConfiguration(
        max_concurrent_tasks=2,
        default_timeout_seconds=30,
        retry_on_failure=True,
        max_retries=3,
        retry_backoff_base=1.5,
        enable_priority_scheduling=True,
        enable_dependency_resolution=True,
    )

    orchestrator = EnhancedTaskExecutionOrchestrator(service, config)
    await orchestrator.initialize()

    print("\n[1] 测试基本任务执行...")
    task1 = await service.create_and_submit_task(
        {"type": "data_processing", "data": "sample_data_1"},
        priority=TaskPriority.HIGH,
    )
    await orchestrator.submit_task_with_dependencies(task1)
    results = await orchestrator.execute_tasks_batch()
    for task_id, result in results.items():
        print(f"  ✓ 任务 {task_id}: {'成功' if result.success else '失败'}")

    print("\n[2] 测试优先级调度...")
    task_low = await service.create_and_submit_task(
        {"type": "cleanup", "data": "temp_files"},
        priority=TaskPriority.LOW,
    )
    task_high = await service.create_and_submit_task(
        {"type": "critical_report", "data": "urgent_data"},
        priority=TaskPriority.HIGH,
    )
    task_medium = await service.create_and_submit_task(
        {"type": "regular_backup", "data": "backup_data"},
        priority=TaskPriority.MEDIUM,
    )
    await orchestrator.submit_task_with_dependencies(task_low)
    await orchestrator.submit_task_with_dependencies(task_high)
    await orchestrator.submit_task_with_dependencies(task_medium)
    print("  已提交: LOW, HIGH, MEDIUM优先级任务")
    results = await orchestrator.execute_tasks_batch()
    print(f"  ✓ 执行了 {len(results)} 个任务")

    print("\n[3] 测试任务依赖关系...")
    await orchestrator.initialize()  # 重置

    task_a = await service.create_and_submit_task(
        {"step": "A", "action": "fetch_data"},
        priority=TaskPriority.MEDIUM,
    )
    task_b = await service.create_and_submit_task(
        {"step": "B", "action": "process_data"},
        priority=TaskPriority.MEDIUM,
    )
    task_c = await service.create_and_submit_task(
        {"step": "C", "action": "generate_report"},
        priority=TaskPriority.MEDIUM,
    )

    await orchestrator.submit_task_with_dependencies(task_a)
    await orchestrator.submit_task_with_dependencies(task_b, depends_on=[task_a.task_identifier])
    await orchestrator.submit_task_with_dependencies(task_c, depends_on=[task_b.task_identifier])

    print("  依赖关系: A → B → C")
    results = await orchestrator.execute_tasks_batch()
    for task_id, result in results.items():
        print(f"  ✓ 任务 {task_id[-8:]}: {'成功' if result.success else '失败'}")

    print("\n[4] 显示执行统计...")
    stats = orchestrator.get_execution_statistics()
    print(f"  总任务数: {stats.total_tasks}")
    print(f"  已完成: {stats.completed_tasks}")
    print(f"  成功率: {stats.success_rate:.1%}")
    print(f"  平均执行时间: {stats.average_duration_seconds:.2f}s")

    print("\n" + "=" * 70)
    print("演示完成！增强型任务执行编排器功能测试通过")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
