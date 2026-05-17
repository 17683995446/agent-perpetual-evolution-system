
"""
Optimized Concurrency Task Pool - 优化并发任务池（7个单词）
实现高性能并发任务管理，支持任务池、限流、批量处理。
"""

import asyncio
import time
import random
from typing import Dict, Any, Optional, List, Set, Callable, Awaitable, Generic, TypeVar
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from abc import ABC, abstractmethod


T = TypeVar('T')


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class TaskResult(Generic[T]):
    """任务执行结果"""
    task_id: str
    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    retry_count: int = 0


@dataclass
class PoolStatistics:
    """任务池统计"""
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    success_rate: float = 1.0
    throughput_tasks_per_second: float = 0.0


class ConcurrencyStrategy(Enum):
    """并发策略"""
    FIXED_POOL = "fixed_pool"
    ADAPTIVE = "adaptive"
    DYNAMIC = "dynamic"


class CircuitBreakerState(Enum):
    """断路器状态"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    断路器模式实现 - 防止级联失败
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_timeout = half_open_timeout
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        
    def record_success(self) -&gt; None:
        """记录成功"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self) -&gt; None:
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count &gt;= self.failure_threshold:
            if self.state == CircuitBreakerState.CLOSED:
                self.state = CircuitBreakerState.OPEN
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
    
    def allow_request(self) -&gt; bool:
        """检查是否允许请求"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time &gt; self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False


class OptimizedConcurrencyPool:
    """
    优化的并发任务池
    支持多种并发策略、限流、断路器模式、任务监控等高级特性
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 10,
        min_concurrent_tasks: int = 2,
        concurrency_strategy: ConcurrencyStrategy = ConcurrencyStrategy.FIXED_POOL,
        queue_size: int = 1000,
        enable_circuit_breaker: bool = True,
        enable_throttling: bool = True,
        max_tasks_per_second: float = 100.0,
        thread_pool_size: int = 4
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.min_concurrent_tasks = min_concurrent_tasks
        self.concurrency_strategy = concurrency_strategy
        self.queue_size = queue_size
        self.enable_circuit_breaker = enable_circuit_breaker
        self.enable_throttling = enable_throttling
        self.max_tasks_per_second = max_tasks_per_second
        
        self._current_concurrent_tasks = min_concurrent_tasks
        self._task_queue: deque = deque()
        self._running_tasks: Set[str] = set()
        self._task_results: Dict[str, TaskResult] = {}
        self._statistics = PoolStatistics()
        
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._circuit_breaker = CircuitBreaker()
        self._rate_limit_tokens = self.max_tasks_per_second
        self._last_rate_limit_update = time.time()
        
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        self._is_running = False
        self._start_time: Optional[float] = None
        
    async def initialize(self) -&gt; None:
        """初始化任务池"""
        self._is_running = True
        self._start_time = time.time()
        self._rate_limit_tokens = self.max_tasks_per_second
        
    async def shutdown(self, wait: bool = True) -&gt; None:
        """关闭任务池"""
        self._is_running = False
        
        if wait:
            while self._running_tasks:
                await asyncio.sleep(0.1)
        
        self._thread_pool.shutdown(wait=wait)
        
    async def submit_task(
        self,
        task_id: str,
        task_func: Callable[..., Awaitable[T]],
        *args,
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout: Optional[float] = None,
        **kwargs
    ) -&gt; Optional[TaskResult]:
        """
        提交任务到任务池
        """
        if not self._is_running:
            await self.initialize()
            
        if self.enable_circuit_breaker and not self._circuit_breaker.allow_request():
            return TaskResult(
                task_id=task_id,
                success=False,
                error=Exception("Circuit breaker is open"),
                start_time=time.time(),
                end_time=time.time()
            )
            
        if self.enable_throttling:
            await self._acquire_rate_limit_token()
            
        self._statistics.total_tasks += 1
        self._statistics.pending_tasks += 1
        
        task_result = TaskResult(task_id=task_id, success=False)
        self._task_results[task_id] = task_result
        
        try:
            async with self._semaphore:
                self._running_tasks.add(task_id)
                self._statistics.pending_tasks -= 1
                self._statistics.running_tasks += 1
                
                task_result.start_time = time.time()
                
                try:
                    if timeout:
                        result = await asyncio.wait_for(
                            task_func(*args, **kwargs),
                            timeout=timeout
                        )
                    else:
                        result = await task_func(*args, **kwargs)
                        
                    task_result.result = result
                    task_result.success = True
                    self._statistics.completed_tasks += 1
                    
                    if self.enable_circuit_breaker:
                        self._circuit_breaker.record_success()
                        
                except Exception as e:
                    task_result.error = e
                    task_result.success = False
                    self._statistics.failed_tasks += 1
                    
                    if self.enable_circuit_breaker:
                        self._circuit_breaker.record_failure()
                        
                task_result.end_time = time.time()
                if task_result.start_time and task_result.end_time:
                    task_result.duration = task_result.end_time - task_result.start_time
                    self._statistics.total_execution_time += task_result.duration
                
        finally:
            self._running_tasks.discard(task_id)
            self._statistics.running_tasks -= 1
            
        self._update_statistics()
        return task_result
        
    async def submit_tasks_batch(
        self,
        tasks: List[Dict[str, Any]],
        batch_size: int = 10
    ) -&gt; List[TaskResult]:
        """
        批量提交任务
        """
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[
                    self.submit_task(
                        task['task_id'],
                        task['task_func'],
                        *task.get('args', []),
                        priority=task.get('priority', TaskPriority.MEDIUM),
                        timeout=task.get('timeout'),
                        **task.get('kwargs', {})
                    )
                    for task in batch
                ]
            )
            results.extend(batch_results)
            
        return results
        
    async def _acquire_rate_limit_token(self) -&gt; None:
        """获取限流令牌"""
        now = time.time()
        elapsed = now - self._last_rate_limit_update
        
        if elapsed &gt; 0:
            new_tokens = elapsed * self.max_tasks_per_second
            self._rate_limit_tokens = min(
                self._rate_limit_tokens + new_tokens,
                self.max_tasks_per_second
            )
            self._last_rate_limit_update = now
            
        while self._rate_limit_tokens &lt; 1:
            await asyncio.sleep(0.01)
            now = time.time()
            elapsed = now - self._last_rate_limit_update
            
            if elapsed &gt; 0:
                new_tokens = elapsed * self.max_tasks_per_second
                self._rate_limit_tokens = min(
                    self._rate_limit_tokens + new_tokens,
                    self.max_tasks_per_second
                )
                self._last_rate_limit_update = now
                
        self._rate_limit_tokens -= 1
        
    def _update_statistics(self) -&gt; None:
        """更新统计信息"""
        total = self._statistics.completed_tasks + self._statistics.failed_tasks
        
        if total &gt; 0:
            self._statistics.success_rate = self._statistics.completed_tasks / total
            self._statistics.average_execution_time = (
                self._statistics.total_execution_time / total
            )
            
        if self._start_time:
            elapsed = time.time() - self._start_time
            if elapsed &gt; 0:
                self._statistics.throughput_tasks_per_second = total / elapsed
                
    def get_statistics(self) -&gt; PoolStatistics:
        """获取当前统计信息"""
        return self._statistics
        
    def get_active_task_count(self) -&gt; int:
        """获取活跃任务数"""
        return len(self._running_tasks)
        
    def get_queue_size(self) -&gt; int:
        """获取队列大小"""
        return len(self._task_queue)
        
    def is_healthy(self) -&gt; bool:
        """检查任务池是否健康"""
        return (
            self._is_running and
            self._circuit_breaker.state != CircuitBreakerState.OPEN and
            self._statistics.success_rate &gt; 0.8
        )


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Optional[List[type]] = None
):
    """
    异步重试装饰器 - 支持指数退避+抖动
    """
    if retry_exceptions is None:
        retry_exceptions = [Exception]
        
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except tuple(retry_exceptions) as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        break
                        
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random())
                        
                    await asyncio.sleep(delay)
                    
            raise last_exception
            
        return wrapper
    return decorator


class LRUCache(Generic[T]):
    """
    LRU缓存实现 - O(1)时间复杂度的缓存
    """
    
    def __init__(self, capacity: int = 1000, ttl_seconds: Optional[float] = None):
        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, T] = {}
        self.timestamps: Dict[str, float] = {}
        self.order: deque = deque()
        self.hits = 0
        self.misses = 0
        
    def get(self, key: str) -&gt; Optional[T]:
        """获取缓存项"""
        if key not in self.cache:
            self.misses += 1
            return None
            
        if self.ttl_seconds is not None:
            if time.time() - self.timestamps[key] &gt; self.ttl_seconds:
                self.misses += 1
                del self.cache[key]
                del self.timestamps[key]
                return None
                
        self.hits += 1
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)
        return self.cache[key]
        
    def set(self, key: str, value: T) -&gt; None:
        """设置缓存项"""
        if key in self.cache:
            self.order.remove(key)
            
        if len(self.cache) &gt;= self.capacity:
            oldest_key = self.order.popleft()
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            
        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.order.append(key)
        
    def get_hit_rate(self) -&gt; float:
        """获取缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total &gt; 0 else 0.0
        
    def clear(self) -&gt; None:
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
        self.order.clear()
        self.hits = 0
        self.misses = 0

