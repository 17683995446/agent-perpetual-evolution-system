"""
String Manipulation Utility - 字符串处理工具（4个单词）

提供各种字符串处理和操作的工具函数。
文件名包含4个单词，非常清晰明了。
"""

import re
from typing import Optional, List, Dict, Any


class StringManipulationUtility:
    """
    字符串处理工具类

    提供字符串清洗、格式化、验证、转换等功能。
    """

    @staticmethod
    def clean_whitespace_from_string(input_string: str) -> str:
        """
        清洗字符串中的空白字符

        参数:
            input_string: 输入的原始字符串

        返回:
            清洗后的字符串，包含正常的单词间距
        """
        cleaned = re.sub(r'\s+', ' ', input_string.strip())
        return cleaned

    @staticmethod
    def convert_string_to_snake_case(input_string: str) -> str:
        """
        将字符串转换为 snake_case 格式

        参数:
            input_string: 输入的字符串（支持 PascalCase、camelCase、kebab-case）

        返回:
            snake_case 格式的字符串
        """
        # 先替换驼峰命名为下划线分隔
        temp_str = re.sub(r'(?<!^)(?=[A-Z])', '_', input_string)
        # 替换连字符为下划线
        temp_str = temp_str.replace('-', '_')
        # 转换为小写并合并连续下划线
        return re.sub(r'_+', '_', temp_str.lower()).strip('_')

    @staticmethod
    def convert_string_to_camel_case(input_string: str) -> str:
        """
        将字符串转换为 camelCase 格式

        参数:
            input_string: 输入的字符串

        返回:
            camelCase 格式的字符串
        """
        words = re.split(r'[_\- ]', input_string)
        if not words:
            return ''

        first_word = words[0].lower()
        other_words = [word.capitalize() for word in words[1:] if word]
        return first_word + ''.join(other_words)

    @staticmethod
    def truncate_long_string(input_string: str, max_length: int, suffix: str = '...') -> str:
        """
        截断过长的字符串

        参数:
            input_string: 输入的字符串
            max_length: 最大长度
            suffix: 截断后的后缀字符串

        返回:
            截断后的字符串
        """
        if len(input_string) <= max_length:
            return input_string

        truncated_length = max_length - len(suffix)
        if truncated_length <= 0:
            return suffix

        return input_string[:truncated_length] + suffix

    @staticmethod
    def validate_email_format(email_string: str) -> bool:
        """
        验证电子邮件格式

        参数:
            email_string: 要验证的电子邮件字符串

        返回:
            如果格式有效返回 True，否则返回 False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_string))

    @staticmethod
    def extract_digits_from_string(input_string: str) -> str:
        """
        从字符串中提取数字字符

        参数:
            input_string: 输入的字符串

        返回:
            只包含数字的字符串
        """
        return ''.join(char for char in input_string if char.isdigit())

    @staticmethod
    def extract_alphabetic_chars(input_string: str) -> str:
        """
        从字符串中提取字母字符

        参数:
            input_string: 输入的字符串

        返回:
            只包含字母的字符串
        """
        return ''.join(char for char in input_string if char.isalpha())

    @staticmethod
    def count_occurrences_in_string(input_string: str, search_substring: str) -> int:
        """
        统计子字符串在输入字符串中的出现次数

        参数:
            input_string: 输入的字符串
            search_substring: 要搜索的子字符串

        返回:
            出现的次数
        """
        return input_string.count(search_substring)

    @staticmethod
    def replace_multiple_substrings(
        input_string: str,
        replacements: Dict[str, str]
    ) -> str:
        """
        批量替换多个子字符串

        参数:
            input_string: 输入的字符串
            replacements: 替换映射字典 {原字符串: 新字符串}

        返回:
            替换后的字符串
        """
        result = input_string
        for old_substring, new_substring in replacements.items():
            result = result.replace(old_substring, new_substring)
        return result

    @staticmethod
    def pad_string_with_characters(
        input_string: str,
        total_length: int,
        pad_character: str = ' ',
        pad_left: bool = False
    ) -> str:
        """
        用字符填充字符串到指定长度

        参数:
            input_string: 输入的字符串
            total_length: 目标总长度
            pad_character: 填充字符
            pad_left: 是否在左边填充（默认右边）

        返回:
            填充后的字符串
        """
        if len(input_string) >= total_length:
            return input_string

        pad_length = total_length - len(input_string)
        padding = pad_character * pad_length

        if pad_left:
            return padding + input_string
        return input_string + padding
