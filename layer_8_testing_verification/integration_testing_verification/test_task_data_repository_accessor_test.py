"""
Test Task Data Repository Accessor - 测试任务数据仓储访问器（7个单词）

任务数据仓储的集成测试，使用内存 SQLite 数据库。
"""

import pytest
import pytest_asyncio
from typing import Optional, Dict, Any

from src.agent_perpetual_system_complete.layer_5_data_access.task_data_repository_accessor import (
    TaskDataRepositoryAccessor,
)
from src.agent_perpetual_system_complete.layer_4_domain_model.task_domain_entity_definition import (
    TaskStatus,
    TaskPriority,
)


@pytest_asyncio.fixture
async def repository_accessor():
    """
    测试夹具：创建任务数据仓储访问器，使用内存数据库
    """
    accessor = TaskDataRepositoryAccessor(db_url="sqlite+aiosqlite:///:memory:")
    await accessor.initialize_database()
    yield accessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestTaskDataRepositoryIntegrationTest:
    """
    任务数据仓储集成测试
    """
    
    async def test_create_and_retrieve_task(self, repository_accessor) -> None:
        """
        测试创建和获取任务
        """
        task_content = {
            "type": "integration_test",
            "data": {"value": "test_data"}
        }
        
        created_task = await repository_accessor.create_task(
            task_content=task_content,
            priority=TaskPriority.HIGH,
            timeout_seconds=600,
        )
        
        assert created_task.task_identifier is not None
        assert created_task.task_content["type"] == "integration_test"
        assert created_task.priority == TaskPriority.HIGH
        assert created_task.status == TaskStatus.PENDING
        
        retrieved_task = await repository_accessor.get_task_by_identifier(created_task.task_identifier)
        
        assert retrieved_task is not None
        assert retrieved_task.task_identifier == created_task.task_identifier
    
    async def test_get_pending_tasks(self, repository_accessor) -> None:
        """
        测试获取待处理任务
        """
        # 创建3个任务
        await repository_accessor.create_task({"type": "test1"}, priority=TaskPriority.LOW)
        await repository_accessor.create_task({"type": "test2"}, priority=TaskPriority.HIGH)
        await repository_accessor.create_task({"type": "test3"}, priority=TaskPriority.MEDIUM)
        
        pending_tasks = await repository_accessor.get_pending_tasks()
        
        assert len(pending_tasks) == 3
        # 应该按优先级排序
        assert pending_tasks[0].priority == TaskPriority.HIGH
        assert pending_tasks[1].priority == TaskPriority.MEDIUM
        assert pending_tasks[2].priority == TaskPriority.LOW
    
    async def test_update_task_status(self, repository_accessor) -> None:
        """
        测试更新任务状态
        """
        task = await repository_accessor.create_task({"type": "test"})
        
        updated_task = await repository_accessor.update_task_status(
            task.task_identifier,
            TaskStatus.RUNNING,
        )
        
        assert updated_task is not None
        assert updated_task.status == TaskStatus.RUNNING
        
        # 更新为完成状态
        result_data = {"status": "success", "output": "test_output"}
        completed_task = await repository_accessor.update_task_status(
            task.task_identifier,
            TaskStatus.COMPLETED,
            result=result_data,
            execution_duration_seconds=2.5,
        )
        
        assert completed_task is not None
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.result is not None
        assert completed_task.execution_duration_seconds == 2.5
    
    async def test_task_statistics(self, repository_accessor) -> None:
        """
        测试任务统计
        """
        # 创建一些任务
        await repository_accessor.create_task({"type": "pending1"})
        await repository_accessor.create_task({"type": "pending2"})
        
        stats = await repository_accessor.get_task_statistics()
        
        assert stats["counts_by_status"][TaskStatus.PENDING] == 2
        assert stats["total"] == 2
