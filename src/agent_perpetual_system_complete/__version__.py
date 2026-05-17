"""
Application Version Module - 应用程序版本模块

此模块包含应用程序版本信息，用于版本管理和兼容性检查。
"""

__version__ = "3.0.0"
__major__ = 3
__minor__ = 0
__patch__ = 0
__release__ = "final"
__build__ = 20240514


def get_version_components() -> dict:
    """
    获取版本组件字典

    返回包含主版本、次版本、补丁版本等信息的字典。
    """
    return {
        "major": __major__,
        "minor": __minor__,
        "patch": __patch__,
        "release": __release__,
        "build": __build__,
    }


def get_version_string() -> str:
    """
    获取完整版本字符串

    返回格式为 "x.y.z" 的版本字符串。
    """
    return f"{__major__}.{__minor__}.{__patch__}"
