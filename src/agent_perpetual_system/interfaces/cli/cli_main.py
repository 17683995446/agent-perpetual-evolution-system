"""
CLI Main Entry Point - 命令行主入口

该模块是系统的命令行主入口，提供：
- 命令行参数解析
- 主命令注册
- 应用程序启动
"""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
import click

# 尝试导入核心模块
try:
    from ...core.config_manager import get_application_settings
    from ...core.logger_config import setup_structured_logging
    from .cli_command_group import AgentSystemCommandGroup
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


console = Console()


@click.group(
    cls=AgentSystemCommandGroup,
    invoke_without_command=True,
    help="Agent Perpetual System - 永续循环自进化运行系统"
)
@click.version_option(
    version="2.0.0",
    prog_name="agent-perpetual-system",
    help="显示版本信息"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="启用详细输出"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="指定配置文件路径"
)
def cli_main(verbose: bool, config: Optional[str]):
    """
    Agent Perpetual System - 永续循环自进化运行系统

    一个高度模块化、产品级的智能体运行框架。
    支持任务管理、记忆管理、策略优化和知识学习。
    """
    # 设置日志
    setup_structured_logging()

    # 显示欢迎信息
    if verbose:
        console.print(Panel.fit(
            "[bold cyan]🚀 Agent Perpetual System[/bold cyan]\n"
            "永续循环自进化运行系统 v2.0.0",
            style="blue"
        ))


def run_cli():
    """
    运行CLI主函数

    这是CLI的入口点
    """
    try:
        cli_main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用户中断[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
