"""
CLI Command Definition - 命令行命令定义

该模块定义所有CLI命令：
- start: 启动系统
- stop: 停止系统
- task: 任务相关命令
- status: 查看状态
- info: 系统信息
"""

import asyncio
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import click

try:
    from ...core.config_manager import get_application_settings
    from ...core.logger_config import setup_structured_logging
    from ...modules.task_management.task_service import TaskService
    from ...modules.evolution_system.evolution_engine import EvolutionEngine
except ImportError:
    pass


console = Console()


class AgentSystemCommandGroup(click.Group):
    """自定义命令组"""

    def resolve_command(self, ctx, args):
        """解析命令"""
        return super().resolve_command(ctx, args)


@click.command("start", help="启动 Agent 系统")
@click.option(
    "--mode",
    type=click.Choice(["full", "task-only", "evolution-only"]),
    default="full",
    help="运行模式"
)
def command_start_system(mode: str):
    """
    启动 Agent 系统

    Args:
        mode: 运行模式
            - full: 完整模式（任务+进化）
            - task-only: 仅任务模式
            - evolution-only: 仅进化模式
    """
    console.print(f"[green]启动 Agent 系统 (模式: {mode})[/green]")

    try:
        # 初始化系统
        setup_structured_logging()

        console.print("[green]✅ 系统启动成功[/green]")
        console.print("按 Ctrl+C 停止系统")

        # 保持运行
        asyncio.run(asyncio.Event().wait())

    except KeyboardInterrupt:
        console.print("\n[yellow]系统已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]启动失败: {str(e)}[/red]")


@click.command("status", help="查看系统状态")
@click.option("--detailed", "-d", is_flag=True, help="显示详细信息")
def command_show_status(detailed: bool):
    """显示系统当前状态"""
    console.print("[cyan]获取系统状态...[/cyan]")

    try:
        settings = get_application_settings()

        # 创建状态表
        table = Table(title="系统状态", show_header=True)
        table.add_column("项目", style="cyan")
        table.add_column("值", style="green")

        table.add_row("系统名称", settings.app_name)
        table.add_row("运行模式", settings.environment)
        table.add_row("调试模式", "开启" if settings.debug_mode else "关闭")
        table.add_row("进化模块", "启用" if settings.evolution_enabled else "禁用")
        table.add_row("轮询间隔", f"{settings.task_poll_interval}秒")

        console.print(table)

        if detailed:
            console.print("\n[cyan]详细统计信息:[/cyan]")

            async def get_detailed_stats():
                task_service = TaskService()
                stats = await task_service.get_task_statistics()

                detail_table = Table(show_header=False)
                detail_table.add_column("统计项", style="yellow")
                detail_table.add_column("数量", style="green")

                detail_table.add_row("待处理任务", str(stats.get("pending", 0)))
                detail_table.add_row("正在执行", str(stats.get("running", 0)))
                detail_table.add_row("已完成", str(stats.get("completed", 0)))
                detail_table.add_row("执行失败", str(stats.get("failed", 0)))
                detail_table.add_row("总计", str(stats.get("total", 0)))

                console.print(detail_table)

            asyncio.run(get_detailed_stats())

    except Exception as e:
        console.print(f"[red]获取状态失败: {str(e)}[/red]")


@click.command("info", help="显示系统信息")
def command_show_info():
    """显示系统详细信息"""
    console.print("[cyan]Agent Perpetual System[/cyan]")
    console.print("版本: 2.0.0")
    console.print("描述: 永续循环自进化运行系统")
    console.print("功能:")
    console.print("  - 任务管理与执行")
    console.print("  - 记忆管理与清理")
    console.print("  - 策略自动优化")
    console.print("  - 知识自主学习")


@click.command("task-create", help="创建新任务")
@click.argument("content", type=str)
@click.option("--priority", "-p", type=int, default=5, help="任务优先级 (1-10)")
@click.option("--timeout", "-t", type=int, default=300, help="超时时间(秒)")
def command_create_task(content: str, priority: int, timeout: int):
    """
    创建新任务

    Args:
        content: 任务内容 (JSON格式或纯文本)
        priority: 优先级 (1-10)
        timeout: 超时时间(秒)
    """
    try:
        # 尝试解析JSON
        try:
            task_content = json.loads(content)
        except json.JSONDecodeError:
            task_content = {"type": "default", "value": content}

        async def create():
            task_service = TaskService()
            result = await task_service.create_new_task(
                content=task_content,
                priority=priority,
                timeout=timeout
            )
            return result

        result = asyncio.run(create())

        console.print(f"[green]✅ 任务创建成功[/green]")
        console.print(f"任务ID: {result['task_id']}")
        console.print(f"优先级: {result['priority']}")
        console.print(f"状态: {result['status']}")

    except Exception as e:
        console.print(f"[red]创建任务失败: {str(e)}[/red]")


@click.command("task-list", help="列出待处理任务")
@click.option("--limit", "-l", type=int, default=10, help="显示数量限制")
def command_list_tasks(limit: int):
    """列出待处理任务"""
    console.print("[cyan]获取待处理任务列表...[/cyan]")

    try:
        async def get_tasks():
            task_service = TaskService()
            tasks = await task_service.get_pending_task_list(limit=limit)
            return tasks

        tasks = asyncio.run(get_tasks())

        if not tasks:
            console.print("[yellow]没有待处理任务[/yellow]")
            return

        table = Table(title=f"待处理任务 (共 {len(tasks)} 个)")
        table.add_column("任务ID", style="cyan")
        table.add_column("类型", style="green")
        table.add_column("优先级", style="magenta")
        table.add_column("状态", style="yellow")
        table.add_column("创建时间", style="blue")

        for task in tasks:
            table.add_row(
                task["task_id"],
                task["content"].get("type", "unknown"),
                str(task["priority"]),
                task["status"],
                task["created_at"].split("T")[0] if task.get("created_at") else "N/A"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]获取任务列表失败: {str(e)}[/red]")


@click.command("task-execute", help="执行指定任务")
@click.argument("task_id")
def command_execute_task(task_id: str):
    """
    执行指定任务

    Args:
        task_id: 任务ID
    """
    console.print(f"[cyan]执行任务: {task_id}[/cyan]")

    try:
        async def execute():
            task_service = TaskService()
            result = await task_service.execute_single_task(task_id)
            return result

        with Progress() as progress:
            task_progress = progress.add_task("执行中...", total=100)
            result = asyncio.run(execute())

            if result["status"] == "success":
                progress.update(task_progress, completed=100)
                console.print(f"[green]✅ 任务执行成功[/green]")
                console.print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
            else:
                progress.update(task_progress, completed=100)
                console.print(f"[red]❌ 任务执行失败[/red]")
                console.print(f"错误: {result.get('error', 'Unknown error')}")

    except Exception as e:
        console.print(f"[red]执行任务失败: {str(e)}[/red]")


# 注册命令到命令组
def register_commands(cli_group):
    """注册所有命令到命令组"""
    cli_group.add_command(command_start_system, name="start")
    cli_group.add_command(command_show_status, name="status")
    cli_group.add_command(command_show_info, name="info")
    cli_group.add_command(command_create_task, name="task-create")
    cli_group.add_command(command_list_tasks, name="task-list")
    cli_group.add_command(command_execute_task, name="task-execute")
