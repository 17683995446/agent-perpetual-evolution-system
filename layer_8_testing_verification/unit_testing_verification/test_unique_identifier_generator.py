"""
Test Unique Identifier Generator - 测试唯一标识符生成器（5个单词）

测试唯一标识符生成器的功能。
文件名包含5个单词，非常清晰明了。
"""

import pytest
from src.agent_perpetual_system_complete.layer_7_foundation_utility.unique_identifier_generator import (
    UniqueIdentifierGenerator
)


class TestUniqueIdentifierGenerator:
    """
    唯一标识符生成器测试类
    """

    def test_generate_random_uuid_string_returns_valid_uuid(self):
        """
        测试生成随机UUID字符串
        """
        uuid_str = UniqueIdentifierGenerator.generate_random_uuid_string()
        assert len(uuid_str) == 36
        assert '-' in uuid_str

    def test_generate_task_identifier_with_prefix(self):
        """
        测试生成带前缀的任务ID
        """
        task_id = UniqueIdentifierGenerator.generate_task_identifier_with_prefix()
        assert task_id.startswith('task_')
        assert len(task_id) > 5

    def test_generate_memory_identifier_with_prefix(self):
        """
        测试生成带前缀的记忆ID
        """
        memory_id = UniqueIdentifierGenerator.generate_memory_identifier_with_prefix()
        assert memory_id.startswith('memory_')
        assert len(memory_id) > 5

    def test_generate_short_random_string_default_length(self):
        """
        测试生成默认长度的随机字符串
        """
        random_str = UniqueIdentifierGenerator.generate_short_random_string()
        assert len(random_str) == 12

    def test_generate_short_random_string_custom_length(self):
        """
        测试生成长度的随机字符串
        """
        random_str = UniqueIdentifierGenerator.generate_short_random_string(length=20)
        assert len(random_str) == 20

    def test_generate_timestamp_identifier(self):
        """
        测试生成时间戳标识符
        """
        timestamp_id = UniqueIdentifierGenerator.generate_timestamp_identifier()
        assert '_' in timestamp_id

    def test_generate_timestamp_identifier_with_prefix(self):
        """
        测试生成带前缀的时间戳标识符
        """
        custom_prefix = 'custom_test'
        timestamp_id = UniqueIdentifierGenerator.generate_timestamp_identifier(prefix=custom_prefix)
        assert timestamp_id.startswith(f'{custom_prefix}_')

    def test_generate_multiple_identifiers_are_unique(self):
        """
        测试生成的多个标识符都是唯一的
        """
        identifiers = set()
        for _ in range(100):
            task_id = UniqueIdentifierGenerator.generate_task_identifier_with_prefix()
            identifiers.add(task_id)

        assert len(identifiers) == 100
