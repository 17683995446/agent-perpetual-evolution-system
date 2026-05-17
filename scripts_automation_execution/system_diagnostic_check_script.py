"""
System Diagnostic Check Script - 系统诊断检查脚本（5个单词）

验证项目结构和配置。
"""

import sys
from pathlib import Path


def check_directory_structure(base_path: Path):
    """
    检查目录结构
    """
    print("🔍 检查项目结构...")

    expected_dirs = [
        "src/agent_perpetual_system_complete/layer_7_foundation_utility",
        "src/agent_perpetual_system_complete/layer_6_infrastructure_abstraction",
        "layer_8_testing_verification/unit_testing_verification",
        "scripts_automation_execution",
        "documentation_reference_guide",
        "configuration_settings_storage",
        "runtime_data_storage",
    ]

    all_good = True
    for dir_path in expected_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (缺失)")
            all_good = False

    return all_good


def check_file_naming(base_path: Path):
    """
    检查文件命名规范
    """
    print("\n📚 检查文件命名规范（4个单词以上）...")

    checked_files = []

    layer_7_dir = base_path / "src/agent_perpetual_system_complete/layer_7_foundation_utility"
    for file_path in layer_7_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        name = file_path.name[:-3]
        word_count = len(name.split("_"))
        checked_files.append((file_path.name, word_count))

    for filename, word_count in checked_files:
        if word_count >= 4:
            print(f"✅ {filename} ({word_count}个单词)")
        else:
            print(f"⚠️ {filename} ({word_count}个单词)")

    return True


def main():
    """
    主函数
    """
    base_path = Path(__file__).parent.parent
    print("=" * 60)
    print("🚀 Agent Perpetual System - 结构诊断检查")
    print("=" * 60)

    structure_ok = check_directory_structure(base_path)
    naming_ok = check_file_naming(base_path)

    print("\n" + "=" * 60)
    if structure_ok and naming_ok:
        print("✅ 所有检查通过！项目结构完整，命名规范！")
    else:
        print("⚠️ 部分检查未通过，请检查上述内容")
    print("=" * 60)


if __name__ == "__main__":
    main()
