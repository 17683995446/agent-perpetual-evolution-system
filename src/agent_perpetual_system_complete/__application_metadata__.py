"""
Application Metadata Module - 应用程序元数据模块

此模块包含关于应用程序的元信息，包括应用名称、版本、作者等。
文件名包含4个单词，非常清晰。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ApplicationMetadata:
    """
    应用程序元数据类

    包含应用程序的基本元信息，用于标识和描述系统。
    所有属性都有完整的文档字符串。
    """
    application_full_name: str = field(default="Agent Perpetual System Complete")
    application_short_name: str = field(default="AgentSystemV2")
    application_version: str = field(default="3.0.0")
    application_description: str = field(default="A complete, modular, 8-layer architecture agent system")
    application_author: str = field(default="Agent Team")
    application_license: str = field(default="MIT License")
    application_copyright: str = field(default="2024 Agent Team")
    architecture_layers_count: int = field(default=8)
    minimum_python_version: str = field(default="3.10.0")


APPLICATION_METADATA = ApplicationMetadata()


def get_application_metadata() -> ApplicationMetadata:
    """
    获取应用程序元数据实例

    返回包含所有应用元信息的配置对象。
    """
    return APPLICATION_METADATA


def get_application_name_version_string() -> str:
    """
    获取应用名称和版本的组合字符串

    返回格式化的 "名称 版本" 字符串，用于显示。
    """
    metadata = get_application_metadata()
    return f"{metadata.application_full_name} v{metadata.application_version}"


def get_architecture_information_dict() -> Dict[str, Any]:
    """
    获取架构信息字典

    返回包含架构层数和描述的字典。
    """
    metadata = get_application_metadata()
    return {
        "total_layers": metadata.architecture_layers_count,
        "layers": [
            "Layer 1: Interface Presentation Layer",
            "Layer 2: Orchestration Coordination Layer",
            "Layer 3: Business Service Layer",
            "Layer 4: Domain Model Layer",
            "Layer 5: Data Access Layer",
            "Layer 6: Infrastructure Abstraction Layer",
            "Layer 7: Foundation Utility Layer",
            "Layer 8: Testing Verification Layer",
        ],
        "description": "8-layer architecture with clear separation of concerns",
    }
