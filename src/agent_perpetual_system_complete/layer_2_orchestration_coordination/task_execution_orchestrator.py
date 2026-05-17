"""
Enhanced Task Execution Orchestrator - 增强型任务执行编排器（6个单词）

负责任务的并发执行、依赖解析、优先级调度、超时控制、重试机制等完整功能。
"""

import asyncio
import time
import heapq
from typing import Dict, Any, Optional, List, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
from functools import total_ordering

from ..layer_3_business_service.task_management_service_provider import (
    TaskManagementServiceProvider,
    TaskExecutionResult,
)
from ..layer_4_domain_model.task_domain_entity_definition import (
    TaskDomainEntity,
    TaskStatus,
    TaskPriority,
)
from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


class TaskDependencyType(str, Enum):
    """
    任务依赖类型
    """
    BLOCKED_BY = "blocked_by"
    DEPENDS_ON = "depends_on"
    TRIGGERED_BY = "triggered_by"


@dataclass
class TaskRetryState:
    """
    任务重试状态
    """
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    backoff_delay_seconds: float = 1.0


@total_ordering
@dataclass
class PriorityQueueItem:
    """
    优先级队列项
    使用负优先级来实现max-heap行为（因为Python的heapq是min-heap）
    """
    priority: int
    submitted_at: float
    task_identifier: str

    def __lt__(self, other: 'PriorityQueueItem') -> bool:
        if self.priority != other.priority:
            return -self.priority < -other.priority
        return self.submitted_at < other.submitted_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriorityQueueItem):
            return NotImplemented
        return (self.priority, self.submitted_at, self.task_identifier) == \
               (other.priority, other.submitted_at, other.task_identifier)


@dataclass
class TaskExecutionContext:
    """
    任务执行上下文
    """
    task: TaskDomainEntity
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TaskExecutionResult] = None
    dependencies_satisfied: bool = False
    is_blocked: bool = False
    error_message: Optional[str] = None
    retry_state: TaskRetryState = field(default_factory=TaskRetryState)
    execution_attempt: int = 0


@dataclass
class ExecutionStatistics:
    """
    执行统计信息
    """
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    timeout_tasks: int = 0
    retried_tasks: int = 0
    average_duration_seconds: float = 0.0
    total_execution_time_seconds: float = 0.0
    tasks_per_minute: float = 0.0
    success_rate: float = 0.0
    average_retries_per_task: float = 0.0


@dataclass
class ExecutionConfiguration:
    """
    执行配置
    """
    max_concurrent_tasks: int = 10
    default_timeout_seconds: int = 300
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    retry_backoff_max: float = 60.0
    enable_priority_scheduling: bool = True
    enable_dependency_resolution: bool = True
    enable_timeout_enforcement: bool = True
    graceful_shutdown_timeout_seconds: int = 30
    enable_dependency_cascading_failure: bool = True
    queue_check_interval_seconds: float = 0.1


class EnhancedTaskExecutionOrchestrator:
    """
    增强型任务执行编排器

    核心职责：
    1. 基于优先级的任务调度（使用优先级队列）
    2. 完整的任务依赖管理和解析
    3. 任务超时控制
    4. 智能重试机制（带指数退避）
    5. 并发控制
    6. 完整的执行统计
    7. 优雅关闭
    """

    def __init__(self, service_provider: TaskManagementServiceProvider, config: Optional[ExecutionConfiguration] = None):
        self.service_provider = service_provider
        self.config = config or ExecutionConfiguration()
        self.logger = get_structured_logger(__name__)

        self._execution_contexts: Dict[str, TaskExecutionContext] = {}
        self._task_dependencies: Dict[str, List[str]] = defaultdict(list)
        self._reverse_dependencies: Dict[str, List[str]] = defaultdict(list)
        self._running_tasks: Set[str] = set()
        self._priority_queue: List[PriorityQueueItem] = []
        self._task_semaphore: Optional[asyncio.Semaphore] = None
        self._is_shutting_down = False
        self._is_running = False
        self._start_time: Optional[datetime] = None
        self._queue_condition: Optional[asyncio.Condition] = None
        self._worker_tasks: List[asyncio.Task] = []

    async def initialize(self) -> None:
        """
        初始化编排器
        """
        self.logger.info(
            "initializing_enhanced_task_execution_orchestrator",
            max_concurrent=self.config.max_concurrent_tasks,
            enable_priority=self.config.enable_priority_scheduling,
            max_retries=self.config.max_retries,
        )

        self._task_semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        self._queue_condition = asyncio.Condition()
        self._is_shutting_down = False
        self._is_running = False
        self._start_time = datetime.utcnow()
        heapq.heapify(self._priority_queue)

        self.logger.info("enhanced_task_execution_orchestrator_initialized")

    async def submit_task_with_dependencies(
        self,
        task: TaskDomainEntity,
        depends_on: Optional[List[str]] = None,
    ) -> str:
        """
        提交任务及其依赖关系

        Args:
            task: 要提交的任务
            depends_on: 依赖的任务标识符列表

        Returns:
            任务标识符
        """
        self._execution_contexts[task.task_identifier] = TaskExecutionContext(
            task=task,
            dependencies_satisfied=not depends_on,
        )

        if depends_on:
            self._task_dependencies[task.task_identifier] = depends_on
            for dep_id in depends_on:
                self._reverse_dependencies[dep_id].append(task.task_identifier)
            self.logger.info(
                "task_submitted_with_dependencies",
                task_identifier=task.task_identifier,
                priority=task.priority,
                depends_on_count=len(depends_on),
            )
        else:
            self.logger.info(
                "task_submitted_without_dependencies",
                task_identifier=task.task_identifier,
                priority=task.priority,
            )

        await self._add_to_priority_queue(task)

        return task.task_identifier

    async def _add_to_priority_queue(self, task: TaskDomainEntity) -> None:
        """
        将任务添加到优先级队列
        """
        if self.config.enable_priority_scheduling:
            item = PriorityQueueItem(
                priority=task.priority,
                submitted_at=time.time(),
                task_identifier=task.task_identifier,
            )
        else:
            item = PriorityQueueItem(
                priority=TaskPriority.MEDIUM,
                submitted_at=time.time(),
                task_identifier=task.task_identifier,
            )

        heapq.heappush(self._priority_queue, item)
        self.logger.debug(
            "task_added_to_priority_queue",
            task_identifier=task.task_identifier,
            priority=task.priority,
            queue_size=len(self._priority_queue),
        )

        async with self._queue_condition:
            self._queue_condition.notify()

    async def start_orchestration(self, executor_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None) -> None:
        """
        启动编排器，开始持续执行任务

        Args:
            executor_fn: 自定义执行函数
        """
        if self._is_running:
            self.logger.warning("orchestrator_already_running")
            return

        self._is_running = True
        self.logger.info("starting_task_orchestration")

        for _ in range(self.config.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker_loop(executor_fn))
            self._worker_tasks.append(worker)

    async def _worker_loop(self, executor_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None) -> None:
        """
        工作线程循环
        """
        self.logger.debug("worker_started")

        while self._is_running and not self._is_shutting_down:
            task_identifier = await self._get_next_task_from_queue()

            if task_identifier is None:
                continue

            try:
                result = await self._execute_single_task_with_timeout(task_identifier, executor_fn)
                await self._handle_task_completion(task_identifier, result)
            except Exception as e:
                self.logger.error(
                    "worker_task_failed",
                    task_identifier=task_identifier,
                    error=str(e),
                )

    async def _get_next_task_from_queue(self) -> Optional[str]:
        """
        从优先级队列获取下一个可执行的任务
        """
        async with self._queue_condition:
            while self._is_running and not self._is_shutting_down:
                if not self._priority_queue:
                    await self._queue_condition.wait()
                    continue

                next_item = heapq.heappop(self._priority_queue)
                task_identifier = next_item.task_identifier

                if task_identifier not in self._execution_contexts:
                    continue

                ctx = self._execution_contexts[task_identifier]

                if ctx.is_blocked:
                    continue

                if not self._check_dependencies_satisfied(task_identifier):
                    continue

                if task_identifier in self._running_tasks:
                    continue

                if ctx.task.status != TaskStatus.PENDING:
                    continue

                return task_identifier

        return None

    async def _execute_single_task_with_timeout(
        self,
        task_identifier: str,
        executor_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> TaskExecutionResult:
        """
        执行单个任务，带超时控制
        """
        if task_identifier not in self._execution_contexts:
            return TaskExecutionResult(
                success=False,
                result=None,
                error_message="Task not found in execution contexts",
                execution_duration_seconds=0.0,
                task_identifier=task_identifier,
            )

        ctx = self._execution_contexts[task_identifier]
        ctx.execution_attempt += 1

        self._running_tasks.add(task_identifier)

        timeout = ctx.task.timeout_seconds or self.config.default_timeout_seconds

        try:
            self.logger.info(
                "starting_task_execution",
                task_identifier=task_identifier,
                attempt=ctx.execution_attempt,
                timeout=timeout,
            )

            ctx.started_at = datetime.utcnow()

            result = await asyncio.wait_for(
                self.service_provider.execute_single_task(task_identifier, executor_fn),
                timeout=timeout,
            )

            return result

        except asyncio.TimeoutError:
            self.logger.warning(
                "task_execution_timeout",
                task_identifier=task_identifier,
                timeout=timeout,
                attempt=ctx.execution_attempt,
            )

            return TaskExecutionResult(
                success=False,
                result=None,
                error_message=f"Task timed out after {timeout} seconds",
                execution_duration_seconds=timeout,
                task_identifier=task_identifier,
            )

        except Exception as e:
            self.logger.error(
                "task_execution_error",
                task_identifier=task_identifier,
                error=str(e),
                attempt=ctx.execution_attempt,
            )

            return TaskExecutionResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_duration_seconds=(datetime.utcnow() - ctx.started_at).total_seconds(),
                task_identifier=task_identifier,
            )

        finally:
            if task_identifier in self._running_tasks:
                self._running_tasks.remove(task_identifier)

    async def _handle_task_completion(self, task_identifier: str, result: TaskExecutionResult) -> None:
        """
        处理任务完成事件
        """
        if task_identifier not in self._execution_contexts:
            return

        ctx = self._execution_contexts[task_identifier]
        ctx.result = result
        ctx.completed_at = datetime.utcnow()

        if result.success:
            self.logger.info(
                "task_completed_successfully",
                task_identifier=task_identifier,
                duration=result.execution_duration_seconds,
                attempt=ctx.execution_attempt,
            )
            await self._notify_dependent_tasks(task_identifier)
        else:
            await self._handle_task_failure(task_identifier, ctx)

    async def _handle_task_failure(self, task_identifier: str, ctx: TaskExecutionContext) -> None:
        """
        处理任务失败，考虑重试
        """
        if not self.config.retry_on_failure:
            self.logger.error(
                "task_failed_no_retry",
                task_identifier=task_identifier,
                retry_disabled=True,
            )
            await self._notify_dependent_tasks_failure(task_identifier)
            return

        if ctx.retry_state.retry_count >= self.config.max_retries:
            self.logger.error(
                "task_failed_max_retries_exceeded",
                task_identifier=task_identifier,
                retries=ctx.retry_state.retry_count,
                max_retries=self.config.max_retries,
            )
            await self._notify_dependent_tasks_failure(task_identifier)
            return

        ctx.retry_state.retry_count += 1
        ctx.retry_state.last_retry_at = datetime.utcnow()

        backoff_delay = min(
            self.config.retry_backoff_base ** ctx.retry_state.retry_count,
            self.config.retry_backoff_max,
        )
        ctx.retry_state.backoff_delay_seconds = backoff_delay

        self.logger.warning(
            "scheduling_task_retry",
            task_identifier=task_identifier,
            retry_count=ctx.retry_state.retry_count,
            backoff_delay=backoff_delay,
        )

        asyncio.create_task(self._schedule_retry(task_identifier, backoff_delay))

    async def _schedule_retry(self, task_identifier: str, delay_seconds: float) -> None:
        """
        调度任务重试
        """
        await asyncio.sleep(delay_seconds)

        if self._is_shutting_down:
            return

        if task_identifier not in self._execution_contexts:
            return

        ctx = self._execution_contexts[task_identifier]
        await self._add_to_priority_queue(ctx.task)

    async def _notify_dependent_tasks(self, completed_task_id: str) -> None:
        """
        通知依赖任务，某个任务已完成
        """
        if completed_task_id not in self._reverse_dependencies:
            return

        for dependent_task_id in self._reverse_dependencies[completed_task_id]:
            if self._check_dependencies_satisfied(dependent_task_id):
                self.logger.debug(
                    "dependencies_satisfied_for_task",
                    dependent_task_id=dependent_task_id,
                    completed_task=completed_task_id,
                )
                if dependent_task_id in self._execution_contexts:
                    self._execution_contexts[dependent_task_id].dependencies_satisfied = True
                    await self._add_to_priority_queue(self._execution_contexts[dependent_task_id].task)

    async def _notify_dependent_tasks_failure(self, failed_task_id: str) -> None:
        """
        通知依赖任务，某个任务已失败
        """
        if not self.config.enable_dependency_cascading_failure:
            return

        if failed_task_id not in self._reverse_dependencies:
            return

        for dependent_task_id in self._reverse_dependencies[failed_task_id]:
            if dependent_task_id in self._execution_contexts:
                ctx = self._execution_contexts[dependent_task_id]
                ctx.is_blocked = True
                ctx.error_message = f"Dependency failed: {failed_task_id}"

                self.logger.warning(
                    "dependent_task_blocked",
                    dependent_task_id=dependent_task_id,
                    failed_dependency=failed_task_id,
                )

    def _check_dependencies_satisfied(self, task_identifier: str) -> bool:
        """
        检查任务依赖是否满足
        """
        if not self.config.enable_dependency_resolution:
            return True

        if task_identifier not in self._task_dependencies:
            return True

        dependencies = self._task_dependencies[task_identifier]

        for dep_id in dependencies:
            if dep_id not in self._execution_contexts:
                return False

            ctx = self._execution_contexts[dep_id]
            if ctx.result is None or not ctx.result.success:
                return False

        return True

    def get_execution_statistics(self) -> ExecutionStatistics:
        """
        获取执行统计信息
        """
        total_tasks = len(self._execution_contexts)
        completed_tasks = sum(
            1 for ctx in self._execution_contexts.values()
            if ctx.result is not None
        )
        failed_tasks = sum(
            1 for ctx in self._execution_contexts.values()
            if ctx.result is not None and not ctx.result.success
        )
        timeout_tasks = sum(
            1 for ctx in self._execution_contexts.values()
            if ctx.result is not None and "timed out" in (ctx.result.error_message or "")
        )
        retried_tasks = sum(
            1 for ctx in self._execution_contexts.values()
            if ctx.retry_state.retry_count > 0
        )
        running_tasks = len(self._running_tasks)
        pending_tasks = total_tasks - completed_tasks - running_tasks

        total_duration = sum(
            ctx.result.execution_duration_seconds
            for ctx in self._execution_contexts.values()
            if ctx.result is not None
        )
        average_duration = total_duration / completed_tasks if completed_tasks > 0 else 0.0

        total_retries = sum(
            ctx.retry_state.retry_count
            for ctx in self._execution_contexts.values()
        )
        average_retries = total_retries / total_tasks if total_tasks > 0 else 0.0

        elapsed_minutes = (datetime.utcnow() - self._start_time).total_seconds() / 60 if self._start_time else 1.0
        tasks_per_minute = completed_tasks / elapsed_minutes if elapsed_minutes > 0 else 0.0

        success_rate = (completed_tasks - failed_tasks) / completed_tasks if completed_tasks > 0 else 0.0

        return ExecutionStatistics(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            running_tasks=running_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            timeout_tasks=timeout_tasks,
            retried_tasks=retried_tasks,
            average_duration_seconds=average_duration,
            total_execution_time_seconds=total_duration,
            tasks_per_minute=tasks_per_minute,
            success_rate=success_rate,
            average_retries_per_task=average_retries,
        )

    async def graceful_shutdown(self) -> None:
        """
        优雅关闭编排器
        """
        self.logger.info("initiating_graceful_shutdown")
        self._is_shutting_down = True
        self._is_running = False

        async with self._queue_condition:
            self._queue_condition.notify_all()

        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            self._worker_tasks = []

        start_time = time.time()
        timeout = self.config.graceful_shutdown_timeout_seconds

        while self._running_tasks and (time.time() - start_time) < timeout:
            self.logger.info(
                "waiting_for_running_tasks",
                remaining_tasks=len(self._running_tasks),
            )
            await asyncio.sleep(0.5)

        self.logger.info(
            "graceful_shutdown_completed",
            final_statistics=self.get_execution_statistics().__dict__,
        )

    async def execute_tasks_batch(
        self,
        task_identifiers: Optional[List[str]] = None,
        executor_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> Dict[str, TaskExecutionResult]:
        """
        批量执行任务（保持向后兼容）

        Args:
            task_identifiers: 要执行的任务标识符列表，None表示执行所有待处理任务
            executor_fn: 自定义执行函数

        Returns:
            任务标识符到执行结果的映射
        """
        if task_identifiers is None:
            pending_tasks = await self.service_provider.get_pending_tasks_for_execution()
            task_identifiers = [task.task_identifier for task in pending_tasks]

        self.logger.info(
            "starting_batch_execution",
            task_count=len(task_identifiers),
        )

        await self.start_orchestration(executor_fn)

        completed_tasks: Dict[str, TaskExecutionResult] = {}
        while len(completed_tasks) < len(task_identifiers) and not self._is_shutting_down:
            for tid in task_identifiers:
                if tid not in completed_tasks and tid in self._execution_contexts:
                    ctx = self._execution_contexts[tid]
                    if ctx.result is not None:
                        completed_tasks[tid] = ctx.result

            if len(completed_tasks) < len(task_identifiers):
                await asyncio.sleep(0.1)

        await self.graceful_shutdown()

        self.logger.info(
            "batch_execution_completed",
            total_tasks=len(task_identifiers),
            successful=sum(1 for r in completed_tasks.values() if r.success),
            failed=sum(1 for r in completed_tasks.values() if not r.success),
        )

        return completed_tasks
