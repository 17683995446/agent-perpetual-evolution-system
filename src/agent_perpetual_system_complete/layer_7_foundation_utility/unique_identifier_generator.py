"""
Unique Identifier Generator - 唯一标识符生成器（4个单词）

负责生成各类唯一标识符，包括任务ID、记忆ID、策略ID等。
文件名包含4个单词，非常清晰明了。
"""

import uuid
import secrets
import string
from typing import Optional
from datetime import datetime


class UniqueIdentifierGenerator:
    """
    唯一标识符生成器类

    提供多种唯一标识符生成策略：
    - UUID格式
    - 自定义前缀格式
    - 时间戳格式
    - 随机字符串格式
    """

    @staticmethod
    def generate_random_uuid_string() -> str:
        """
        生成随机UUID字符串

        返回标准的UUID v4字符串。
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_task_identifier_with_prefix() -> str:
        """
        生成带前缀的任务标识符

        返回格式为 "task_xxxxxxxxxxxxxxxx" 的任务ID。
        """
        unique_suffix = uuid.uuid4().hex[:16]
        return f"task_{unique_suffix}"

    @staticmethod
    def generate_memory_identifier_with_prefix() -> str:
        """
        生成带前缀的记忆标识符

        返回格式为 "memory_xxxxxxxxxxxxxxxx" 的记忆ID。
        """
        unique_suffix = uuid.uuid4().hex[:16]
        return f"memory_{unique_suffix}"

    @staticmethod
    def generate_strategy_identifier_with_prefix() -> str:
        """
        生成带前缀的策略标识符

        返回格式为 "strategy_xxxxxxxxxxxxxxxx" 的策略ID。
        """
        unique_suffix = uuid.uuid4().hex[:16]
        return f"strategy_{unique_suffix}"

    @staticmethod
    def generate_knowledge_identifier_with_prefix() -> str:
        """
        生成带前缀的知识标识符

        返回格式为 "knowledge_xxxxxxxxxxxxxxxx" 的知识ID。
        """
        unique_suffix = uuid.uuid4().hex[:16]
        return f"knowledge_{unique_suffix}"

    @staticmethod
    def generate_short_random_string(length: int = 12) -> str:
        """
        生成指定长度的随机字符串

        参数:
            length: 生成字符串的长度，默认为12

        返回:
            包含字母和数字的随机字符串
        """
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def generate_timestamp_identifier(prefix: Optional[str] = None) -> str:
        """
        生成基于时间戳的标识符

        参数:
            prefix: 可选的前缀字符串

        返回:
            包含时间戳的唯一标识符
        """
        timestamp = int(datetime.now().timestamp() * 1000000)
        random_part = secrets.token_hex(4)

        if prefix:
            return f"{prefix}_{timestamp}_{random_part}"
        return f"time_{timestamp}_{random_part}"
