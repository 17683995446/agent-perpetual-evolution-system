#!/usr/bin/env python3
"""
手动修复语法错误脚本
逐个检查和修复有问题的文件
"""
import ast
import os
from pathlib import Path

BASE_DIR = Path("/workspace/agent_perpetual")

print("🔧 开始手动修复语法错误...\n")

# 错误文件列表
error_files = [
    BASE_DIR / "demo_siliconflow.py",
    BASE_DIR / "test_api_simple.py",
    BASE_DIR / "simple_siliconflow_test.py",
    BASE_DIR / "new_chapter_optimization_demo.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "modules" / "siliconflow_integration.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_6_infrastructure_abstraction" / "enhanced_structured_logging.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "dependency_injection_container.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "optimized_concurrency_pool.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "batch_operation_manager.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "advanced_integrated_system.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "advanced_cache_manager.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "advanced_recovery_system.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "ci_cd_system.py",
    BASE_DIR / "src" / "agent_perpetual_system_complete" / "layer_7_foundation_utility" / "advanced_stress_test.py",
]

fixed_count = 0

for file_path in error_files:
    if not file_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        continue
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 先尝试解析
        try:
            ast.parse(content, filename=str(file_path))
            print(f"✅ {file_path.name}: 已经没有语法错误")
            continue
        except SyntaxError as e:
            print(f"🔍 处理: {file_path.name}:{e.lineno}")
            print(f"   错误: {e.msg}")
        
        # 修复策略1：清理奇怪字符
        # 尝试替换一些常见问题
        # 检查是否有非标准冒号
        lines = content.split("\n")
        
        # 简单修复：对于常见语法问题，我们可以尝试一些模式修复
        # 这里我们主要检查一些常见问题
        fixed_content = content
        
        # 保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        
        # 验证
        try:
            ast.parse(fixed_content, filename=str(file_path))
            fixed_count += 1
            print(f"✅ {file_path.name}: 修复成功")
        except Exception as ve:
            print(f"❌ {file_path.name}: 验证失败: {ve}")
            
    except Exception as e:
        print(f"❌ 处理 {file_path} 时出错: {e}")

print(f"\n📊 修复完成: 处理了 {len(error_files)} 个文件")
