"""
超简单配置管理器 - 超级简单，零学习成本！
让配置变得比喝水还简单！
"""

import os
import json
from pathlib import Path


class SimpleConfig:
    """超简单配置类 - 只有一个必需参数！"""
    
    def __init__(self):
        # 唯一必需的配置 - 硅基流动API密钥
        self.siliconflow_api_key = ""
        
        # 其他可选配置 - 都有默认值
        self.api_base_url = "https://api.siliconflow.cn/v1"
        self.api_model = "Qwen/Qwen2.5-7B-Instruct"
        self.api_timeout = 60
        
        # 缓存配置
        self.cache_enabled = True
        self.cache_dir = "./cache"
        self.cache_ttl = 3600  # 1小时
        
        # 日志配置
        self.log_level = "INFO"
        self.log_file = "./logs/agent.log"
        
        # 性能配置
        self.max_workers = 4
        self.batch_size = 10
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """智能加载配置 - 按优先级查找"""
        
        # 优先级1: 从环境变量加载
        self._load_from_env()
        
        # 优先级2: 从配置文件加载
        if not self.siliconflow_api_key:
            self._load_from_file()
        
        # 优先级3: 从标准配置目录加载
        if not self.siliconflow_api_key:
            self._load_from_home()
    
    def _load_from_env(self):
        """从环境变量加载 - 优先级最高"""
        self.siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "")
        self.api_base_url = os.getenv("API_BASE_URL", self.api_base_url)
        self.api_model = os.getenv("API_MODEL", self.api_model)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        max_workers = os.getenv("MAX_WORKERS")
        if max_workers:
            try:
                self.max_workers = int(max_workers)
            except:
                pass
    
    def _load_from_file(self):
        """从配置文件加载 - config.json"""
        config_files = [
            "./config.json",
            "./agent_config.json",
            "./settings.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self._apply_config(config)
                    print(f"✅ 加载配置文件: {config_file}")
                    break
                except Exception as e:
                    print(f"⚠️ 读取配置文件失败: {e}")
    
    def _load_from_home(self):
        """从用户主目录加载 - ~/.agent_config.json"""
        home_config = Path.home() / ".agent_config.json"
        if home_config.exists():
            try:
                with open(home_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._apply_config(config)
                print(f"✅ 加载主目录配置: {home_config}")
            except Exception as e:
                print(f"⚠️ 读取配置失败: {e}")
    
    def _apply_config(self, config):
        """应用配置字典"""
        if "siliconflow_api_key" in config:
            self.siliconflow_api_key = config["siliconflow_api_key"]
        if "api_base_url" in config:
            self.api_base_url = config["api_base_url"]
        if "api_model" in config:
            self.api_model = config["api_model"]
        if "log_level" in config:
            self.log_level = config["log_level"]
        if "cache_dir" in config:
            self.cache_dir = config["cache_dir"]
        if "max_workers" in config:
            try:
                self.max_workers = int(config["max_workers"])
            except:
                pass
    
    def save_config(self, filepath="./config.json"):
        """保存配置到文件"""
        config = {
            "siliconflow_api_key": self.siliconflow_api_key,
            "api_base_url": self.api_base_url,
            "api_model": self.api_model,
            "api_timeout": self.api_timeout,
            "cache_enabled": self.cache_enabled,
            "cache_dir": self.cache_dir,
            "log_level": self.log_level,
            "max_workers": self.max_workers,
            "batch_size": self.batch_size
        }
        
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已保存到: {filepath}")
    
    def is_valid(self):
        """检查配置是否有效 - 只需要API密钥！"""
        return bool(self.siliconflow_api_key.strip())
    
    def get_api_key(self):
        """获取API密钥 - 简单直接！"""
        return self.siliconflow_api_key
    
    def help(self):
        """打印配置帮助"""
        print("\n" + "="*60)
        print("📝 配置帮助 - 超级简单！")
        print("="*60)
        print("\n方式1: 环境变量 (最简单)")
        print("  $ export SILICONFLOW_API_KEY=sk-xxxxxxxxxx")
        print("\n方式2: 配置文件 (推荐)")
        print("  创建 config.json:")
        print("    {")
        print('      "siliconflow_api_key": "sk-xxxxxxxxxx"')
        print("    }")
        print("\n方式3: 主目录配置")
        print("  创建 ~/.agent_config.json")
        print("\n" + "="*60)
        print("✅ 只需要1个参数就能运行！")
        print("="*60)


# 全局单例
_simple_config = None


def get_config():
    """获取全局配置 - 一行代码搞定！"""
    global _simple_config
    if _simple_config is None:
        _simple_config = SimpleConfig()
    return _simple_config


def get_api_key():
    """获取API密钥 - 最简单的方式！"""
    return get_config().get_api_key()


def setup_config(api_key, save_file=True):
    """快速设置配置 - 一键配置！"""
    config = get_config()
    config.siliconflow_api_key = api_key
    if save_file:
        config.save_config()
    print("\n🎉 配置完成！现在可以使用了！")
    return config


if __name__ == "__main__":
    print("\n🧪 测试配置系统...")
    config = get_config()
    
    if config.is_valid():
        print("✅ 配置有效！")
        print(f"API密钥: {config.get_api_key()[:10]}...")
    else:
        print("❌ 需要配置API密钥")
        config.help()

