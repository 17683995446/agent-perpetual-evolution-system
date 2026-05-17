"""
ID生成器模块

提供各种唯一ID的生成功能
"""

import uuid
from datetime import datetime
from typing import Optional


class IDGenerator:
    """
    ID生成器类

    提供多种ID生成策略：
    - UUID格式（默认）
    - 时间戳格式
    - 自定义前缀格式
    """

    @staticmethod
    def generate_uuid() -> str:
        """
        生成UUID格式的ID

        Returns:
            str: UUID格式的ID

        Example:
            >>> task_id = IDGenerator.generate_uuid()
            # 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_task_id() -> str:
        """
        生成任务ID

        Returns:
            str: 格式为 'task_xxxxxxxxxxxxxxxx' 的ID

        Example:
            >>> task_id = IDGenerator.generate_task_id()
            # 'task_a1b2c3d4e5f67890'
        """
        unique_id = uuid.uuid4().hex[:16]
        return f"task_{unique_id}"

    @staticmethod
    def generate_memory_id() -> str:
        """
        生成记忆ID

        Returns:
            str: 格式为 'mem_xxxxxxxxxxxxxxxx' 的ID
        """
        unique_id = uuid.uuid4().hex[:16]
        return f"mem_{unique_id}"

    @staticmethod
    def generate_strategy_id() -> str:
        """
        生成策略ID

        Returns:
            str: 格式为 'strategy_xxxxxxxxxxxxxxxx' 的ID
        """
        unique_id = uuid.uuid4().hex[:16]
        return f"strategy_{unique_id}"

    @staticmethod
    def generate_knowledge_id() -> str:
        """
        生成知识ID

        Returns:
            str: 格式为 'knowledge_xxxxxxxxxxxxxxxx' 的ID
        """
        unique_id = uuid.uuid4().hex[:16]
        return f"knowledge_{unique_id}"

    @staticmethod
    def generate_log_id() -> str:
        """
        生成日志ID

        Returns:
            str: 格式为 'log_xxxxxxxxxxxxxxxx' 的ID
        """
        unique_id = uuid.uuid4().hex[:16]
        return f"log_{unique_id}"

    @staticmethod
    def generate_timestamp_id(prefix: Optional[str] = None) -> str:
        """
        生成时间戳格式的ID

        Args:
            prefix: ID前缀

        Returns:
            str: 格式为 '{prefix}_{timestamp}' 的ID

        Example:
            >>> task_id = IDGenerator.generate_timestamp_id('task')
            # 'task_20240101123456789'
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        if prefix:
            return f"{prefix}_{timestamp}"
        return str(timestamp)
