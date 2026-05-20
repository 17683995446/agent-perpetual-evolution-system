#!/usr/bin/env python3
"""
语法错误检测与修复脚本
精确定位所有15个语法错误
"""
import ast
import os
from pathlib import Path

BASE_DIR = Path("/workspace/agent_perpetual")

all_python_files = list(BASE_DIR.rglob("*.py"))
print(f"🔍 检查 {len(all_python_files)} 个Python文件...\n")

syntax_errors = []

for file_path in all_python_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        syntax_errors.append({
            "file": str(file_path),
            "lineno": e.lineno,
            "offset": e.offset,
            "text": e.text.rstrip() if e.text else "",
            "msg": e.msg
        })
        print(f"❌ {file_path.name}:{e.lineno}")
        print(f"   {e.msg}")
        if e.text:
            print(f"   {e.text.rstrip()}")
            print(f"   {' ' * (e.offset - 1)}^")
        print()
    except Exception as e:
        pass

print(f"📊 总计发现 {len(syntax_errors)} 个语法错误")

if syntax_errors:
    print("\n" + "="*80)
    print("📋 详细错误列表")
    print("="*80)
    for i, err in enumerate(syntax_errors, 1):
        print(f"\n{i}. {Path(err['file']).name}:{err['lineno']}")
        print(f"   错误: {err['msg']}")
        print(f"   位置: {err['file']}")
        print(f"   代码: {err['text']}")
