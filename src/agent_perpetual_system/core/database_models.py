"""
数据库模型模块 - 定义系统核心数据模型

该模块负责：
- 定义所有数据库表结构
- 提供数据类型和约束
- 定义模型之间的关系

使用 SQLAlchemy 2.0 ORM 风格，支持异步操作。
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import JSON, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database_manager import DatabaseBaseModel


class TaskStatusEnum:
    """
    任务状态枚举类

    定义任务可能的所有状态：
    - PENDING: 等待执行
    - RUNNING: 正在执行
    - COMPLETED: 已完成
    - FAILED: 执行失败
    - TIMEOUT: 执行超时
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class RunningModeEnum:
    """
    运行模式枚举类

    定义系统运行模式：
    - IDLE: 空闲模式（无任务）
    - WORKING: 工作模式（执行任务）
    - EVOLUTION: 进化模式（空闲时自我进化）
    """
    IDLE = "idle"
    WORKING = "working"
    EVOLUTION = "evolution"


class EvolutionPhaseEnum:
    """
    进化阶段枚举类

    定义空闲进化过程的四个阶段：
    - IDLE: 空闲状态（等待进化）
    - MEMORY_CLEANUP: 记忆整理与清理
    - STRATEGY_OPTIMIZE: 执行策略优化
    - KNOWLEDGE_LEARNING: 知识学习与补强
    """
    IDLE = "idle"
    MEMORY_CLEANUP = "memory_cleanup"
    STRATEGY_OPTIMIZE = "strategy_optimize"
    KNOWLEDGE_LEARNING = "knowledge_learning"


class TaskDatabaseModel(DatabaseBaseModel):
    """
    任务数据库模型

    存储任务的所有信息和执行状态。

    Attributes:
        task_id: 任务唯一标识符
        content: 任务内容（JSON格式）
        priority: 任务优先级（1-10，数值越大优先级越高）
        status: 任务当前状态
        timeout: 任务超时时间（秒）
        context: 任务执行上下文
        result: 任务执行结果
        error_message: 错误信息（如果失败）
        execution_time: 执行耗时（秒）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="任务唯一标识符"
    )
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="任务内容（JSON格式）"
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        index=True,
        comment="任务优先级（1-10）"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=TaskStatusEnum.PENDING,
        index=True,
        comment="任务当前状态"
    )
    timeout: Mapped[int] = mapped_column(
        Integer,
        default=300,
        comment="任务超时时间（秒）"
    )
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="任务执行上下文"
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="任务执行结果"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="错误信息"
    )
    execution_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="执行耗时（秒）"
    )


class MemoryDatabaseModel(DatabaseBaseModel):
    """
    记忆数据库模型

    存储系统的记忆和经验数据。

    Attributes:
        memory_type: 记忆类型（context/experience/knowledge）
        content: 记忆内容
        source_task_id: 来源任务ID
        score: 记忆价值评分（0-1）
        tags: 记忆标签（用于检索）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "memories"

    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="记忆类型"
    )
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="记忆内容"
    )
    source_task_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="来源任务ID"
    )
    score: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        index=True,
        comment="价值评分（0-1）"
    )
    tags: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="记忆标签"
    )


class StrategyDatabaseModel(DatabaseBaseModel):
    """
    策略数据库模型

    存储系统执行策略和优化记录。

    Attributes:
        name: 策略名称
        task_type: 适用任务类型
        content: 策略内容
        effect_score: 效果评分
        version: 版本号
        is_active: 是否激活
    """
    __tablename__ = "strategies"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="策略名称"
    )
    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="适用任务类型"
    )
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="策略内容"
    )
    effect_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        comment="效果评分"
    )
    version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        comment="版本号"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        comment="是否激活"
    )


class KnowledgeDatabaseModel(DatabaseBaseModel):
    """
    知识数据库模型

    存储系统学习的知识内容。

    Attributes:
        content: 知识内容
        source: 知识来源
        struct_result: 结构化结果
        learn_status: 学习状态
        ability_tags: 能力标签
    """
    __tablename__ = "knowledge"

    content: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="知识内容"
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="知识来源"
    )
    struct_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="结构化结果"
    )
    learn_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="学习状态"
    )
    ability_tags: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="能力标签"
    )


class SystemStateDatabaseModel(DatabaseBaseModel):
    """
    系统状态数据库模型

    存储系统当前的运行状态，支持断点续跑。

    Attributes:
        current_mode: 当前运行模式
        current_task_id: 当前执行的任务ID
        evolution_phase: 当前进化阶段
        evolution_progress: 进化进度（0-1）
        system_health: 系统健康度（0-1）
        last_checkpoint: 上次检查点时间
    """
    __tablename__ = "system_state"

    current_mode: Mapped[str] = mapped_column(
        String(20),
        default=RunningModeEnum.IDLE,
        comment="当前运行模式"
    )
    current_task_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="当前执行的任务ID"
    )
    evolution_phase: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="当前进化阶段"
    )
    evolution_progress: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        comment="进化进度（0-1）"
    )
    system_health: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        comment="系统健康度（0-1）"
    )
    last_checkpoint: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="上次检查点时间"
    )
