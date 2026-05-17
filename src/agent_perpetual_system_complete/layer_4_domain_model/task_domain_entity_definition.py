"""
Task Domain Entity Definition - 任务领域实体定义（5个单词）

定义任务领域的实体和值对象，使用 SQLAlchemy 2.0 实现。
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Boolean, Float, Text, DateTime, JSON, 
    PrimaryKeyConstraint, Index, ForeignKey
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

# 声明基类
Base = declarative_base()


class TaskStatus(str, Enum):
    """
    任务状态枚举
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(int, Enum):
    """
    任务优先级枚举
    """
    LOWEST = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    HIGHEST = 5


class TaskDomainEntity(Base):
    """
    任务领域实体
    """
    __tablename__ = "task_domain_entity"
    __table_args__ = (
        Index("idx_task_status_priority", "status", "priority"),
        Index("idx_task_created_at", "created_at"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_identifier: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    task_content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=TaskPriority.MEDIUM)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.PENDING, index=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    execution_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(
        self,
        task_identifier: str,
        task_content: Dict[str, Any],
        priority: int = TaskPriority.MEDIUM,
        status: str = TaskStatus.PENDING,
        timeout_seconds: int = 300,
        execution_context: Optional[Dict[str, Any]] = None,
        is_archived: bool = False,
        **kwargs
    ):
        self.task_identifier = task_identifier
        self.task_content = task_content
        self.priority = priority
        self.status = status
        self.timeout_seconds = timeout_seconds
        self.execution_context = execution_context
        self.is_archived = is_archived
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return (
            f"<TaskDomainEntity(id={self.id}, task_identifier='{self.task_identifier}', "
            f"status='{self.status}')>"
        )


class TaskExecutionLog(Base):
    """
    任务执行日志实体
    记录任务执行过程中的详细日志。
    """
    __tablename__ = "task_execution_log"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    log_level: Mapped[str] = mapped_column(String(20))
    log_message: Mapped[str] = mapped_column(Text)
    log_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    def __init__(
        self,
        task_id: str,
        log_level: str,
        log_message: str,
        log_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.task_id = task_id
        self.log_level = log_level
        self.log_message = log_message
        self.log_metadata = log_metadata
        self.created_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            setattr(self, key, value)
