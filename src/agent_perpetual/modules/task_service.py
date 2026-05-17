"""
任务服务模块 - 产品级任务管理系统
"""
import asyncio
import time
import uuid
from typing import Dict, List, Optional
from sqlalchemy import select, desc
from src.agent_perpetual.core.database import get_session
from src.agent_perpetual.core.models import Task, TaskStatus
from src.agent_perpetual.core.logging import get_logger

logger = get_logger(__name__)


class TaskService:
    """任务服务类，提供任务的完整 CRUD 和业务逻辑"""

    @staticmethod
    def generate_task_id() -> str:
        """生成唯一任务ID"""
        return f"task_{uuid.uuid4().hex[:16]}"

    @staticmethod
    async def create_task(
        content: Dict,
        priority: int = 5,
        timeout: int = 300,
        context: Optional[Dict] = None,
    ) -> Task:
        """创建新任务"""
        task_id = TaskService.generate_task_id()
        task = Task(
            task_id=task_id,
            content=content,
            priority=priority,
            status=TaskStatus.PENDING,
            timeout=timeout,
            context=context or {},
        )
        async with get_session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        
        logger.info(
            "task_created",
            task_id=task_id,
            priority=priority,
            content_type=content.get("type", "unknown"),
        )
        return task

    @staticmethod
    async def get_task(task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        async with get_session() as session:
            result = await session.execute(select(Task).where(Task.task_id == task_id))
            task = result.scalar_one_or_none()
            if task:
                await session.refresh(task)
            return task

    @staticmethod
    async def get_pending_tasks(limit: int = 100) -> List[Task]:
        """获取待处理任务，按优先级和创建时间排序"""
        async with get_session() as session:
            result = await session.execute(
                select(Task)
                .where(Task.status == TaskStatus.PENDING)
                .order_by(desc(Task.priority), Task.created_at)
                .limit(limit)
            )
            return list(result.scalars().all())

    @staticmethod
    async def update_task_status(
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None,
    ) -> Optional[Task]:
        """更新任务状态"""
        async with get_session() as session:
            result_stmt = await session.execute(
                select(Task).where(Task.task_id == task_id))
            task = result_stmt.scalar_one_or_none()
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
                    "task_status_updated",
                    task_id=task_id,
                    status=status.value,
                )
            return task

    @staticmethod
    async def execute_task_logic(task: Task) -> Dict:
        """执行任务逻辑"""
        logger.info("executing_task", task_id=task.task_id)
        start_time = time.time()
        
        # 模拟任务执行
        await asyncio.sleep(0.3)
        
        execution_time = time.time() - start_time
        result = {
            "status": "success",
            "result": f"Executed task: {task.task_id}",
            "steps": ["step1", "step2", "step3"],
            "execution_time": execution_time,
        }
        logger.info(
            "task_executed",
            task_id=task.task_id,
            execution_time=execution_time,
        )
        return result

    @staticmethod
    async def run_task(task: Task) -> Optional[Task]:
        """完整的任务执行流程"""
        start_time = time.time()
        try:
            await TaskService.update_task_status(task.task_id, TaskStatus.RUNNING)
            result = await TaskService.execute_task_logic(task)
            execution_time = time.time() - start_time
            await TaskService.update_task_status(
                task.task_id, TaskStatus.COMPLETED, result=result, execution_time=execution_time)
            return await TaskService.get_task(task.task_id)
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "task_execution_failed",
                task_id=task.task_id,
                error=str(e),
                exc_info=True,
            )
            await TaskService.update_task_status(
                task.task_id,
                TaskStatus.FAILED,
                error_message=str(e),
                execution_time=execution_time,
            )
            raise
