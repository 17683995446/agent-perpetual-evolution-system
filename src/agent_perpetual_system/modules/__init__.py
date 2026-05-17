"""
Modules Module - 业务模块层

该模块包含：
- 任务管理模块
- 进化系统模块
"""

from .task_management import TaskRepository, TaskService
from .evolution_system import (
    EvolutionEngine,
    MemoryCleanupManager,
    StrategyOptimizer,
    KnowledgeLearner,
)

__all__ = [
    # Task Management
    "TaskRepository",
    "TaskService",
    # Evolution System
    "EvolutionEngine",
    "MemoryCleanupManager",
    "StrategyOptimizer",
    "KnowledgeLearner",
]
