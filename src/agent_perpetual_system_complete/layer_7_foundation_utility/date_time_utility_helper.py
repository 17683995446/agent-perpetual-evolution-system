"""
Date Time Utility Helper - 日期时间工具助手（4个单词）

提供各种日期时间相关的工具函数和辅助方法。
文件名包含4个单词，非常清晰明了。
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any


class DateTimeUtilityHelper:
    """
    日期时间工具助手类

    提供日期时间格式化、解析、计算等功能。
    """

    @staticmethod
    def get_current_timestamp_seconds() -> float:
        """
        获取当前时间戳（秒）

        返回从 epoch 开始的秒数，包含小数。
        """
        return time.time()

    @staticmethod
    def get_current_timestamp_milliseconds() -> int:
        """
        获取当前时间戳（毫秒）

        返回从 epoch 开始的毫秒数，整数。
        """
        return int(time.time() * 1000)

    @staticmethod
    def get_current_datetime_object() -> datetime:
        """
        获取当前日期时间对象

        返回本地时区的 datetime 对象。
        """
        return datetime.now()

    @staticmethod
    def get_current_datetime_iso_format() -> str:
        """
        获取当前日期时间的 ISO 格式字符串

        返回格式为 "YYYY-MM-DDTHH:MM:SS.ffffff" 的字符串。
        """
        return datetime.now().isoformat()

    @staticmethod
    def format_datetime_readable(
        dt: Optional[datetime] = None,
        format_pattern: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """
        格式化日期时间为可读字符串

        参数:
            dt: 要格式化的日期时间对象，如果为 None 则使用当前时间
            format_pattern: 格式化模式字符串

        返回:
            格式化后的日期时间字符串
        """
        target_dt = dt or datetime.now()
        return target_dt.strftime(format_pattern)

    @staticmethod
    def parse_datetime_from_string(
        datetime_str: str,
        format_pattern: Optional[str] = None
    ) -> datetime:
        """
        从字符串解析日期时间

        参数:
            datetime_str: 日期时间字符串
            format_pattern: 格式化模式，如果为 None 则尝试自动解析

        返回:
            解析后的 datetime 对象
        """
        if format_pattern:
            return datetime.strptime(datetime_str, format_pattern)
        return datetime.fromisoformat(datetime_str)

    @staticmethod
    def add_seconds_to_datetime(dt: datetime, seconds: float) -> datetime:
        """
        给日期时间增加指定秒数

        参数:
            dt: 起始日期时间
            seconds: 要增加的秒数

        返回:
            增加后的日期时间对象
        """
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def add_days_to_datetime(dt: datetime, days: int) -> datetime:
        """
        给日期时间增加指定天数

        参数:
            dt: 起始日期时间
            days: 要增加的天数

        返回:
            增加后的日期时间对象
        """
        return dt + timedelta(days=days)

    @staticmethod
    def calculate_time_difference_seconds(dt1: datetime, dt2: datetime) -> float:
        """
        计算两个日期时间之间的差值（秒）

        参数:
            dt1: 第一个日期时间
            dt2: 第二个日期时间

        返回:
            dt2 - dt1 的秒数差值
        """
        time_delta = dt2 - dt1
        return time_delta.total_seconds()

    @staticmethod
    def get_datetime_days_ago(days: int) -> datetime:
        """
        获取指定天数前的日期时间

        参数:
            days: 天数

        返回:
            指定天数前的日期时间对象
        """
        return datetime.now() - timedelta(days=days)


class TimerContextManager:
    """
    计时器上下文管理器类

    用于测量代码块执行时间。
    """

    def __init__(self, auto_log: bool = False):
        """
        初始化计时器

        参数:
            auto_log: 是否自动记录日志
        """
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None
        self.auto_log = auto_log

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return False

    def get_elapsed_milliseconds(self) -> float:
        """
        获取经过的毫秒数

        返回:
            经过的毫秒数
        """
        if self.elapsed_time is not None:
            return self.elapsed_time * 1000
        return 0.0
