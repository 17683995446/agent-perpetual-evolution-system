
"""
Batch Operation Manager - 批量操作管理器（6个单词）
实现高效的批量处理、操作合并、批量I/O优化
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Set, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from functools import wraps, partial
from abc import ABC, abstractmethod


T = TypeVar('T')
R = TypeVar('R')


class BatchStrategy(Enum):
    """批量策略"""
    TIME_BASED = "time_based"
    SIZE_BASED = "size_based"
    ADAPTIVE = "adaptive"


class OperationType(Enum):
    """操作类型"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    UPSERT = "upsert"


@dataclass
class BatchOperation(Generic[T]):
    """批量操作"""
    operation_id: str
    operation_type: OperationType
    items: List[T]
    created_at: float
    priority: int = 0
    timeout_seconds: Optional[float] = None


@dataclass
class BatchResult(Generic[R]):
    """批量结果"""
    operation_id: str
    success_count: int
    failed_count: int
    total_count: int
    results: List[R]
    errors: List[Exception]
    start_time: float
    end_time: float
    duration: float


@dataclass
class BatchStatistics:
    """批量统计"""
    total_operations: int = 0
    total_items: int = 0
    total_success_count: int = 0
    total_failed_count: int = 0
    total_duration: float = 0.0
    average_batch_size: float = 0.0
    average_duration_per_item: float = 0.0
    operations_per_second: float = 0.0
    items_per_second: float = 0.0


class BatchingPolicy:
    """
    批量策略配置
    """
    
    def __init__(
        self,
        max_batch_size: int = 100,
        max_wait_seconds: float = 1.0,
        min_batch_size: int = 1,
        strategy: BatchStrategy = BatchStrategy.ADAPTIVE
    ):
        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_seconds
        self.min_batch_size = min_batch_size
        self.strategy = strategy
        
    def should_flush(self, current_batch_size: int, current_wait_seconds: float) -&gt; bool:
        """判断是否应该刷新批次"""
        if self.strategy == BatchStrategy.SIZE_BASED:
            return current_batch_size &gt;= self.max_batch_size
        elif self.strategy == BatchStrategy.TIME_BASED:
            return current_wait_seconds &gt;= self.max_wait_seconds
        elif self.strategy == BatchStrategy.ADAPTIVE:
            size_ok = current_batch_size &gt;= self.max_batch_size
            time_ok = current_wait_seconds &gt;= self.max_wait_seconds
            min_ok = current_batch_size &gt;= self.min_batch_size
            return (size_ok or time_ok) and min_ok
        return False


class BatchOperationManager(Generic[T, R]):
    """
    批量操作管理器
    实现高效的批量处理、操作合并、性能优化
    """
    
    def __init__(
        self,
        policy: BatchingPolicy,
        handler: Callable[[List[T]], Awaitable[List[R]]],
        auto_flush: bool = True
    ):
        self.policy = policy
        self.handler = handler
        self.auto_flush = auto_flush
        
        self._current_batch: Dict[OperationType, List[Tuple[T, asyncio.Future]]] = defaultdict(list)
        self._batch_start_time: Dict[OperationType, float] = {}
        self._pending_futures: List[asyncio.Future] = []
        
        self._statistics = BatchStatistics()
        self._total_items_processed = 0
        self._start_time = time.time()
        
        self._is_running = False
        self._flush_task: Optional[asyncio.Task] = None
        
    async def start(self) -&gt; None:
        """启动批量管理器"""
        self._is_running = True
        self._start_time = time.time()
        
        if self.auto_flush:
            self._flush_task = asyncio.create_task(self._auto_flush_loop())
            
    async def shutdown(self, wait: bool = True) -&gt; None:
        """关闭批量管理器"""
        self._is_running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            if wait:
                try:
                    await self._flush_task
                except asyncio.CancelledError:
                    pass
                    
        await self._flush_all()
        
    async def submit(
        self,
        operation_type: OperationType,
        item: T,
        timeout: Optional[float] = None
    ) -&gt; R:
        """
        提交单个操作，等待批量处理
        """
        future = asyncio.Future()
        
        if operation_type not in self._current_batch:
            self._current_batch[operation_type] = []
            self._batch_start_time[operation_type] = time.time()
            
        self._current_batch[operation_type].append((item, future))
        
        current_size = len(self._current_batch[operation_type])
        current_wait = time.time() - self._batch_start_time[operation_type]
        
        if self.policy.should_flush(current_size, current_wait):
            await self._flush_operation_type(operation_type)
            
        if timeout is not None:
            return await asyncio.wait_for(future, timeout=timeout)
        else:
            return await future
            
    async def submit_batch(
        self,
        operation_type: OperationType,
        items: List[T]
    ) -&gt; List[R]:
        """
        提交批量操作
        """
        futures = []
        
        for item in items:
            future = asyncio.Future()
            
            if operation_type not in self._current_batch:
                self._current_batch[operation_type] = []
                self._batch_start_time[operation_type] = time.time()
                
            self._current_batch[operation_type].append((item, future))
            futures.append(future)
            
        current_size = len(self._current_batch[operation_type])
        
        if current_size &gt;= self.policy.max_batch_size:
            await self._flush_operation_type(operation_type)
            
        return await asyncio.gather(*futures)
        
    async def flush(self) -&gt; None:
        """手动刷新所有批次"""
        await self._flush_all()
        
    async def _auto_flush_loop(self) -&gt; None:
        """自动刷新循环"""
        while self._is_running:
            try:
                await asyncio.sleep(0.05)
                await self._check_and_flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                pass
                
    async def _check_and_flush(self) -&gt; None:
        """检查并刷新批次"""
        for operation_type in list(self._current_batch.keys()):
            if not self._current_batch[operation_type]:
                continue
                
            current_size = len(self._current_batch[operation_type])
            current_wait = time.time() - self._batch_start_time[operation_type]
            
            if self.policy.should_flush(current_size, current_wait):
                await self._flush_operation_type(operation_type)
                
    async def _flush_all(self) -&gt; None:
        """刷新所有操作类型"""
        for operation_type in list(self._current_batch.keys()):
            await self._flush_operation_type(operation_type)
            
    async def _flush_operation_type(self, operation_type: OperationType) -&gt; None:
        """刷新特定操作类型的批次"""
        batch = self._current_batch.get(operation_type, [])
        if not batch:
            return
            
        self._current_batch[operation_type] = []
        self._batch_start_time[operation_type] = time.time()
        
        items = [item for item, future in batch]
        futures = [future for item, future in batch]
        
        operation_id = f"{operation_type.value}_{time.time()}"
        start_time = time.time()
        
        self._statistics.total_operations += 1
        self._statistics.total_items += len(items)
        
        try:
            results = await self.handler(items)
            
            success_count = len(results)
            failed_count = 0
            errors = []
            
            for future, result in zip(futures, results):
                if not future.done():
                    future.set_result(result)
                    
        except Exception as e:
            success_count = 0
            failed_count = len(futures)
            errors = [e] * len(futures)
            
            for future in futures:
                if not future.done():
                    future.set_exception(e)
                    
        end_time = time.time()
        duration = end_time - start_time
        
        self._statistics.total_success_count += success_count
        self._statistics.total_failed_count += failed_count
        self._statistics.total_duration += duration
        self._total_items_processed += len(items)
        
        self._update_statistics()
        
    def _update_statistics(self) -&gt; None:
        """更新统计信息"""
        if self._statistics.total_operations &gt; 0:
            self._statistics.average_batch_size = (
                self._statistics.total_items / self._statistics.total_operations
            )
            self._statistics.average_duration_per_item = (
                self._statistics.total_duration / self._statistics.total_items
            )
            
        elapsed = time.time() - self._start_time
        if elapsed &gt; 0:
            self._statistics.operations_per_second = (
                self._statistics.total_operations / elapsed
            )
            self._statistics.items_per_second = (
                self._statistics.total_items / elapsed
            )
            
    def get_statistics(self) -&gt; BatchStatistics:
        """获取统计信息"""
        return self._statistics
        
    def get_current_batch_sizes(self) -&gt; Dict[OperationType, int]:
        """获取当前各批次大小"""
        return {
            op_type: len(items)
            for op_type, items in self._current_batch.items()
        }


class OperationMerger(Generic[T]):
    """
    操作合并器 - 合并重复或类似的操作
    """
    
    def __init__(self):
        self._merge_queues: Dict[str, List[T]] = defaultdict(list)
        self._operation_timestamps: Dict[str, float] = {}
        
    def add_operation(
        self,
        operation_key: str,
        item: T,
        merge_window_seconds: float = 0.5
    ) -&gt; Optional[List[T]]:
        """
        添加操作，如果在合并窗口内，合并到现有批次
        返回完整批次如果应该执行
        """
        current_time = time.time()
        
        if operation_key not in self._merge_queues:
            self._merge_queues[operation_key] = [item]
            self._operation_timestamps[operation_key] = current_time
            return None
            
        last_timestamp = self._operation_timestamps.get(operation_key, 0)
        
        if current_time - last_timestamp &lt; merge_window_seconds:
            self._merge_queues[operation_key].append(item)
            return None
        else:
            batch = self._merge_queues.pop(operation_key, [])
            self._operation_timestamps[operation_key] = current_time
            self._merge_queues[operation_key] = [item]
            return batch if batch else None
            
    def flush_all(self) -&gt; Dict[str, List[T]]:
        """刷新所有待合并的操作"""
        result = {**self._merge_queues}
        self._merge_queues.clear()
        self._operation_timestamps.clear()
        return result


def batch_operation(
    manager: BatchOperationManager,
    operation_type: OperationType
):
    """
    批量操作装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator


class ParallelBatchProcessor:
    """
    并行批量处理器 - 使用多线程并行处理多个批次
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        
    async def process_batches_parallel(
        self,
        batches: List[List[T]],
        processor: Callable[[List[T]], Awaitable[List[R]]]
    ) -&gt; List[List[R]]:
        """并行处理多个批次"""
        tasks = [processor(batch) for batch in batches]
        return await asyncio.gather(*tasks)


async def demo_batch_operations() -&gt; None:
    """
    演示批量操作
    """
    
    async def sample_handler(items: List[Dict[str, Any]]) -&gt; List[Dict[str, Any]]:
        """示例处理器"""
        await asyncio.sleep(0.01)
        return [{"processed": item, "success": True} for item in items]
        
    policy = BatchingPolicy(
        max_batch_size=10,
        max_wait_seconds=0.1,
        strategy=BatchStrategy.ADAPTIVE
    )
    
    manager = BatchOperationManager(policy, sample_handler)
    await manager.start()
    
    print("=== 演示批量操作 ===")
    
    results = []
    for i in range(25):
        item = {"id": i, "data": f"item_{i}"}
        result = await manager.submit(OperationType.INSERT, item)
        results.append(result)
        
    await manager.flush()
    
    print(f"处理了 {len(results)} 个项目")
    
    stats = manager.get_statistics()
    print(f"总操作: {stats.total_operations}")
    print(f"平均批次大小: {stats.average_batch_size:.2f}")
    print(f"吞吐量: {stats.items_per_second:.2f} 项/秒")
    
    await manager.shutdown()

