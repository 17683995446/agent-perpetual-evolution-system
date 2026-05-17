"""
任务服务模块 - 任务业务逻辑层

该模块负责：
- 任务创建和管理的业务逻辑
- 任务执行流程编排
- 任务与记忆系统的交互
"""

import asyncio
from typing import Dict, List, Optional, Any
from ...core.logger_config import get_structured_logger
from ...utils.id_generator import IDGenerator
from ...utils.time_utils import Timer
from .task_repository import TaskRepository
from ...core.database_models import TaskStatusEnum

logger = get_structured_logger(__name__)


class TaskService:
    """
    任务服务类

    提供任务的完整业务逻辑，包括：
    - 任务创建
    - 任务查询
    - 任务执行
    - 任务状态管理
    """

    @staticmethod
    async def create_new_task(
        content: Dict[str, Any],
        priority: int = 5,
        timeout: int = 300,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        创建新任务

        Args:
            content: 任务内容
            priority: 优先级（1-10）
            timeout: 超时时间（秒）
            context: 任务上下文

        Returns:
            Dict: 包含任务信息的字典

        Example:
            >>> result = await TaskService.create_new_task(
            ...     content={"type": "analysis", "data": "..."},
            ...     priority=8
            ... )
        """
        task_id = IDGenerator.generate_task_id()

        task = await TaskRepository.create_task(
            task_id=task_id,
            content=content,
            priority=priority,
            timeout=timeout,
            context=context,
        )

        logger.info(
            "task_service_created_task",
            task_id=task_id,
            priority=priority,
            content_type=content.get("type", "unknown")
        )

        return {
            "task_id": task.task_id,
            "status": task.status,
            "priority": task.priority,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }

    @staticmethod
    async def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            Optional[Dict]: 任务信息字典

        Example:
            >>> task = await TaskService.get_task("task_123")
        """
        task = await TaskRepository.get_task_by_id(task_id)

        if not task:
            logger.warning("task_not_found", task_id=task_id)
            return None

        return {
            "task_id": task.task_id,
            "content": task.content,
            "priority": task.priority,
            "status": task.status,
            "timeout": task.timeout,
            "context": task.context,
            "result": task.result,
            "error_message": task.error_message,
            "execution_time": task.execution_time,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

    @staticmethod
    async def get_pending_task_list(limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取待处理任务列表

        Args:
            limit: 返回的最大任务数量

        Returns:
            List[Dict]: 任务信息字典列表

        Example:
            >>> tasks = await TaskService.get_pending_task_list(limit=10)
        """
        tasks = await TaskRepository.get_pending_tasks(limit=limit)

        return [
            {
                "task_id": task.task_id,
                "content": task.content,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            }
            for task in tasks
        ]

    @staticmethod
    async def execute_single_task(task_id: str) -> Dict[str, Any]:
        """
        执行单个任务

        Args:
            task_id: 任务ID

        Returns:
            Dict: 执行结果

        Raises:
            Exception: 如果任务执行失败

        Example:
            >>> result = await TaskService.execute_single_task("task_123")
        """
        logger.info("task_service_start_execution", task_id=task_id)

        with Timer() as timer:
            try:
                # 更新状态为运行中
                await TaskRepository.update_task_status(
                    task_id, TaskStatusEnum.RUNNING
                )

                # 获取任务详情
                task = await TaskRepository.get_task_by_id(task_id)
                if not task:
                    raise ValueError(f"Task not found: {task_id}")

                # 执行任务逻辑（这里是模拟实现）
                result = await TaskService._execute_task_logic(task)

                # 更新状态为已完成
                await TaskRepository.update_task_status(
                    task_id,
                    TaskStatusEnum.COMPLETED,
                    result=result,
                    execution_time=timer.elapsed_time,
                )

                logger.info(
                    "task_service_completed",
                    task_id=task_id,
                    execution_time=timer.elapsed_time
                )

                return {
                    "status": "success",
                    "task_id": task_id,
                    "result": result,
                    "execution_time": timer.elapsed_time,
                }

            except Exception as e:
                # 更新状态为失败
                await TaskRepository.update_task_status(
                    task_id,
                    TaskStatusEnum.FAILED,
                    error_message=str(e),
                    execution_time=timer.elapsed_time,
                )

                logger.error(
                    "task_service_failed",
                    task_id=task_id,
                    error=str(e),
                    exc_info=True
                )

                return {
                    "status": "failed",
                    "task_id": task_id,
                    "error": str(e),
                    "execution_time": timer.elapsed_time,
                }

    @staticmethod
    async def _execute_task_logic(task) -> Dict[str, Any]:
        """
        执行任务的实际逻辑

        这是一个模拟实现，可以根据实际需求扩展。

        Args:
            task: 任务对象

        Returns:
            Dict: 执行结果
        """
        # 模拟任务执行过程
        await asyncio.sleep(0.5)

        return {
            "status": "success",
            "message": f"Task {task.task_id} executed successfully",
            "output": f"Processed content: {task.content}",
            "steps_completed": ["step_1_analyze", "step_2_process", "step_3_output"],
        }

    @staticmethod
    async def get_task_statistics() -> Dict[str, Any]:
        """
        获取任务统计信息

        Returns:
            Dict: 统计信息

        Example:
            >>> stats = await TaskService.get_task_statistics()
        """
        pending_count = await TaskRepository.get_task_count_by_status(TaskStatusEnum.PENDING)
        running_count = await TaskRepository.get_task_count_by_status(TaskStatusEnum.RUNNING)
        completed_count = await TaskRepository.get_task_count_by_status(TaskStatusEnum.COMPLETED)
        failed_count = await TaskRepository.get_task_count_by_status(TaskStatusEnum.FAILED)

        return {
            "pending": pending_count,
            "running": running_count,
            "completed": completed_count,
            "failed": failed_count,
            "total": pending_count + running_count + completed_count + failed_count,
        }
