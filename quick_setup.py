"""
一键配置脚本 - 30秒搞定配置！
运行方式:
  python quick_setup.py
"""

import sys
import os


def print_header():
    print("\n" + "="*70)
    print("🎉 Agent永续自进化系统 - 快速配置")
    print("="*70)


def show_current_status():
    """检查当前配置状态"""
    print("\n📊 当前状态检查:")
    
    # 检查环境变量
    if os.environ.get("SILICONFLOW_API_KEY") and print("✅ 环境变量已配置") or print("❌ 环境变量未配置")
    
    # 检查配置文件
    if os.path.exists("./config.json") and print("✅ config.json 存在") or print("❌ config.json 不存在")
    
    if os.path.exists("./agent_config.json") and print("✅ agent_config.json 存在") or print("❌ agent_config.json 不存在")


def quick_setup():
    """快速设置"""
    print_header()
    print("\n🚀 只需要一个参数就能开始！")
    
    # 收集配置
    api_key = input("\n请输入您的硅基流动API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 保存配置
    try:
        import simple_config
        config = simple_config.setup_config(api_key, save_file=True)
        
        print("\n" + "="*70)
        print("✅ 配置完成！")
        print("="*70)
        
        # 验证
        if config.is_valid():
            print("✅ 配置验证成功！")
            print(f"  - 配置文件: ./config.json")
            print(f"  - API密钥: " + config.get_api_key()[:10] + "...")
            print("\n🎉 现在可以开始使用了！")
            print("  运行: python simple_agent.py")
            return True
        else:
            print("❌ 配置验证失败")
            return False
            
    except ImportError:
        print("\n💡 提示: 请确保 simple_config.py 在同级目录")
        return False


def show_quick_guide():
    """显示快速指南"""
    print("\n" + "="*70)
    print("📖 快速使用指南")
    print("="*70)
    
    print("\n方法1: 环境变量 (最快")
    print("  $ export SILICONFLOW_API_KEY=sk-...")
    
    print("\n方法2: 配置文件 (推荐)")
    print("  $ cp config.example.json config.json")
    print("  $ nano config.json")
    
    print("\n方法3: 一键配置 (最简单)")
    print("  $ python quick_setup.py")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # 检查是否需要帮助
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_quick_guide()
    elif len(sys.argv) > 1 and sys.argv[1] in ["--status", "-s"]:
        show_current_status()
    else:
        quick_setup()

