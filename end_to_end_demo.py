#!/usr/bin/env python3
"""
端到端演示 - Agent 永续循环自进化系统完整演示
"""
import asyncio
import time
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent_perpetual.core.config import get_settings
from src.agent_perpetual.core.database import init_database, create_tables
from src.agent_perpetual.core.logging import setup_logging, get_logger
from src.agent_perpetual.core.models import Task, TaskStatus, Mode
from src.agent_perpetual.modules.task_service import TaskService

console = Console()
logger = get_logger(__name__)


class E2EDemo:
    """端到端演示系统"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tasks_processed = 0
        self.start_time = None
    
    async def setup(self):
        """初始化系统"""
        console.print("[cyan]初始化系统...[/cyan]")
        setup_logging()
        init_database()
        await create_tables()
        console.print("[green]系统初始化完成！[/green]\n")
    
    async def create_sample_tasks(self):
        """创建示例任务"""
        console.print(Panel("创建示例任务", style="blue"))
        
        tasks_data = [
            {"type": "analysis", "data": "Analyze customer feedback"},
            {"type": "summarize", "data": "Summarize meeting notes"},
            {"type": "translation", "data": "Translate document to Chinese"},
        ]
        
        created_tasks = []
        for i, task_content in enumerate(tasks_data):
            priority = 10 - i * 3  # 10, 7, 4
            task = await TaskService.create_task(
                content=task_content,
                priority=priority,
                timeout=300
            )
            created_tasks.append(task)
            console.print(f"  ✅ 任务 [cyan]{task.task_id}[/cyan] 创建成功，优先级: {priority}")
        
        console.print()
        return created_tasks
    
    async def display_pending_tasks(self):
        """显示待处理任务"""
        tasks = await TaskService.get_pending_tasks()
        
        if not tasks:
            console.print("[yellow]没有待处理任务[/yellow]")
            return
        
        table = Table(title="待处理任务")
        table.add_column("任务ID", style="cyan")
        table.add_column("类型", style="green")
        table.add_column("优先级", style="magenta")
        table.add_column("状态", style="yellow")
        
        for task in tasks:
            table.add_row(
                task.task_id,
                task.content.get("type", "unknown"),
                str(task.priority),
                task.status.value
            )
        
        console.print(table)
        console.print()
    
    async def process_tasks(self):
        """处理任务"""
        console.print(Panel("开始处理任务", style="green"))
        
        pending_tasks = await TaskService.get_pending_tasks()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for task in pending_tasks:
                task_desc = f"执行任务 {task.task_id}"
                task_progress = progress.add_task(task_desc, total=100)
                
                try:
                    # 模拟执行任务
                    await asyncio.sleep(0.5)
                    progress.update(task_progress, advance=33)
                    
                    updated_task = await TaskService.update_task_status(
                        task.task_id, TaskStatus.RUNNING
                    )
                    await asyncio.sleep(0.5)
                    progress.update(task_progress, advance=33)
                    
                    updated_task = await TaskService.update_task_status(
                        task.task_id,
                        TaskStatus.COMPLETED,
                        result={"status": "success", "output": f"Processed {task.task_id}"}
                    )
                    progress.update(task_progress, advance=34)
                    
                    self.tasks_processed += 1
                    console.print(f"  ✅ 任务 [cyan]{task.task_id}[/cyan] 执行完成")
                    
                except Exception as e:
                    console.print(f"  ❌ 任务执行失败: {str(e)}")
        
        console.print()
    
    async def simulate_evolution(self):
        """模拟空闲时的进化过程"""
        console.print(Panel("模拟空闲进化过程", style="yellow"))
        
        phases = [
            "记忆整理与清理",
            "执行策略优化",
            "知识学习与更新"
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for i, phase in enumerate(phases):
                task_id = progress.add_task(phase, total=100)
                
                for _ in range(5):
                    await asyncio.sleep(0.2)
                    progress.update(task_id, advance=20)
                
                progress.update(task_id, completed=100)
        
        console.print("\n[green]进化过程完成！[/green]")
    
    async def run(self):
        """运行完整演示"""
        console.print(Panel("🚀 Agent 永续循环自进化系统 - 端到端演示", 
                          style="bold blue", expand=False))
        console.print()
        
        await self.setup()
        self.start_time = time.time()
        
        # 创建示例任务
        await self.create_sample_tasks()
        
        # 显示待处理任务
        console.print(Panel("任务队列预览", style="cyan"))
        await self.display_pending_tasks()
        
        # 处理任务
        await self.process_tasks()
        
        # 模拟进化
        await self.simulate_evolution()
        
        # 最终统计
        self.show_summary()
    
    def show_summary(self):
        """显示演示总结"""
        elapsed_time = time.time() - self.start_time
        
        console.print()
        console.print(Panel.fit("📊 演示总结", style="bold green"))
        
        summary_table = Table(show_header=False)
        summary_table.add_column("指标", style="cyan")
        summary_table.add_column("数值", style="green")
        
        summary_table.add_row("处理任务数", str(self.tasks_processed))
        summary_table.add_row("总耗时", f"{elapsed_time:.2f}秒")
        summary_table.add_row("系统状态", "运行正常")
        
        console.print(summary_table)
        console.print()
        console.print("[bold]演示完成！[/bold]")


async def main():
    """主函数"""
    demo = E2EDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]演示被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]演示发生错误: {str(e)}[/red]")
