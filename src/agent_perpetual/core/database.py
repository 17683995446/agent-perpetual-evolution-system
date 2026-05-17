"""
数据库模块 - 使用 SQLAlchemy 2.0 实现产品级数据持久化
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from .config import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    """基础模型类，包含公共字段"""
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


_engine: Optional[object] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def init_database() -> None:
    """初始化数据库连接"""
    global _engine, _session_factory
    settings = get_settings()

    # 确保使用异步驱动
    db_url = settings.database_url
    if db_url.startswith("sqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")

    _engine = create_async_engine(
        db_url,
        echo=settings.echo_sql,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    _session_factory = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def create_tables() -> None:
    """创建数据库表"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的异步上下文管理器"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
