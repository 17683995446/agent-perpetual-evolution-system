"""
配置管理模块 - 使用 Pydantic Settings 实现产品级配置管理

该模块负责：
- 应用程序配置管理
- 环境变量支持
- 配置验证和类型安全
"""

from typing import Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class ApplicationSettings(BaseSettings):
    """应用程序主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENT_SYSTEM_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="Agent Perpetual System",
        description="应用程序名称"
    )
    app_version: str = Field(
        default="2.0.0",
        description="应用程序版本"
    )
    debug_mode: bool = Field(
        default=False,
        description="调试模式开关"
    )
    environment: str = Field(
        default="development",
        description="运行环境：development/staging/production"
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/agent_system.db",
        description="数据库连接URL"
    )
    database_echo_sql: bool = Field(
        default=False,
        description="是否打印SQL语句"
    )
    database_pool_size: int = Field(
        default=5,
        description="数据库连接池大小"
    )

    redis_url: Optional[str] = Field(
        default=None,
        description="Redis连接URL（用于分布式场景）"
    )

    api_host: str = Field(
        default="0.0.0.0",
        description="API监听地址"
    )
    api_port: int = Field(
        default=8000,
        description="API监听端口"
    )
    api_cors_origins: List[str] = Field(
        default=["*"],
        description="CORS允许的源"
    )

    task_poll_interval: float = Field(
        default=2.0,
        description="任务轮询间隔（秒）"
    )
    task_timeout_seconds: int = Field(
        default=300,
        description="任务默认超时时间（秒）"
    )
    task_max_concurrent: int = Field(
        default=1,
        description="最大并发任务数"
    )

    log_level: str = Field(
        default="INFO",
        description="日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL"
    )
    log_file_path: Optional[Path] = Field(
        default=Path("logs/application.log"),
        description="日志文件路径"
    )
    log_to_console: bool = Field(
        default=True,
        description="是否输出到控制台"
    )
    log_file_rotation_max_bytes: int = Field(
        default=10 * 1024 * 1024,
        description="日志文件轮转大小（字节）"
    )
    log_file_backup_count: int = Field(
        default=5,
        description="日志文件保留份数"
    )

    evolution_enabled: bool = Field(
        default=True,
        description="是否启用自主进化模块"
    )
    evolution_memory_cleanup_days: int = Field(
        default=7,
        description="记忆清理天数"
    )
    evolution_phase_sequence: List[str] = Field(
        default=["memory_cleanup", "strategy_optimize", "knowledge_learning"],
        description="进化阶段执行顺序"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证运行环境"""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(
                f"Invalid environment: {v}. Must be one of {valid_environments}"
            )
        return v


# 全局配置单例
_global_settings: Optional[ApplicationSettings] = None


def get_application_settings() -> ApplicationSettings:
    """
    获取全局配置单例

    Returns:
        ApplicationSettings: 应用程序配置实例

    Example:
        >>> settings = get_application_settings()
        >>> print(settings.app_name)
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = ApplicationSettings()
        # 确保日志目录存在
        if _global_settings.log_file_path:
            _global_settings.log_file_path.parent.mkdir(
                parents=True, exist_ok=True
            )
    return _global_settings


def reload_application_settings() -> ApplicationSettings:
    """
    重新加载配置（可用于配置热更新）

    Returns:
        ApplicationSettings: 重新加载后的配置实例
    """
    global _global_settings
    _global_settings = ApplicationSettings()
    return _global_settings
