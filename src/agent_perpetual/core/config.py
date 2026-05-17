"""
配置管理模块 - 使用 Pydantic Settings 实现产品级配置管理
"""

from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """系统配置类，支持环境变量和 .env 文件"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AP_",
        case_sensitive=False,
        extra="ignore",
    )

    # 基础配置
    app_name: str = Field(default="Agent Perpetual System", description="应用名称")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境: development/staging/production")

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./agent_perpetual.db",
        description="数据库连接 URL"
    )
    echo_sql: bool = Field(default=False, description="是否打印 SQL 语句")

    # Redis 配置
    redis_url: Optional[str] = Field(default=None, description="Redis 连接 URL")

    # API 配置
    api_host: str = Field(default="0.0.0.0", description="API 监听地址")
    api_port: int = Field(default=8000, description="API 监听端口")
    cors_origins: list[str] = Field(default=["*"], description="CORS 允许的源")

    # 任务调度配置
    poll_interval: float = Field(default=2.0, description="任务轮询间隔（秒）")
    task_timeout: int = Field(default=300, description="任务超时时间（秒）")
    max_concurrent_tasks: int = Field(default=1, description="最大并发任务数")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[Path] = Field(default=Path("logs/app.log"), description="日志文件路径")
    log_to_console: bool = Field(default=True, description="是否输出到控制台")

    # 进化模块配置
    enable_evolution: bool = Field(default=True, description="是否启用进化模块")
    memory_cleanup_days: int = Field(default=7, description="记忆清理天数")
    evolution_phase_order: list[str] = Field(
        default=["memory_cleanup", "strategy_optimize", "knowledge_learning"],
        description="进化阶段顺序"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v


# 全局配置单例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
        if _settings.log_file:
            _settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    return _settings
