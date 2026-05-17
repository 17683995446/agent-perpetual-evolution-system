"""
Configuration Manager - 配置管理器
统一管理敏感配置，避免硬编码
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class APIConfig:
    """API配置"""
    siliconflow_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database: str = "agent_perpetual"


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "json"
    directory: str = "./logs"


@dataclass
class SystemConfig:
    """系统配置"""
    api: APIConfig = field(default_factory=APIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = SystemConfig()
            cls._instance._load_from_env()
        return cls._instance
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # API配置
        self._config.api.siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "")
        self._config.api.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._config.api.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        # 数据库配置
        self._config.database.host = os.getenv("DB_HOST", "localhost")
        self._config.database.port = int(os.getenv("DB_PORT", "5432"))
        self._config.database.username = os.getenv("DB_USERNAME", "")
        self._config.database.password = os.getenv("DB_PASSWORD", "")
        self._config.database.database = os.getenv("DB_NAME", "agent_perpetual")
        
        # 日志配置
        self._config.logging.level = os.getenv("LOG_LEVEL", "INFO")
        self._config.logging.format = os.getenv("LOG_FORMAT", "json")
        self._config.logging.directory = os.getenv("LOG_DIR", "./logs")
    
    def get_config(self) -> SystemConfig:
        """获取配置"""
        return self._config
    
    def get_api_key(self, service: str) -> str:
        """获取指定服务的API密钥"""
        if service.lower() == "siliconflow":
            return self._config.api.siliconflow_api_key
        elif service.lower() == "openai":
            return self._config.api.openai_api_key
        elif service.lower() == "anthropic":
            return self._config.api.anthropic_api_key
        return ""
    
    def validate_config(self) -> bool:
        """验证配置"""
        errors = []
        
        # 检查必要的API密钥
        if not self._config.api.siliconflow_api_key:
            errors.append("SILICONFLOW_API_KEY 环境变量未设置")
        
        # 检查数据库配置
        if not self._config.database.username:
            errors.append("DB_USERNAME 环境变量未设置")
        if not self._config.database.password:
            errors.append("DB_PASSWORD 环境变量未设置")
        
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True


# 全局配置实例
config_manager = ConfigManager()


def get_config() -> SystemConfig:
    """获取全局配置"""
    return config_manager.get_config()


def get_api_key(service: str) -> str:
    """获取API密钥"""
    return config_manager.get_api_key(service)


def validate_config() -> bool:
    """验证配置"""
    return config_manager.validate_config()


# 辅助函数
def require_api_key(service: str) -> str:
    """获取必需的API密钥，如果未设置则抛出异常"""
    key = get_api_key(service)
    if not key:
        raise EnvironmentError(
            f"请设置环境变量 {service.upper()}_API_KEY"
        )
    return key

