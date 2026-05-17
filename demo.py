"""
演示脚本 - 快速体验 Agent Perpetual 的核心功能
"""

import asyncio
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agent_perpetual.core.config import get_settings
from src.agent_perpetual.core.logging import setup_logging, get_logger
from src.agent_perpetual.core.database import init_database, create_tables
from src.agent_perpetual.core.models import TaskStatus, Mode
from src.agent_perpetual.modules.task_service import TaskService

logger = get_logger(__name__)


async def main():
    print("=" * 60)
    print("  Agent Perpetual - 永续循环自进化运行系统")
    print("=" * 60)
    
    # 初始化
    print("\n[1/4] 初始化系统...")
    setup_logging()
    init_database()
    await create_tables()
    print("    ✓ 系统初始化完成")
    
    # 创建测试任务
    print("\n[2/4] 创建测试任务...")
    task1 = await TaskService.create_task(
        content={"type": "test", "data": "Hello World 1"},
        priority=8,
    )
    print(f"    ✓ 创建任务: {task1.task_id} (优先级: 8)")
    
    task2 = await TaskService.create_task(
        content={"type": "test", "data": "Hello World 2"},
        priority=5,
    )
    print(f"    ✓ 创建任务: {task2.task_id} (优先级: 5)")
    
    # 检查待处理任务
    print("\n[3/4] 检查待处理任务...")
    pending_tasks = await TaskService.get_pending_tasks()
    print(f"    ✓ 待处理任务数量: {len(pending_tasks)}")
    for task in pending_tasks:
        print(f"      - {task.task_id}, 优先级: {task.priority}")
    
    # 运行一个任务
    print("\n[4/4] 运行一个任务 (演示)...")
    if pending_tasks:
        print(f"    执行任务: {pending_tasks[0].task_id}")
        try:
            result = await TaskService.run_task(pending_tasks[0])
            print(f"    ✓ 任务执行完成!")
        except Exception as e:
            print(f"    ✗ 任务执行失败: {e}")
    
    # 再次检查任务
    print("\n任务状态检查:")
    all_tasks = await TaskService.get_pending_tasks()
    print(f"  剩余待处理任务: {len(all_tasks)}")
    
    print("\n" + "=" * 60)
    print("  演示完成!")
    print("  要启动完整的系统，请运行:")
    print("  $ agent-perpetual start")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n演示已停止")
