"""
批量修复脚本 - 替换所有硬编码API密钥
"""

import os
import re

# 需要修复的文件列表
files_to_fix = [
    "./test_simple_api.py",
    "./ai_evolution_engine.py",
    "./demo_api.py",
    "./simple_siliconflow_test.py",
    "./test_find_model.py",
    "./test_api_simple.py",
    "./src/agent_perpetual_system_complete/modules/ai_web_api.py",
    "./src/agent_perpetual_system_complete/modules/config_manager.py",
    "./demo_siliconflow.py",
    "./ai_evolution_simple.py",
    "./test_evolution_simple.py",
]

# 硬编码密钥模式
API_KEY_PATTERN = r'API_KEY\s*=\s*["\']REDACTED_API_KEY["\']'

# 替换内容
REPLACEMENT = '''# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")
'''


def fix_file(filepath):
    """修复单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "REDACTED_API_KEY" in content:
            # 使用正则替换
            new_content = re.sub(API_KEY_PATTERN, REPLACEMENT, content)
            
            # 写入修复后的内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 修复成功: {filepath}")
            return True
        else:
            print(f"⚠️ 未找到需要修复的内容: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {filepath}: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("🔧 批量修复硬编码API密钥")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            if fix_file(filepath):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"❌ 文件不存在: {filepath}")
            fail_count += 1
    
    print("\n" + "="*60)
    print(f"修复完成!")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print("="*60)
    
    # 验证修复结果
    print("\n🔍 验证修复结果...")
    remaining_keys = []
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "REDACTED_API_KEY" in content:
                    remaining_keys.append(filepath)
    
    if remaining_keys:
        print("\n❌ 仍有未修复的硬编码密钥:")
        for fp in remaining_keys:
            print(f"  - {fp}")
    else:
        print("\n✅ 所有硬编码密钥已修复!")


if __name__ == "__main__":
    main()

