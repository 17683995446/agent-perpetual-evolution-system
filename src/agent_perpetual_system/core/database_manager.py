"""
数据库管理模块 - 使用 SQLAlchemy 2.0 实现产品级数据持久化

该模块负责：
- 数据库连接管理
- 异步会话管理
- 数据库表创建
- 连接池管理
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
from .config_manager import get_application_settings


class DatabaseBaseModel(AsyncAttrs, DeclarativeBase):
    """
    数据库基础模型类

    所有数据库模型都需要继承此类，
    自动获得创建时间和更新时间字段。
    """
    pass


# 全局数据库引擎和会话工厂
_database_engine = None
_database_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def initialize_database_engine() -> None:
    """
    初始化数据库引擎

    该函数根据配置创建异步数据库引擎，
    并设置会话工厂。

    Example:
        >>> initialize_database_engine()
        >>> await create_database_tables()
    """
    global _database_engine, _database_session_factory

    settings = get_application_settings()

    # 创建异步引擎
    _database_engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo_sql,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=settings.database_pool_size,
    )

    # 创建会话工厂
    _database_session_factory = async_sessionmaker(
        _database_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def create_database_tables() -> None:
    """
    创建所有数据库表

    该函数根据模型定义创建所有必要的数据库表。
    建议在应用启动时调用一次。

    Raises:
        RuntimeError: 如果数据库未初始化

    Example:
        >>> initialize_database_engine()
        >>> await create_database_tables()
    """
    if _database_engine is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database_engine() first."
        )

    async with _database_engine.begin() as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.create_all)


async def drop_database_tables() -> None:
    """
    删除所有数据库表

    警告：此操作会删除所有数据，请谨慎使用！
    建议仅在测试环境中使用。

    Raises:
        RuntimeError: 如果数据库未初始化

    Example:
        >>> await drop_database_tables()
    """
    if _database_engine is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database_engine() first."
        )

    async with _database_engine.begin() as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.drop_all)


@asynccontextmanager
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的异步上下文管理器

    该函数提供数据库会话的自动获取和释放，
    自动处理事务的提交和回滚。

    Yields:
        AsyncSession: 异步数据库会话

    Raises:
        RuntimeError: 如果数据库未初始化

    Example:
        >>> async with get_database_session() as session:
        ...     result = await session.execute(select(TaskModel))
        ...     tasks = result.scalars().all()
    """
    if _database_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database_engine() first."
        )

    async with _database_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_database_engine_status() -> dict:
    """
    获取数据库引擎状态

    Returns:
        dict: 包含引擎状态信息的字典

    Example:
        >>> status = await get_database_engine_status()
        >>> print(status["pool_size"])
    """
    if _database_engine is None:
        return {
            "initialized": False,
            "pool_size": 0,
            "checked_out": 0,
        }

    pool = _database_engine.pool
    return {
        "initialized": True,
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }


async def close_database_connection() -> None:
    """
    关闭数据库连接

    建议在应用关闭时调用，释放所有连接资源。

    Example:
        >>> await close_database_connection()
    """
    global _database_engine, _database_session_factory

    if _database_engine is not None:
        await _database_engine.dispose()
        _database_engine = None
        _database_session_factory = None
