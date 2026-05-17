"""
Agent Perpetual System Complete - 完整的Agent永续循环自进化系统

一个高度模块化的8层架构的智能体运行系统。
"""

from .__version__ import __version__
from .__application_metadata__ import (
    ApplicationMetadata,
    get_application_metadata,
    get_application_name_version_string,
)

__all__ = [
    "__version__",
    "ApplicationMetadata",
    "get_application_metadata",
    "get_application_name_version_string",
]
