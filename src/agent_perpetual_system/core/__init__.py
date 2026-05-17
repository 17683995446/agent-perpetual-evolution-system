"""
核心模块 - 包含应用程序的基础设施组件

该模块提供系统运行所需的核心功能：
- 配置管理
- 日志系统
- 数据库管理
- 异常定义
"""

from .config_manager import (
    ApplicationSettings,
    get_application_settings,
    reload_application_settings,
)

from .logger_config import (
    setup_structured_logging,
    get_structured_logger,
    LogContext,
)

from .database_manager import (
    DatabaseBaseModel,
    initialize_database_engine,
    create_database_tables,
    drop_database_tables,
    get_database_session,
    get_database_engine_status,
    close_database_connection,
)

from .database_models import (
    TaskStatusEnum,
    RunningModeEnum,
    EvolutionPhaseEnum,
    TaskDatabaseModel,
    MemoryDatabaseModel,
    StrategyDatabaseModel,
    KnowledgeDatabaseModel,
    SystemStateDatabaseModel,
)

from .exceptions import (
    AgentSystemException,
    DatabaseException,
    TaskNotFoundException,
    TaskExecutionException,
    TaskTimeoutException,
    ConfigurationException,
    EvolutionException,
    SchedulerException,
)

__all__ = [
    # 配置管理
    "ApplicationSettings",
    "get_application_settings",
    "reload_application_settings",
    # 日志系统
    "setup_structured_logging",
    "get_structured_logger",
    "LogContext",
    # 数据库管理
    "DatabaseBaseModel",
    "initialize_database_engine",
    "create_database_tables",
    "drop_database_tables",
    "get_database_session",
    "get_database_engine_status",
    "close_database_connection",
    # 数据模型
    "TaskStatusEnum",
    "RunningModeEnum",
    "EvolutionPhaseEnum",
    "TaskDatabaseModel",
    "MemoryDatabaseModel",
    "StrategyDatabaseModel",
    "KnowledgeDatabaseModel",
    "SystemStateDatabaseModel",
    # 异常
    "AgentSystemException",
    "DatabaseException",
    "TaskNotFoundException",
    "TaskExecutionException",
    "TaskTimeoutException",
    "ConfigurationException",
    "EvolutionException",
    "SchedulerException",
]
