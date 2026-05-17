"""
Test Task Domain Entity Definition - 测试任务领域实体（6个单词）

测试任务领域实体的单元测试，使用 pytest 和 pytest-asyncio。
"""

import pytest
import pytest_asyncio
from datetime import datetime

from src.agent_perpetual_system_complete.layer_4_domain_model.task_domain_entity_definition import (
    TaskDomainEntity,
    TaskStatus,
    TaskPriority,
    TaskExecutionLog,
)


class TestTaskStatusTest:
    """
    任务状态测试
    """
    
    def test_task_status_enum_values(self) -> None:
        """
        测试任务状态枚举值
        """
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"
        assert TaskStatus.TIMEOUT == "timeout"
    
    def test_task_priority_enum_values(self) -> None:
        """
        测试任务优先级枚举值
        """
        assert TaskPriority.LOWEST == 1
        assert TaskPriority.LOW == 2
        assert TaskPriority.MEDIUM == 3
        assert TaskPriority.HIGH == 4
        assert TaskPriority.HIGHEST == 5


class TestTaskDomainEntityTest:
    """
    任务领域实体测试
    """
    
    def test_task_entity_initialization(self) -> None:
        """
        测试任务实体初始化
        """
        entity = TaskDomainEntity(
            task_identifier="task_test_001",
            task_content={"type": "test", "data": "test_data"},
            priority=TaskPriority.HIGH,
        )
        
        assert entity.task_identifier == "task_test_001"
        assert entity.task_content["type"] == "test"
        assert entity.priority == TaskPriority.HIGH
        assert entity.status == TaskStatus.PENDING
        assert entity.is_archived is False
    
    def test_task_entity_repr(self) -> None:
        """
        测试任务实体的 __repr__ 方法
        """
        entity = TaskDomainEntity(
            id=1,
            task_identifier="task_test_001",
            task_content={},
        )
        
        repr_str = repr(entity)
        
        assert "TaskDomainEntity" in repr_str
        assert "task_test_001" in repr_str


class TestTaskExecutionLogTest:
    """
    任务执行日志测试
    """
    
    def test_execution_log_initialization(self) -> None:
        """
        测试任务执行日志初始化
        """
        log = TaskExecutionLog(
            task_id="task_test_001",
            log_level="INFO",
            log_message="Test log message",
        )
        
        assert log.task_id == "task_test_001"
        assert log.log_level == "INFO"
        assert log.log_message == "Test log message"
