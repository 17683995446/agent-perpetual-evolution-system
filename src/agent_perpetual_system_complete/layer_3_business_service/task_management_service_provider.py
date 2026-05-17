"""
Task Management Service Provider - 任务管理服务提供者（5个单词）

提供完整的任务管理业务逻辑，包括创建、执行、监控等功能。
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

from ..layer_5_data_access.task_data_repository_accessor import TaskDataRepositoryAccessor
from ..layer_4_domain_model.task_domain_entity_definition import (
    TaskDomainEntity,
    TaskStatus,
    TaskPriority,
)
from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


@dataclass
class TaskExecutionResult:
    """
    任务执行结果
    """
    success: bool
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_duration_seconds: float
    task_identifier: str


class TaskManagementServiceProvider:
    """
    任务管理服务提供者
    提供完整的任务管理业务逻辑。
    """
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///./agent_system.db"):
        self.repo = TaskDataRepositoryAccessor(db_url)
        self.logger = get_structured_logger(__name__)
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """
        初始化服务
        """
        if not self.is_initialized:
            await self.repo.initialize_database()
            self.is_initialized = True
            self.logger.info("task_management_service_initialized")
    
    async def create_and_submit_task(
        self,
        task_content: Dict[str, Any],
        priority: int = TaskPriority.MEDIUM,
        timeout_seconds: int = 300,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> TaskDomainEntity:
        """
        创建并提交任务
        """
        task = await self.repo.create_task(
            task_content=task_content,
            priority=priority,
            timeout_seconds=timeout_seconds,
            execution_context=execution_context,
        )
        
        self.logger.info(
            "task_created_and_submitted",
            task_identifier=task.task_identifier,
            priority=task.priority,
        )
        
        return task
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def execute_single_task(
        self,
        task_identifier: str,
        executor_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> TaskExecutionResult:
        """
        执行单个任务
        使用 tenacity 实现自动重试。
        """
        start_time = time.time()

        try:
            self.logger.info("starting_task_execution", task_identifier=task_identifier)

            # 更新状态为运行中
            await self.repo.update_task_status(
                task_identifier,
                TaskStatus.RUNNING,
            )

            # 实际执行（这里模拟一个示例）
            if executor_fn is not None:
                task = await self.repo.get_task_by_identifier(task_identifier)
                if task:
                    result = executor_fn(task.task_content)
                    if hasattr(result, "__await__"):
                        result_data = await result
                    else:
                        result_data = result
                else:
                    result_data = {"status": "failed", "reason": "task_not_found"}
            else:
                result_data = await self._simulate_task_execution(task_identifier)
            
            execution_duration = time.time() - start_time
            
            # 更新状态为完成
            await self.repo.update_task_status(
                task_identifier,
                TaskStatus.COMPLETED,
                result=result_data,
                execution_duration_seconds=execution_duration,
            )
            
            self.logger.info(
                "task_execution_completed",
                task_identifier=task_identifier,
                duration=execution_duration,
            )
            
            return TaskExecutionResult(
                success=True,
                result=result_data,
                error_message=None,
                execution_duration_seconds=execution_duration,
                task_identifier=task_identifier,
            )
            
        except Exception as e:
            execution_duration = time.time() - start_time
            
            await self.repo.update_task_status(
                task_identifier,
                TaskStatus.FAILED,
                error_message=str(e),
                execution_duration_seconds=execution_duration,
            )
            
            self.logger.error(
                "task_execution_failed",
                task_identifier=task_identifier,
                error=str(e),
                duration=execution_duration,
            )
            
            return TaskExecutionResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_duration_seconds=execution_duration,
                task_identifier=task_identifier,
            )
    
    async def _simulate_task_execution(self, task_identifier: str) -> Dict[str, Any]:
        """
        模拟任务执行（实际项目中替换为真实逻辑）
        """
        await asyncio.sleep(0.5)
        return {
            "status": "success",
            "data": {"task_identifier": task_identifier, "processed": True},
            "message": "Task completed successfully",
        }
    
    async def get_pending_tasks_for_execution(self, limit: int = 100) -> List[TaskDomainEntity]:
        """
        获取待执行的任务
        """
        tasks = await self.repo.get_pending_tasks(limit=limit)
        return tasks
    
    async def get_task_statistics_report(self) -> Dict[str, Any]:
        """
        获取任务统计报告
        """
        stats = await self.repo.get_task_statistics()
        return stats
