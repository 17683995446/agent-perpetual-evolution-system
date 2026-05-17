"""
自定义异常模块 - 定义系统级异常类型

该模块提供所有业务相关的自定义异常，
便于错误处理和日志记录。
"""


class AgentSystemException(Exception):
    """Agent系统基础异常类"""
    pass


class DatabaseException(AgentSystemException):
    """数据库操作异常"""
    pass


class TaskNotFoundException(AgentSystemException):
    """任务未找到异常"""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class TaskExecutionException(AgentSystemException):
    """任务执行异常"""
    def __init__(self, task_id: str, reason: str):
        self.task_id = task_id
        self.reason = reason
        super().__init__(f"Task execution failed: {task_id}, reason: {reason}")


class TaskTimeoutException(AgentSystemException):
    """任务超时异常"""
    def __init__(self, task_id: str, timeout: int):
        self.task_id = task_id
        self.timeout = timeout
        super().__init__(f"Task timeout: {task_id}, timeout: {timeout}s")


class ConfigurationException(AgentSystemException):
    """配置异常"""
    pass


class EvolutionException(AgentSystemException):
    """进化过程异常"""
    pass


class SchedulerException(AgentSystemException):
    """调度器异常"""
    pass
