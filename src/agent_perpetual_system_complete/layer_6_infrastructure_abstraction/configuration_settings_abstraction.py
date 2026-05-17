"""
Configuration Settings Abstraction - 配置设置抽象（5个单词）

提供应用程序配置设置的抽象和管理功能。
文件名包含5个单词，非常清晰明了。
"""

import os
from pathlib import Path
from typing import Any, Optional, Dict, Union
from dataclasses import dataclass, field


@dataclass
class ApplicationConfiguration:
    """
    应用程序配置数据类

    包含应用程序运行所需的所有配置参数。
    """
    application_name: str = field(default="Agent Perpetual System")
    application_version: str = field(default="3.0.0")
    environment_type: str = field(default="development")

    debug_mode_enabled: bool = field(default=False)

    api_server_host: str = field(default="0.0.0.0")
    api_server_port: int = field(default=8000)
    api_cors_origins: list = field(default_factory=lambda: ["*"])

    database_url: str = field(default="sqlite+aiosqlite:///./data/agent_system.db")
    database_echo_sql: bool = field(default=False)
    database_pool_size: int = field(default=5)

    task_polling_interval: float = field(default=2.0)
    task_default_timeout: int = field(default=300)
    task_max_concurrent: int = field(default=1)

    logging_level: str = field(default="INFO")
    logging_file_path: Optional[str] = field(default="./logs/application.log")
    logging_console_output: bool = field(default=True)
    logging_rotation_max_bytes: int = field(default=10 * 1024 * 1024)
    logging_backup_count: int = field(default=5)

    evolution_system_enabled: bool = field(default=True)
    evolution_memory_cleanup_days: int = field(default=7)


class ConfigurationSettingsManager:
    """
    配置设置管理器类

    提供配置的加载、访问、更新等功能。
    """

    def __init__(self, config_file_path: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器

        参数:
            config_file_path: 可选的配置文件路径
        """
        self._config: Optional[ApplicationConfiguration] = None
        self._config_file_path = (
            Path(config_file_path) if config_file_path else None
        )

    def load_default_configuration(self) -> ApplicationConfiguration:
        """
        加载默认配置

        返回:
            配置对象
        """
        self._config = ApplicationConfiguration()
        self._apply_environment_variables()
        return self._config

    def _apply_environment_variables(self) -> None:
        """
        应用环境变量覆盖配置
        """
        if self._config is None:
            return

        # 从环境变量读取配置
        env_prefix = "AGENT_SYSTEM_"

        for attr_name in dir(self._config):
            if not attr_name.startswith('_'):
                env_var_name = f"{env_prefix}{attr_name.upper()}"
                env_value = os.getenv(env_var_name)

                if env_value is not None:
                    current_value = getattr(self._config, attr_name)

                    # 根据类型转换值
                    if isinstance(current_value, bool):
                        new_value = env_value.lower() in ('true', '1', 'yes')
                    elif isinstance(current_value, int):
                        new_value = int(env_value)
                    elif isinstance(current_value, float):
                        new_value = float(env_value)
                    elif isinstance(current_value, list):
                        new_value = [item.strip() for item in env_value.split(',')]
                    else:
                        new_value = env_value

                    setattr(self._config, attr_name, new_value)

    def get_configuration(self) -> ApplicationConfiguration:
        """
        获取当前配置对象

        返回:
            配置对象
        """
        if self._config is None:
            return self.load_default_configuration()
        return self._config

    def get_configuration_value(
        self,
        key: str,
        default_value: Any = None
    ) -> Any:
        """
        获取特定配置值

        参数:
            key: 配置键名
            default_value: 未找到时的默认值

        返回:
            配置值
        """
        config = self.get_configuration()

        if hasattr(config, key):
            return getattr(config, key)
        return default_value

    def update_configuration_value(self, key: str, value: Any) -> None:
        """
        更新配置值

        参数:
            key: 配置键名
            value: 新值
        """
        config = self.get_configuration()

        if hasattr(config, key):
            setattr(config, key, value)

    def is_development_environment(self) -> bool:
        """
        判断是否为开发环境

        返回:
            是否为开发环境
        """
        config = self.get_configuration()
        return config.environment_type == "development"

    def is_production_environment(self) -> bool:
        """
        判断是否为生产环境

        返回:
            是否为生产环境
        """
        config = self.get_configuration()
        return config.environment_type == "production"


# 全局配置管理器实例
_config_manager_instance: Optional[ConfigurationSettingsManager] = None


def get_configuration_manager() -> ConfigurationSettingsManager:
    """
    获取全局配置管理器实例

    返回:
        配置管理器
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigurationSettingsManager()
    return _config_manager_instance


def get_configuration() -> ApplicationConfiguration:
    """
    获取全局配置对象

    返回:
        配置对象
    """
    return get_configuration_manager().get_configuration()
