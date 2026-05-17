"""
命令行接口 - 产品级CLI工具
"""

import asyncio
import click
from rich.console import Console
from rich.table import Table
from ..agent.scheduler import AgentScheduler
from ..modules.task_service import TaskService
from ..core.config import get_settings
from ..core.logging import setup_logging

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Agent Perpetual - 永续循环自进化运行系统"""
    setup_logging()


@cli.command()
def start():
    """启动 Agent 系统"""
    console.print("[bold green]启动 Agent Perpetual 系统...[/bold green]")
    
    scheduler = AgentScheduler()
    
    try:
        asyncio.run(scheduler.start())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]系统已停止[/bold yellow]")


@cli.command()
@click.argument("content", type=str)
@click.option("--priority", "-p", type=int, default=5, help="任务优先级 (1-10)")
@click.option("--timeout", "-t", type=int, default=300, help="超时时间(秒)")
def add_task(content, priority, timeout):
    """添加新任务"""
    import json
    try:
        task_content = json.loads(content)
    except json.JSONDecodeError:
        task_content = {"type": "default", "value": content}
    
    async def create():
        task = await TaskService.create_task(
            content=task_content,
            priority=priority,
            timeout=timeout,
        )
        console.print(f"[bold green]任务已创建[/bold green]: {task.task_id}")
    
    asyncio.run(create())


@cli.command()
def list_tasks():
    """列出待处理任务"""
    
    async def show():
        tasks = await TaskService.get_pending_tasks()
        
        if not tasks:
            console.print("[yellow]没有待处理任务[/yellow]")
            return
        
        table = Table(title="待处理任务")
        table.add_column("任务ID", style="cyan")
        table.add_column("优先级", style="magenta")
        table.add_column("状态", style="green")
        table.add_column("创建时间", style="yellow")
        
        for task in tasks:
            table.add_row(
                task.task_id,
                str(task.priority),
                task.status.value,
                task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        
        console.print(table)
    
    asyncio.run(show())


@cli.command()
def info():
    """显示系统信息"""
    settings = get_settings()
    
    table = Table(title="系统信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("运行环境", settings.environment)
    table.add_row("调试模式", str(settings.debug))
    table.add_row("API 端口", str(settings.api_port))
    table.add_row("轮询间隔", f"{settings.poll_interval}秒")
    table.add_row("进化模块", "启用" if settings.enable_evolution else "禁用")
    
    console.print(table)


if __name__ == "__main__":
    cli()
