"""
日志配置模块 - 使用 Structlog 实现产品级结构化日志

该模块负责：
- 结构化日志配置
- 日志格式控制
- 日志输出管理
- 日志轮转设置
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import structlog
from .config_manager import get_application_settings, ApplicationSettings


def setup_structured_logging() -> None:
    """
    配置结构化日志系统

    该函数初始化全局的结构化日志系统，支持：
    - 控制台彩色输出（开发环境）
    - JSON格式输出（生产环境）
    - 文件输出和轮转
    - 结构化字段绑定

    Example:
        >>> setup_structured_logging()
        >>> logger = get_structured_logger(__name__)
        >>> logger.info("user_action", user_id=123, action="login")
    """
    settings = get_application_settings()

    # 配置标准库 logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # 定义日志处理器链
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # 根据环境选择输出格式
    if settings.environment == "production":
        # 生产环境：JSON格式，便于日志收集和分析
        processors.append(structlog.processors.JSONRenderer())
    else:
        # 开发环境：彩色控制台输出
        processors.append(structlog.dev.ConsoleRenderer())

    # 配置 structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置文件日志（如果配置了）
    if settings.log_file_path:
        _setup_file_handler(settings)


def _setup_file_handler(settings: ApplicationSettings) -> None:
    """
    配置文件日志处理器

    Args:
        settings: 应用程序配置
    """
    if not settings.log_file_path:
        return

    # 确保日志目录存在
    settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # 使用 RotatingFileHandler 实现日志轮转
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(
        filename=str(settings.log_file_path),
        maxBytes=settings.log_file_rotation_max_bytes,
        backupCount=settings.log_file_backup_count,
        encoding="utf-8",
    )

    # 设置文件日志格式为JSON（便于后续分析）
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
    )

    logging.getLogger().addHandler(file_handler)


def get_structured_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    获取结构化日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        structlog.stdlib.BoundLogger: 结构化日志记录器

    Example:
        >>> logger = get_structured_logger(__name__)
        >>> logger.info("task_completed", task_id="123", duration=1.5)
    """
    return structlog.get_logger(name)


class LogContext:
    """
    日志上下文管理器

    用于在代码块中绑定上下文信息到日志

    Example:
        >>> logger = get_structured_logger(__name__)
        >>> with LogContext(logger, request_id="123", user_id="456"):
        ...     logger.info("processing_request")
        ...     # 所有日志都会包含 request_id 和 user_id
    """

    def __init__(
        self,
        logger: structlog.stdlib.BoundLogger,
        **context
    ):
        self.logger = logger
        self.context = context
        self.bound_logger = None

    def __enter__(self):
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理上下文（可选）
        pass
