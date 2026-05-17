"""
配置管理模块 - 管理API密钥和系统配置
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    """应用配置"""
    # 硅基流动API配置
    siliconflow_api_key: str = ""
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./app.db"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 其他配置
    debug: bool = True


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else None
        self.config = AppConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
        
        # 从文件加载配置
        if self.config_file and self.config_file.exists():
            self._load_from_file()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        if "SILICONFLOW_API_KEY" in os.environ:
            self.config.siliconflow_api_key = os.environ["SILICONFLOW_API_KEY"]
        
        if "DATABASE_URL" in os.environ:
            self.config.database_url = os.environ["DATABASE_URL"]
        
        if "API_HOST" in os.environ:
            self.config.api_host = os.environ["API_HOST"]
        
        if "API_PORT" in os.environ:
            self.config.api_port = int(os.environ["API_PORT"])
        
        if "DEBUG" in os.environ:
            self.config.debug = os.environ["DEBUG"].lower() in ("true", "1", "yes")
    
    def _load_from_file(self):
        """从配置文件加载"""
        # 简单的JSON配置加载
        try:
            import json
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if config_data:
                if "siliconflow_api_key" in config_data:
                    self.config.siliconflow_api_key = config_data["siliconflow_api_key"]
                
                if "database_url" in config_data:
                    self.config.database_url = config_data["database_url"]
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def get_siliconflow_api_key(self):
        """获取硅基流动API密钥"""
        if not self.config.siliconflow_api_key:
            raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")
        
        return self.config.siliconflow_api_key
    
    def set_siliconflow_api_key(self, api_key: str):
        """设置硅基流动API密钥"""
        self.config.siliconflow_api_key = api_key
