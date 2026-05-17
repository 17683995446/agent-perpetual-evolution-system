"""
任务仓储模块 - 任务数据访问层

该模块负责：
- 任务数据的持久化操作
- 任务查询和过滤
- 任务状态管理
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database_manager import get_database_session
from ...core.database_models import TaskDatabaseModel
from ...core.logger_config import get_structured_logger

logger = get_structured_logger(__name__)


class TaskRepository:
    """
    任务仓储类

    提供任务数据的CRUD操作，
    负责与数据库的交互。
    """

    @staticmethod
    async def create_task(
        task_id: str,
        content: Dict[str, Any],
        priority: int = 5,
        timeout: int = 300,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskDatabaseModel:
        """
        创建新任务

        Args:
            task_id: 任务唯一标识符
            content: 任务内容
            priority: 优先级（1-10）
            timeout: 超时时间（秒）
            context: 任务上下文

        Returns:
            TaskDatabaseModel: 创建的任务对象

        Example:
            >>> task = await TaskRepository.create_task(
            ...     task_id="task_123",
            ...     content={"type": "test"},
            ...     priority=8
            ... )
        """
        async with get_database_session() as session:
            task = TaskDatabaseModel(
                task_id=task_id,
                content=content,
                priority=priority,
                timeout=timeout,
                context=context or {},
            )
            session.add(task)
            await session.flush()
            await session.refresh(task)

            logger.info(
                "task_created_in_repository",
                task_id=task_id,
                priority=priority
            )
            return task

    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[TaskDatabaseModel]:
        """
        根据ID获取任务

        Args:
            task_id: 任务ID

        Returns:
            Optional[TaskDatabaseModel]: 任务对象，如果不存在返回None

        Example:
            >>> task = await TaskRepository.get_task_by_id("task_123")
        """
        async with get_database_session() as session:
            result = await session.execute(
                select(TaskDatabaseModel).where(
                    TaskDatabaseModel.task_id == task_id
                )
            )
            task = result.scalar_one_or_none()
            if task:
                await session.refresh(task)
            return task

    @staticmethod
    async def get_pending_tasks(limit: int = 100) -> List[TaskDatabaseModel]:
        """
        获取待处理任务列表

        按优先级（降序）和创建时间（升序）排序。

        Args:
            limit: 返回的最大任务数量

        Returns:
            List[TaskDatabaseModel]: 待处理任务列表

        Example:
            >>> tasks = await TaskRepository.get_pending_tasks(limit=10)
        """
        async with get_database_session() as session:
            result = await session.execute(
                select(TaskDatabaseModel)
                .where(TaskDatabaseModel.status == "pending")
                .order_by(desc(TaskDatabaseModel.priority), TaskDatabaseModel.created_at)
                .limit(limit)
            )
            return list(result.scalars().all())

    @staticmethod
    async def update_task_status(
        task_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None,
    ) -> Optional[TaskDatabaseModel]:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            result: 执行结果
            error_message: 错误信息
            execution_time: 执行耗时

        Returns:
            Optional[TaskDatabaseModel]: 更新后的任务对象

        Example:
            >>> task = await TaskRepository.update_task_status(
            ...     "task_123",
            ...     status="completed",
            ...     result={"output": "success"}
            ... )
        """
        async with get_database_session() as session:
            result_query = await session.execute(
                select(TaskDatabaseModel).where(
                    TaskDatabaseModel.task_id == task_id
                )
            )
            task = result_query.scalar_one_or_none()

            if task:
                task.status = status
                if result is not None:
                    task.result = result
                if error_message is not None:
                    task.error_message = error_message
                if execution_time is not None:
                    task.execution_time = execution_time

                await session.commit()
                await session.refresh(task)

                logger.info(
                    "task_status_updated_in_repository",
                    task_id=task_id,
                    status=status
                )
            return task

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否删除成功

        Example:
            >>> deleted = await TaskRepository.delete_task("task_123")
        """
        async with get_database_session() as session:
            result = await session.execute(
                select(TaskDatabaseModel).where(
                    TaskDatabaseModel.task_id == task_id
                )
            )
            task = result.scalar_one_or_none()

            if task:
                await session.delete(task)
                await session.commit()
                logger.info("task_deleted", task_id=task_id)
                return True
            return False

    @staticmethod
    async def get_task_count_by_status(status: str) -> int:
        """
        获取指定状态的任务数量

        Args:
            status: 任务状态

        Returns:
            int: 任务数量

        Example:
            >>> count = await TaskRepository.get_task_count_by_status("pending")
        """
        async with get_database_session() as session:
            result = await session.execute(
                select(TaskDatabaseModel).where(
                    TaskDatabaseModel.status == status
                )
            )
            tasks = result.scalars().all()
            return len(tasks)
