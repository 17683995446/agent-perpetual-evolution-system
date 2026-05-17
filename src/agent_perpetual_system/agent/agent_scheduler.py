"""
Agent主调度器模块

该模块负责：
- 主循环控制
- 工作模式与进化模式的切换
- 任务调度编排
"""

import asyncio
from ...core.logger_config import get_structured_logger
from ...core.config_manager import get_application_settings
from ...core.database_models import RunningModeEnum
from ...modules.task_management.task_service import TaskService

logger = get_structured_logger(__name__)


class AgentScheduler:
    """
    Agent主调度器

    负责：
    - 任务队列监听
    - 模式切换
    - 主循环控制
    """

    def __init__(self):
        self.settings = get_application_settings()
        self.task_service = TaskService()
        self.running = False
        self.current_mode = RunningModeEnum.IDLE

    async def start(self):
        """启动调度器"""
        logger.info("agent_scheduler_starting")
        self.running = True
        await self.run_main_loop()

    def stop(self):
        """停止调度器"""
        logger.info("agent_scheduler_stopping")
        self.running = False

    async def run_main_loop(self):
        """主循环"""
        while self.running:
            try:
                # 检查是否有待处理任务
                pending_tasks = await self.task_service.get_pending_task_list(limit=1)

                if pending_tasks:
                    self.current_mode = RunningModeEnum.WORKING
                    await self._handle_working_mode(pending_tasks[0])
                else:
                    self.current_mode = RunningModeEnum.IDLE
                    logger.info("no_pending_tasks_idle")

                await asyncio.sleep(self.settings.task_poll_interval)

            except Exception as e:
                logger.error("main_loop_error", error=str(e))
                await asyncio.sleep(1)

        logger.info("main_loop_exited")

    async def _handle_working_mode(self, task):
        """处理工作模式"""
        logger.info("working_mode_task", task_id=task["task_id"])
        result = await self.task_service.execute_single_task(task["task_id"])
        logger.info("working_mode_result", result=result["status"])
