"""
批量修复脚本 - 修复裸露的except语句
"""

import os
import re

# 需要修复的文件
files_to_fix = [
    "./ai_evolution_engine.py",
    "./src/agent_perpetual_system_complete/layer_7_foundation_utility/self_evolution_system.py",
    "./src/agent_perpetual_system_complete/modules/ai_web_api.py",
    "./src/agent_perpetual_system_complete/modules/siliconflow_integration.py",
    "./src/agent_perpetual_system_complete/layer_3_business_service/memory_cleanup_service_provider.py",
    "./demo_siliconflow.py",
    "./ai_evolution_simple.py",
]


def fix_file(filepath):
    """修复单个文件中的裸露except"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找裸露的except
        bare_except_pattern = r'except\s*:\s*\n(\s+)'
        
        # 替换为具体的异常类型
        # 这里我们使用 Exception 作为通用的异常类型
        def replace_bare_except(match):
            indent = match.group(1)
            return f'except Exception:\n{indent}'
        
        new_content = re.sub(bare_except_pattern, replace_bare_except, content)
        
        # 检查是否有变化
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 修复成功: {filepath}")
            return True
        else:
            print(f"⚠️ 无需修复: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {filepath}: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("🔧 批量修复裸露的except语句")
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
    remaining = []
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'except\s*:\s*\n\s+(?!.*except)', content):
                    remaining.append(filepath)
    
    if remaining:
        print("\n⚠️ 仍有未修复的裸露except:")
        for fp in remaining:
            print(f"  - {fp}")
    else:
        print("\n✅ 所有裸露的except已修复!")


if __name__ == "__main__":
    main()

