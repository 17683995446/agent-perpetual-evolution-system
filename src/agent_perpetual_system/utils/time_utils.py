"""
时间工具模块

提供时间相关的工具函数
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class TimeUtils:
    """
    时间工具类

    提供各种时间相关的工具方法
    """

    @staticmethod
    def get_current_timestamp() -> float:
        """
        获取当前时间戳（秒）

        Returns:
            float: 当前时间戳

        Example:
            >>> timestamp = TimeUtils.get_current_timestamp()
            # 1704067200.123
        """
        return time.time()

    @staticmethod
    def get_current_timestamp_ms() -> int:
        """
        获取当前时间戳（毫秒）

        Returns:
            int: 当前时间戳（毫秒）

        Example:
            >>> timestamp_ms = TimeUtils.get_current_timestamp_ms()
            # 1704067200123
        """
        return int(time.time() * 1000)

    @staticmethod
    def get_current_datetime() -> datetime:
        """
        获取当前日期时间

        Returns:
            datetime: 当前日期时间对象

        Example:
            >>> dt = TimeUtils.get_current_datetime()
            # 2024-01-01 12:00:00.000000
        """
        return datetime.now()

    @staticmethod
    def get_current_datetime_iso() -> str:
        """
        获取当前日期时间的ISO格式字符串

        Returns:
            str: ISO格式的时间字符串

        Example:
            >>> iso_str = TimeUtils.get_current_datetime_iso()
            # '2024-01-01T12:00:00.000000'
        """
        return datetime.now().isoformat()

    @staticmethod
    def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        格式化日期时间

        Args:
            dt: 日期时间对象
            fmt: 格式字符串

        Returns:
            str: 格式化后的时间字符串

        Example:
            >>> dt = datetime.now()
            >>> formatted = TimeUtils.format_datetime(dt)
            # '2024-01-01 12:00:00'
        """
        return dt.strftime(fmt)

    @staticmethod
    def parse_datetime(dt_str: str, fmt: Optional[str] = None) -> datetime:
        """
        解析日期时间字符串

        Args:
            dt_str: 日期时间字符串
            fmt: 格式字符串（如果为None，则尝试自动解析）

        Returns:
            datetime: 日期时间对象

        Example:
            >>> dt = TimeUtils.parse_datetime('2024-01-01 12:00:00')
        """
        if fmt:
            return datetime.strptime(dt_str, fmt)
        # 尝试ISO格式
        return datetime.fromisoformat(dt_str)

    @staticmethod
    def add_seconds(dt: datetime, seconds: float) -> datetime:
        """
        日期时间加秒数

        Args:
            dt: 起始日期时间
            seconds: 要添加的秒数

        Returns:
            datetime: 新的日期时间

        Example:
            >>> dt = datetime.now()
            >>> new_dt = TimeUtils.add_seconds(dt, 60)
        """
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def get_days_ago(days: int) -> datetime:
        """
        获取N天前的日期时间

        Args:
            days: 天数

        Returns:
            datetime: N天前的日期时间

        Example:
            >>> week_ago = TimeUtils.get_days_ago(7)
        """
        return datetime.now() - timedelta(days=days)


class Timer:
    """
    计时器上下文管理器

    用于测量代码执行时间

    Example:
        >>> with Timer() as timer:
        ...     # 执行耗时操作
        ...     pass
        >>> print(f"耗时: {timer.elapsed_time}s")
    """

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return False
