"""
极简示例 - 一行代码获取API密钥！
展示新配置系统有多简单！
"""

import sys
import simple_config


def main():
    print("\n" + "="*60)
    print("🎉 Agent永续自进化系统 - 极简示例")
    print("="*60)
    
    config = simple_config.get_config()
    
    if config.is_valid():
        print("\n✅ 配置就绪！")
        print(f"   API密钥: {config.get_api_key()[:10]}...")
        print(f"   模型: {config.api_model}")
        print(f"   API地址: {config.api_base_url}")
        print(f"   日志级别: {config.log_level}")
    else:
        print("\n❌ 请配置API密钥")
        config.help()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # 如果传入 setup 参数，进行快速设置
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        api_key = input("\n请输入API密钥: ")
        simple_config.setup_config(api_key)
    else:
        main()

