"""
Structured Logging Abstraction - 结构化日志抽象（4个单词）

使用 structlog 提供产品级别的结构化日志系统，
支持控制台输出、文件输出、日志轮转等功能。
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

import structlog
from structlog import BoundLogger
from structlog.types import EventDict, Processor
from structlog.stdlib import ProcessorFormatter
from .configuration_settings_abstraction import (
    ApplicationConfiguration,
    get_configuration,
)


@dataclass
class LoggingConfiguration:
    """
    日志配置类
    """
    log_level: str = "INFO"
    log_file_path: Optional[Path] = None
    log_to_console: bool = True
    log_file_rotation_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_file_backup_count: int = 5
    enable_log_processors: bool = True


class StructuredLoggingManager:
    """
    结构化日志管理器
    提供完整的产品级别日志功能。
    """
    
    _instance: Optional['StructuredLoggingManager'] = None
    _initialized: bool = False
    
    def __new__(cls, *args: Any, **kwargs: Any) -> 'StructuredLoggingManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[LoggingConfiguration] = None) -> None:
        if not StructuredLoggingManager._initialized:
            self.config = config or self._load_config_from_app()
            self._setup_structlog()
            StructuredLoggingManager._initialized = True
    
    def _load_config_from_app(self) -> LoggingConfiguration:
        """
        从应用配置加载日志配置
        """
        app_config = get_configuration()
        return LoggingConfiguration(
            log_level=app_config.logging_level,
            log_file_path=Path(app_config.logging_file_path) if app_config.logging_file_path else None,
            log_to_console=app_config.logging_console_output,
            log_file_rotation_max_bytes=app_config.logging_rotation_max_bytes,
            log_file_backup_count=app_config.logging_backup_count,
        )
    
    def _setup_structlog(self) -> None:
        """
        配置 structlog
        """
        timestamper = structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
            key="timestamp",
        )
        
        shared_processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.add_log_level,
            timestamper,
        ]
        
        if self.config.enable_log_processors:
            shared_processors.extend([
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
            ])
        
        handlers: list[Any] = []
        
        if self.config.log_to_console:
            from rich.logging import RichHandler
            rich_handler = RichHandler(
                level=self.config.log_level,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
            )
            handlers.append(rich_handler)
        
        if self.config.log_file_path:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                filename=str(self.config.log_file_path),
                maxBytes=self.config.log_file_rotation_max_bytes,
                backupCount=self.config.log_file_backup_count,
                encoding="utf-8",
            )
            file_formatter = ProcessorFormatter(
                processors=shared_processors + [structlog.processors.JSONRenderer()],
            )
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        
        structlog.configure(
            processors=shared_processors + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def get_logger(self, name: str) -> BoundLogger:
        """
        获取结构化日志记录器
        """
        return structlog.get_logger(name)
    
    def bind_context(self, **kwargs: Any) -> None:
        """
        绑定上下文信息到所有日志
        """
        structlog.contextvars.bind_contextvars(**kwargs)
    
    def clear_context(self) -> None:
        """
        清除所有绑定的上下文
        """
        structlog.contextvars.clear_contextvars()


def get_structured_logger(name: str) -> BoundLogger:
    """
    便捷函数：获取结构化日志记录器
    """
    manager = StructuredLoggingManager()
    return manager.get_logger(name)
