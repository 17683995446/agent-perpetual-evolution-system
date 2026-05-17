"""
Task Data Repository Accessor - 任务数据仓储访问器（5个单词）

提供任务数据的CRUD操作，使用 SQLAlchemy 2.0 实现异步操作。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, and_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker

from ..layer_4_domain_model.task_domain_entity_definition import (
    TaskDomainEntity,
    TaskStatus,
    TaskPriority,
    TaskExecutionLog,
    Base,
)
from ..layer_7_foundation_utility.unique_identifier_generator import UniqueIdentifierGenerator


class TaskDataRepositoryAccessor:
    """
    任务数据仓储访问器
    使用 SQLAlchemy 2.0 提供异步的 CRUD 操作。
    """
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///./agent_system.db"):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def initialize_database(self) -> None:
        """
        初始化数据库表结构
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def create_task(
        self,
        task_content: Dict[str, Any],
        priority: int = TaskPriority.MEDIUM,
        timeout_seconds: int = 300,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> TaskDomainEntity:
        """
        创建新任务
        """
        task_identifier = UniqueIdentifierGenerator.generate_task_identifier_with_prefix()
        task = TaskDomainEntity(
            task_identifier=task_identifier,
            task_content=task_content,
            priority=priority,
            timeout_seconds=timeout_seconds,
            execution_context=execution_context or {},
        )
        
        async with self.async_session_factory() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        
        return task
    
    async def get_task_by_identifier(self, task_identifier: str) -> Optional[TaskDomainEntity]:
        """
        根据任务标识符获取任务
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(TaskDomainEntity).where(
                    TaskDomainEntity.task_identifier == task_identifier
                )
            )
            return result.scalar_one_or_none()
    
    async def get_pending_tasks(
        self, limit: int = 100, priority_order: bool = True
    ) -> List[TaskDomainEntity]:
        """
        获取待处理的任务
        """
        order_clause = desc(TaskDomainEntity.priority) if priority_order else asc(TaskDomainEntity.priority)
        
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(TaskDomainEntity)
                .where(
                    and_(
                        TaskDomainEntity.status == TaskStatus.PENDING,
                        TaskDomainEntity.is_archived == False,
                    )
                )
                .order_by(order_clause, TaskDomainEntity.created_at)
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def update_task_status(
        self,
        task_identifier: str,
        new_status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_duration_seconds: Optional[float] = None,
    ) -> Optional[TaskDomainEntity]:
        """
        更新任务状态
        """
        async with self.async_session_factory() as session:
            # 先获取任务
            get_result = await session.execute(
                select(TaskDomainEntity).where(
                    TaskDomainEntity.task_identifier == task_identifier
                )
            )
            task = get_result.scalar_one_or_none()
            
            if not task:
                return None
            
            # 更新状态
            task.status = new_status
            
            if result is not None:
                task.result = result
            
            if error_message is not None:
                task.error_message = error_message
            
            if execution_duration_seconds is not None:
                task.execution_duration_seconds = execution_duration_seconds
            
            if new_status == TaskStatus.RUNNING and task.started_at is None:
                task.started_at = datetime.utcnow()
            
            if new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(task)
        
        return task
    
    async def count_tasks_by_status(self, status: str) -> int:
        """
        统计特定状态的任务数量
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.count(TaskDomainEntity.id))
                .where(
                    and_(
                        TaskDomainEntity.status == status,
                        TaskDomainEntity.is_archived == False,
                    )
                )
            )
            return result.scalar() or 0
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        """
        counts = {}
        for status in TaskStatus:
            counts[status.value] = await self.count_tasks_by_status(status.value)
        
        return {
            "counts_by_status": counts,
            "total": sum(counts.values()),
        }
    
    async def log_task_execution(
        self,
        task_id: str,
        log_level: str,
        log_message: str,
        log_metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskExecutionLog:
        """
        记录任务执行日志
        """
        execution_log = TaskExecutionLog(
            task_id=task_id,
            log_level=log_level,
            log_message=log_message,
            log_metadata=log_metadata or {},
        )
        
        async with self.async_session_factory() as session:
            session.add(execution_log)
            await session.commit()
            await session.refresh(execution_log)
        
        return execution_log
