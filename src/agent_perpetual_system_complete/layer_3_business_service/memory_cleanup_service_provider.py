"""
Memory Cleanup Service Provider - 内存清理服务提供者（6个单词）

负责冷热数据分离、自动清理策略、内存使用监控。
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import get_structured_logger


class DataTemperature(str, Enum):
    """
    数据温度枚举
    """
    HOT = "hot"          # 热数据 - 最近访问
    WARM = "warm"        # 温数据 - 近期访问
    COLD = "cold"        # 冷数据 - 长时间未访问
    FROZEN = "frozen"    # 冻结数据 - 几乎不访问


class CleanupAction(str, Enum):
    """
    清理动作枚举
    """
    ARCHIVE = "archive"   # 归档
    COMPRESS = "compress" # 压缩
    DELETE = "delete"     # 删除
    EVICT = "evict"       # 逐出


@dataclass
class MemoryUsageStats:
    """
    内存使用统计
    """
    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_percent: float
    hot_data_bytes: int = 0
    warm_data_bytes: int = 0
    cold_data_bytes: int = 0
    frozen_data_bytes: int = 0


@dataclass
class DataEntry:
    """
    数据条目
    """
    key: str
    value: Any
    temperature: DataTemperature
    created_at: datetime
    last_accessed_at: datetime
    access_count: int
    size_bytes: int


@dataclass
class CleanupPolicy:
    """
    清理策略
    """
    name: str
    threshold_percent: float  # 触发清理的阈值百分比
    hot_to_warm_seconds: int = 3600  # 1小时转温
    warm_to_cold_seconds: int = 86400  # 24小时转冷
    cold_to_frozen_seconds: int = 604800  # 7天转冻结
    frozen_retention_seconds: int = 2592000  # 30天后归档/删除
    default_action: CleanupAction = CleanupAction.ARCHIVE


class MemoryCleanupServiceProvider:
    """
    内存清理服务提供者

    核心职责：
    1. 冷热数据分离和分类
    2. 自动清理策略执行
    3. 内存使用监控和告警
    4. 数据温度管理和演化
    """

    def __init__(
        self,
        policies: Optional[List[CleanupPolicy]] = None,
        max_memory_bytes: Optional[int] = None,
    ):
        self.logger = get_structured_logger(__name__)

        self._data_store: Dict[str, DataEntry] = {}
        self._policies = policies or self._get_default_policies()
        self._max_memory_bytes = max_memory_bytes or (1024 * 1024 * 1024)  # 默认 1GB
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._cleanup_history: List[Dict[str, Any]] = []
        self._temperature_transitions: defaultdict = defaultdict(int)

    async def start(self, interval_seconds: int = 300) -> None:
        """
        启动内存清理服务

        Args:
            interval_seconds: 清理检查间隔，默认5分钟
        """
        if self._is_running:
            self.logger.warning("memory_cleanup_service_already_running")
            return

        self.logger.info(
            "starting_memory_cleanup_service",
            interval_seconds=interval_seconds,
            max_memory_bytes=self._max_memory_bytes,
        )

        self._is_running = True
        self._cleanup_task = asyncio.create_task(
            self._cleanup_loop(interval_seconds)
        )

        self.logger.info("memory_cleanup_service_started")

    async def stop(self) -> None:
        """
        停止内存清理服务
        """
        if not self._is_running:
            self.logger.warning("memory_cleanup_service_not_running")
            return

        self.logger.info("stopping_memory_cleanup_service")
        self._is_running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self.logger.info("memory_cleanup_service_stopped")

    async def store_data(self, key: str, value: Any) -> None:
        """
        存储数据

        Args:
            key: 数据键
            value: 数据值
        """
        now = datetime.utcnow()

        entry = DataEntry(
            key=key,
            value=value,
            temperature=DataTemperature.HOT,
            created_at=now,
            last_accessed_at=now,
            access_count=1,
            size_bytes=self._calculate_size(value),
        )

        self._data_store[key] = entry

        self.logger.debug("data_stored", key=key, size_bytes=entry.size_bytes)

    async def retrieve_data(self, key: str) -> Optional[Any]:
        """
        检索数据

        Args:
            key: 数据键

        Returns:
            数据值，如果不存在则返回 None
        """
        if key not in self._data_store:
            return None

        entry = self._data_store[key]
        entry.last_accessed_at = datetime.utcnow()
        entry.access_count += 1

        # 提升数据温度
        await self._promote_temperature(key)

        return entry.value

    async def get_memory_stats(self) -> MemoryUsageStats:
        """
        获取内存使用统计

        Returns:
            内存使用统计
        """
        total_used = sum(entry.size_bytes for entry in self._data_store.values())

        hot = sum(e.size_bytes for e in self._data_store.values() if e.temperature == DataTemperature.HOT)
        warm = sum(e.size_bytes for e in self._data_store.values() if e.temperature == DataTemperature.WARM)
        cold = sum(e.size_bytes for e in self._data_store.values() if e.temperature == DataTemperature.COLD)
        frozen = sum(e.size_bytes for e in self._data_store.values() if e.temperature == DataTemperature.FROZEN)

        used_percent = (total_used / self._max_memory_bytes) * 100

        return MemoryUsageStats(
            total_bytes=self._max_memory_bytes,
            used_bytes=total_used,
            free_bytes=self._max_memory_bytes - total_used,
            used_percent=used_percent,
            hot_data_bytes=hot,
            warm_data_bytes=warm,
            cold_data_bytes=cold,
            frozen_data_bytes=frozen,
        )

    async def force_cleanup(self) -> Dict[str, Any]:
        """
        强制清理

        Returns:
            清理结果
        """
        self.logger.info("forcing_memory_cleanup")
        result = await self._execute_cleanup()
        self.logger.info("forced_cleanup_complete", result=result)
        return result

    async def _cleanup_loop(self, interval_seconds: int) -> None:
        """
        清理循环

        Args:
            interval_seconds: 检查间隔
        """
        self.logger.info("cleanup_loop_started")

        while self._is_running:
            try:
                await asyncio.sleep(interval_seconds)

                stats = await self.get_memory_stats()

                self.logger.debug(
                    "memory_check",
                    used_percent=stats.used_percent,
                    hot=stats.hot_data_bytes,
                    warm=stats.warm_data_bytes,
                    cold=stats.cold_data_bytes,
                    frozen=stats.frozen_data_bytes,
                )

                # 检查是否需要清理
                for policy in self._policies:
                    if stats.used_percent >= policy.threshold_percent:
                        self.logger.info(
                            "memory_threshold_exceeded",
                            policy=policy.name,
                            threshold=policy.threshold_percent,
                            current=stats.used_percent,
                        )
                        await self._execute_cleanup(policy)
                        break

                # 更新数据温度
                await self._update_all_temperatures()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("cleanup_loop_error", error=str(e))

        self.logger.info("cleanup_loop_stopped")

    async def _execute_cleanup(self, policy: Optional[CleanupPolicy] = None) -> Dict[str, Any]:
        """
        执行清理

        Args:
            policy: 清理策略

        Returns:
            清理结果
        """
        policy = policy or self._policies[0]
        result = {
            "policy": policy.name,
            "timestamp": datetime.utcnow().isoformat(),
            "entries_removed": 0,
            "bytes_freed": 0,
        }

        # 优先清理冻结数据
        frozen_keys = [
            key for key, entry in self._data_store.items()
            if entry.temperature == DataTemperature.FROZEN
        ]

        for key in frozen_keys:
            entry = self._data_store[key]
            del self._data_store[key]
            result["entries_removed"] += 1
            result["bytes_freed"] += entry.size_bytes
            self._temperature_transitions["frozen_cleaned"] += 1

        # 然后清理冷数据
        cold_keys = [
            key for key, entry in self._data_store.items()
            if entry.temperature == DataTemperature.COLD
        ]

        for key in cold_keys:
            entry = self._data_store[key]
            del self._data_store[key]
            result["entries_removed"] += 1
            result["bytes_freed"] += entry.size_bytes
            self._temperature_transitions["cold_cleaned"] += 1

        self._cleanup_history.append(result)

        self.logger.info(
            "cleanup_executed",
            entries_removed=result["entries_removed"],
            bytes_freed=result["bytes_freed"],
        )

        return result

    async def _update_all_temperatures(self) -> None:
        """
        更新所有数据的温度
        """
        now = datetime.utcnow()

        for key, entry in list(self._data_store.items()):
            time_since_access = (now - entry.last_accessed_at).total_seconds()

            for policy in self._policies:
                if time_since_access >= policy.frozen_retention_seconds:
                    await self._downgrade_temperature(key, DataTemperature.FROZEN)
                elif time_since_access >= policy.cold_to_frozen_seconds:
                    await self._downgrade_temperature(key, DataTemperature.COLD)
                elif time_since_access >= policy.warm_to_cold_seconds:
                    await self._downgrade_temperature(key, DataTemperature.WARM)
                break

    async def _promote_temperature(self, key: str) -> None:
        """
        提升数据温度（热数据）

        Args:
            key: 数据键
        """
        if key not in self._data_store:
            return

        entry = self._data_store[key]
        old_temp = entry.temperature

        if old_temp != DataTemperature.HOT:
            entry.temperature = DataTemperature.HOT
            self._temperature_transitions[f"{old_temp}_to_hot"] += 1
            self.logger.debug("temperature_promoted", key=key, from_temp=old_temp, to_temp=DataTemperature.HOT)

    async def _downgrade_temperature(self, key: str, target_temp: DataTemperature) -> None:
        """
        降级数据温度

        Args:
            key: 数据键
            target_temp: 目标温度
        """
        if key not in self._data_store:
            return

        entry = self._data_store[key]
        old_temp = entry.temperature

        if old_temp != target_temp:
            entry.temperature = target_temp
            self._temperature_transitions[f"{old_temp}_to_{target_temp}"] += 1
            self.logger.debug("temperature_downgraded", key=key, from_temp=old_temp, to_temp=target_temp)

    def _calculate_size(self, value: Any) -> int:
        """
        计算值的大小（估算）

        Args:
            value: 值

        Returns:
            字节数
        """
        import sys
        try:
            return sys.getsizeof(value) + (sys.getsizeof(str(value)) if hasattr(value, "__str__") else 0)
        except Exception:
            return 1024  # 默认 1KB

    def _get_default_policies(self) -> List[CleanupPolicy]:
        """
        获取默认策略

        Returns:
            默认策略列表
        """
        return [
            CleanupPolicy(
                name="aggressive",
                threshold_percent=85.0,
            ),
            CleanupPolicy(
                name="normal",
                threshold_percent=75.0,
            ),
            CleanupPolicy(
                name="conservative",
                threshold_percent=60.0,
            ),
        ]

    @property
    def is_running(self) -> bool:
        """
        是否正在运行
        """
        return self._is_running

    @property
    def cleanup_history(self) -> List[Dict[str, Any]]:
        """
        清理历史
        """
        return self._cleanup_history.copy()
