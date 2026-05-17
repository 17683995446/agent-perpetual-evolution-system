"""
数据模型模块 - 定义系统核心数据结构
"""

from enum import Enum, StrEnum
from typing import Optional, Dict, Any
from sqlalchemy import JSON, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class TaskStatus(StrEnum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Mode(StrEnum):
    """运行模式枚举"""
    IDLE = "idle"
    WORKING = "working"
    EVOLUTION = "evolution"


class EvolutionPhase(StrEnum):
    """进化阶段枚举"""
    MEMORY_CLEANUP = "memory_cleanup"
    STRATEGY_OPTIMIZE = "strategy_optimize"
    KNOWLEDGE_LEARNING = "knowledge_learning"


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5, index=True)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING, index=True)
    timeout: Mapped[int] = mapped_column(Integer, default=300)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class Memory(Base):
    """记忆模型"""
    __tablename__ = "memories"

    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    source_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    score: Mapped[float] = mapped_column(Float, default=0.5, index=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)


class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    effect_score: Mapped[float] = mapped_column(Float, default=0.0)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)


class Knowledge(Base):
    """知识模型"""
    __tablename__ = "knowledge"

    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    source: Mapped[str] = mapped_column(String(500), nullable=True)
    struct_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    learn_status: Mapped[str] = mapped_column(String(20), default="pending")
    ability_tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)


class SystemState(Base):
    """系统状态模型"""
    __tablename__ = "system_state"

    current_mode: Mapped[Mode] = mapped_column(default=Mode.IDLE)
    current_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evolution_phase: Mapped[Optional[EvolutionPhase]] = mapped_column(nullable=True)
    evolution_progress: Mapped[float] = mapped_column(Float, default=0.0)
    system_health: Mapped[float] = mapped_column(Float, default=1.0)
    last_checkpoint: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
