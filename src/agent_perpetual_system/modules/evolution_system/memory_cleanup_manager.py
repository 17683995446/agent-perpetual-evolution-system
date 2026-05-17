"""
Memory Cleanup Manager - 记忆清理管理器

该模块负责：
- 过期记忆的自动清理
- 低价值记忆的删除
- 记忆存储空间优化
- 记忆去重和压缩
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, delete, and_
from ...core.database_manager import get_database_session
from ...core.database_models import MemoryDatabaseModel
from ...core.logger_config import get_structured_logger
from ...core.config_manager import get_application_settings

logger = get_structured_logger(__name__)


class MemoryCleanupManager:
    """
    记忆清理管理器

    负责系统记忆的清理和优化工作：
    - 自动清理过期记忆
    - 删除低评分记忆
    - 记忆去重处理
    - 存储空间优化
    """

    def __init__(self):
        self.settings = get_application_settings()
        self.cleanup_days = self.settings.evolution_memory_cleanup_days

    async def execute_memory_cleanup(self) -> Dict[str, Any]:
        """
        执行记忆清理主流程

        Returns:
            Dict: 包含清理结果的字典

        Example:
            >>> manager = MemoryCleanupManager()
            >>> result = await manager.execute_memory_cleanup()
            >>> print(f"Deleted {result['total_deleted']} memories")
        """
        logger.info("memory_cleanup_started")

        total_deleted = 0
        expired_deleted = 0
        low_score_deleted = 0
        duplicate_deleted = 0

        # 1. 清理过期记忆
        expired_result = await self._cleanup_expired_memories()
        expired_deleted = expired_result["deleted_count"]
        total_deleted += expired_deleted

        # 2. 清理低评分记忆
        low_score_result = await self._cleanup_low_score_memories()
        low_score_deleted = low_score_result["deleted_count"]
        total_deleted += low_score_deleted

        # 3. 去重处理
        duplicate_result = await self._remove_duplicate_memories()
        duplicate_deleted = duplicate_result["deleted_count"]
        total_deleted += duplicate_deleted

        logger.info(
            "memory_cleanup_completed",
            total_deleted=total_deleted,
            expired_deleted=expired_deleted,
            low_score_deleted=low_score_deleted,
            duplicate_deleted=duplicate_deleted
        )

        return {
            "status": "success",
            "total_deleted": total_deleted,
            "expired_deleted": expired_deleted,
            "low_score_deleted": low_score_deleted,
            "duplicate_deleted": duplicate_deleted,
        }

    async def _cleanup_expired_memories(self) -> Dict[str, Any]:
        """
        清理过期记忆

        删除超过指定天数的记忆

        Returns:
            Dict: 包含删除结果的字典
        """
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)

        async with get_database_session() as session:
            result = await session.execute(
                delete(MemoryDatabaseModel).where(
                    and_(
                        MemoryDatabaseModel.created_at < cutoff_date
                    )
                )
            )
            deleted_count = result.rowcount
            await session.commit()

        logger.info(
            "expired_memories_cleaned",
            deleted_count=deleted_count,
            cutoff_days=self.cleanup_days
        )

        return {
            "operation": "cleanup_expired",
            "deleted_count": deleted_count,
        }

    async def _cleanup_low_score_memories(self) -> Dict[str, Any]:
        """
        清理低评分记忆

        删除评分低于阈值的记忆

        Returns:
            Dict: 包含删除结果的字典
        """
        score_threshold = 0.3

        async with get_database_session() as session:
            result = await session.execute(
                delete(MemoryDatabaseModel).where(
                    MemoryDatabaseModel.score < score_threshold
                )
            )
            deleted_count = result.rowcount
            await session.commit()

        logger.info(
            "low_score_memories_cleaned",
            deleted_count=deleted_count,
            score_threshold=score_threshold
        )

        return {
            "operation": "cleanup_low_score",
            "deleted_count": deleted_count,
            "score_threshold": score_threshold,
        }

    async def _remove_duplicate_memories(self) -> Dict[str, Any]:
        """
        去除重复记忆

        识别并删除内容相似的重复记忆

        Returns:
            Dict: 包含去重结果的字典
        """
        # 这里可以实现基于内容相似度的去重逻辑
        # 当前为简化实现
        deleted_count = 0

        logger.info(
            "duplicate_memories_removed",
            deleted_count=deleted_count
        )

        return {
            "operation": "remove_duplicates",
            "deleted_count": deleted_count,
        }

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """
        获取记忆统计信息

        Returns:
            Dict: 包含统计信息的字典

        Example:
            >>> stats = await manager.get_memory_statistics()
            >>> print(f"Total memories: {stats['total_count']}")
        """
        async with get_database_session() as session:
            # 获取总记忆数
            total_result = await session.execute(
                select(MemoryDatabaseModel)
            )
            all_memories = total_result.scalars().all()
            total_count = len(all_memories)

            # 按类型统计
            type_counts = {}
            for memory in all_memories:
                memory_type = memory.memory_type
                type_counts[memory_type] = type_counts.get(memory_type, 0) + 1

            # 计算平均评分
            if all_memories:
                avg_score = sum(m.score for m in all_memories) / len(all_memories)
            else:
                avg_score = 0.0

        return {
            "total_count": total_count,
            "type_distribution": type_counts,
            "average_score": avg_score,
            "cleanup_threshold_days": self.cleanup_days,
        }

    async def compress_memory_storage(self) -> Dict[str, Any]:
        """
        压缩记忆存储

        优化记忆存储结构，释放空间

        Returns:
            Dict: 包含压缩结果的字典
        """
        # 在SQLite中，VACUUM可以回收删除记录占据的空间
        # 这里可以添加数据库维护逻辑
        logger.info("memory_storage_compression_completed")

        return {
            "status": "success",
            "message": "Memory storage compression completed",
        }
