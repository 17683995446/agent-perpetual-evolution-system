"""
Workflow Engine - 工作流引擎（3个单词）

基于DAG的工作流定义、执行和管理引擎。
"""

import asyncio
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


class WorkflowStatus(str, Enum):
    """工作流状态"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskNodeStatus(str, Enum):
    """任务节点状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskNodeType(str, Enum):
    """任务节点类型"""
    ACTION = "action"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    SUBWORKFLOW = "subworkflow"
    WAIT = "wait"


@dataclass
class TaskNodeDependency:
    """任务节点依赖"""
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)


@dataclass
class TaskNode:
    """工作流任务节点"""
    node_id: str
    name: str
    node_type: TaskNodeType
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: TaskNodeDependency = field(default_factory=TaskNodeDependency)
    status: TaskNodeStatus = TaskNodeStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    entry_point: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowExecution:
    """工作流执行实例"""
    execution_id: str
    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.CREATED
    node_states: Dict[str, TaskNodeStatus] = field(default_factory=dict)
    node_results: Dict[str, Any] = field(default_factory=dict)
    node_errors: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_execution_id: Optional[str] = None


@dataclass
class WorkflowExecutionConfiguration:
    """工作流执行配置"""
    max_concurrent_nodes: int = 5
    enable_node_retry: bool = True
    max_retries_per_node: int = 3
    retry_delay_seconds: float = 1.0
    enable_conditional_execution: bool = True
    pause_on_failure: bool = False
    execution_timeout_seconds: int = 3600


class WorkflowEngine:
    """
    工作流引擎
    
    核心职责：
    1. 工作流定义和验证
    2. 拓扑排序和依赖解析
    3. 并行执行管理
    4. 条件分支处理
    5. 执行状态追踪
    6. 回溯和重试
    """

    def __init__(self, config: Optional[WorkflowExecutionConfiguration] = None):
        self.config = config or WorkflowExecutionConfiguration()
        self.logger = get_structured_logger(__name__)

        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._node_executors: Dict[TaskNodeType, Callable] = {}
        self._is_running = False

    async def initialize(self) -> None:
        """初始化工作流引擎"""
        self.logger.info(
            "initializing_workflow_engine",
            max_concurrent=self.config.max_concurrent_nodes,
            enable_retry=self.config.enable_node_retry,
        )

        self._register_default_executors()

        self.logger.info("workflow_engine_initialized")

    def _register_default_executors(self) -> None:
        """注册默认的节点执行器"""
        self._node_executors[TaskNodeType.ACTION] = self._execute_action_node
        self._node_executors[TaskNodeType.CONDITION] = self._execute_condition_node
        self._node_executors[TaskNodeType.PARALLEL] = self._execute_parallel_node
        self._node_executors[TaskNodeType.LOOP] = self._execute_loop_node
        self._node_executors[TaskNodeType.SUBWORKFLOW] = self._execute_subworkflow_node
        self._node_executors[TaskNodeType.WAIT] = self._execute_wait_node

    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """
        注册工作流
        
        Args:
            workflow: 工作流定义
            
        Returns:
            注册是否成功
        """
        if not self._validate_workflow(workflow):
            return False

        self._workflows[workflow.workflow_id] = workflow

        self.logger.info(
            "workflow_registered",
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            node_count=len(workflow.nodes),
        )

        return True

    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """
        验证工作流定义
        
        检查：
        1. 循环依赖检测
        2. 入口点存在性
        3. 所有依赖节点存在性
        """
        if not workflow.entry_point:
            self.logger.error("workflow_validation_failed_no_entry_point", workflow_id=workflow.workflow_id)
            return False

        if workflow.entry_point not in workflow.nodes:
            self.logger.error(
                "workflow_validation_failed_invalid_entry_point",
                workflow_id=workflow.workflow_id,
                entry_point=workflow.entry_point,
            )
            return False

        dependency_graph = self._build_dependency_graph(workflow)

        if self._has_circular_dependency(dependency_graph):
            self.logger.error(
                "workflow_validation_failed_circular_dependency",
                workflow_id=workflow.workflow_id,
            )
            return False

        for node_id, node in workflow.nodes.items():
            for dep_id in node.dependencies.depends_on:
                if dep_id not in workflow.nodes:
                    self.logger.error(
                        "workflow_validation_failed_missing_dependency",
                        workflow_id=workflow.workflow_id,
                        node_id=node_id,
                        missing_dep=dep_id,
                    )
                    return False

        self.logger.debug("workflow_validation_passed", workflow_id=workflow.workflow_id)
        return True

    def _build_dependency_graph(self, workflow: WorkflowDefinition) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph: Dict[str, List[str]] = defaultdict(list)

        for node_id, node in workflow.nodes.items():
            for dep_id in node.dependencies.depends_on:
                graph[dep_id].append(node_id)

        return graph

    def _has_circular_dependency(self, graph: Dict[str, List[str]]) -> bool:
        """检测循环依赖"""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def get_topological_order(self, workflow: WorkflowDefinition) -> List[str]:
        """
        获取拓扑排序顺序
        
        使用Kahn算法进行拓扑排序
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in workflow.nodes}

        for node_id, node in workflow.nodes.items():
            in_degree[node_id] = len(node.dependencies.depends_on)

        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result: List[str] = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)

            for dependent_id, dependent_node in workflow.nodes.items():
                if node_id in dependent_node.dependencies.depends_on:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)

        if len(result) != len(workflow.nodes):
            self.logger.warning(
                "topological_sort_incomplete",
                expected=len(workflow.nodes),
                actual=len(result),
            )

        return result

    async def execute_workflow(
        self,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        parent_execution_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            parameters: 执行参数
            parent_execution_id: 父执行ID（用于子工作流）
            
        Returns:
            执行ID
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            self.logger.error("workflow_not_found", workflow_id=workflow_id)
            return None

        execution_id = f"exec-{workflow_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            definition=workflow,
            context=parameters or {},
            parent_execution_id=parent_execution_id,
        )

        self._executions[execution_id] = execution

        self.logger.info(
            "workflow_execution_started",
            execution_id=execution_id,
            workflow_id=workflow_id,
            entry_point=workflow.entry_point,
        )

        asyncio.create_task(self._execute_workflow_async(execution_id))

        return execution_id

    async def _execute_workflow_async(self, execution_id: str) -> None:
        """异步执行工作流"""
        execution = self._executions.get(execution_id)
        if not execution:
            return

        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.utcnow()

        try:
            ready_queue = deque()
            running_tasks: Dict[str, asyncio.Task] = {}

            execution.node_states[execution.definition.entry_point] = TaskNodeStatus.READY
            ready_queue.append(execution.definition.entry_point)

            while ready_queue or running_tasks:
                while len(running_tasks) < self.config.max_concurrent_nodes and ready_queue:
                    node_id = ready_queue.popleft()
                    task = asyncio.create_task(self._execute_node(execution_id, node_id))
                    running_tasks[node_id] = task

                if running_tasks:
                    done, pending = await asyncio.wait(
                        running_tasks.values(),
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for completed_task in done:
                        for node_id, task in list(running_tasks.items()):
                            if task == completed_task:
                                del running_tasks[node_id]
                                break

                newly_ready = [
                    node_id
                    for node_id, status in execution.node_states.items()
                    if status == TaskNodeStatus.READY and node_id not in running_tasks
                ]

                for node_id in newly_ready:
                    if self._are_dependencies_satisfied(execution, node_id):
                        ready_queue.append(node_id)
                    else:
                        execution.node_states[node_id] = TaskNodeStatus.PENDING

            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()

            self.logger.info(
                "workflow_execution_completed",
                execution_id=execution_id,
                duration=(execution.completed_at - execution.started_at).total_seconds(),
            )

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()

            self.logger.error(
                "workflow_execution_failed",
                execution_id=execution_id,
                error=str(e),
            )

    async def _execute_node(self, execution_id: str, node_id: str) -> None:
        """执行单个节点"""
        execution = self._executions.get(execution_id)
        if not execution:
            return

        node = execution.definition.nodes.get(node_id)
        if not node:
            return

        execution.node_states[node_id] = TaskNodeStatus.RUNNING
        node.status = TaskNodeStatus.RUNNING
        node.started_at = datetime.utcnow()

        self.logger.info(
            "node_execution_started",
            execution_id=execution_id,
            node_id=node_id,
            node_type=node.node_type,
        )

        try:
            executor = self._node_executors.get(node.node_type)
            if not executor:
                raise ValueError(f"No executor for node type: {node.node_type}")

            result = await executor(execution, node)

            node.result = result
            node.status = TaskNodeStatus.COMPLETED
            node.completed_at = datetime.utcnow()

            execution.node_states[node_id] = TaskNodeStatus.COMPLETED
            execution.node_results[node_id] = result

            self.logger.info(
                "node_execution_completed",
                execution_id=execution_id,
                node_id=node_id,
                duration=(node.completed_at - node.started_at).total_seconds(),
            )

        except Exception as e:
            node.status = TaskNodeStatus.FAILED
            node.error = str(e)
            node.completed_at = datetime.utcnow()

            execution.node_states[node_id] = TaskNodeStatus.FAILED
            execution.node_errors[node_id] = str(e)

            self.logger.error(
                "node_execution_failed",
                execution_id=execution_id,
                node_id=node_id,
                error=str(e),
            )

            if self.config.pause_on_failure:
                execution.status = WorkflowStatus.PAUSED

    def _are_dependencies_satisfied(self, execution: WorkflowExecution, node_id: str) -> bool:
        """检查节点依赖是否满足"""
        node = execution.definition.nodes.get(node_id)
        if not node:
            return False

        for dep_id in node.dependencies.depends_on:
            dep_status = execution.node_states.get(dep_id)
            if dep_status != TaskNodeStatus.COMPLETED:
                return False

        return True

    async def _execute_action_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行动作节点"""
        action_config = node.config.get("action", {})

        self.logger.debug(
            "executing_action_node",
            node_id=node.node_id,
            action=action_config.get("type"),
        )

        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "node_id": node.node_id,
            "output": action_config.get("output", {}),
        }

    async def _execute_condition_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行条件节点"""
        condition_config = node.config.get("condition", {})
        condition_expr = condition_config.get("expression", "")

        context = execution.context
        condition_result = self._evaluate_condition(condition_expr, context)

        return {
            "status": "success",
            "node_id": node.node_id,
            "condition_result": condition_result,
            "true_branch": condition_config.get("true_branch"),
            "false_branch": condition_config.get("false_branch"),
        }

    def _evaluate_condition(self, expression: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式"""
        try:
            return eval(expression, {"__builtins__": {}}, context)
        except Exception:
            return False

    async def _execute_parallel_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行并行节点"""
        parallel_config = node.config.get("parallel", {})
        parallel_tasks = parallel_config.get("tasks", [])

        self.logger.debug(
            "executing_parallel_node",
            node_id=node.node_id,
            task_count=len(parallel_tasks),
        )

        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "node_id": node.node_id,
            "completed_tasks": len(parallel_tasks),
        }

    async def _execute_loop_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行循环节点"""
        loop_config = node.config.get("loop", {})
        iterations = loop_config.get("iterations", 1)
        loop_variable = loop_config.get("variable", "i")

        self.logger.debug(
            "executing_loop_node",
            node_id=node.node_id,
            iterations=iterations,
        )

        results = []
        for i in range(iterations):
            execution.context[loop_variable] = i
            await asyncio.sleep(0.01)
            results.append({"iteration": i, "status": "success"})

        return {
            "status": "success",
            "node_id": node.node_id,
            "iterations": iterations,
            "results": results,
        }

    async def _execute_subworkflow_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行子工作流节点"""
        subworkflow_config = node.config.get("subworkflow", {})
        subworkflow_id = subworkflow_config.get("workflow_id")

        self.logger.debug(
            "executing_subworkflow_node",
            node_id=node.node_id,
            subworkflow_id=subworkflow_id,
        )

        sub_execution_id = await self.execute_workflow(
            subworkflow_id,
            parameters=execution.context,
            parent_execution_id=execution.execution_id,
        )

        return {
            "status": "success",
            "node_id": node.node_id,
            "sub_execution_id": sub_execution_id,
        }

    async def _execute_wait_node(self, execution: WorkflowExecution, node: TaskNode) -> Any:
        """执行等待节点"""
        wait_config = node.config.get("wait", {})
        duration_seconds = wait_config.get("duration_seconds", 1)

        self.logger.debug(
            "executing_wait_node",
            node_id=node.node_id,
            duration=duration_seconds,
        )

        await asyncio.sleep(duration_seconds)

        return {
            "status": "success",
            "node_id": node.node_id,
            "waited_seconds": duration_seconds,
        }

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        execution = self._executions.get(execution_id)
        if not execution:
            return None

        duration_seconds = None
        if execution.started_at:
            end_time = execution.completed_at or datetime.utcnow()
            duration_seconds = (end_time - execution.started_at).total_seconds()

        return {
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "progress": self._calculate_progress(execution),
            "node_states": {
                node_id: status.value
                for node_id, status in execution.node_states.items()
            },
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_seconds": duration_seconds,
            "parent_execution_id": execution.parent_execution_id,
        }

    def _calculate_progress(self, execution: WorkflowExecution) -> float:
        """计算执行进度"""
        total_nodes = len(execution.definition.nodes)
        if total_nodes == 0:
            return 0.0

        completed_nodes = sum(
            1 for status in execution.node_states.values()
            if status == TaskNodeStatus.COMPLETED
        )

        return (completed_nodes / total_nodes) * 100

    async def cancel_execution(self, execution_id: str) -> bool:
        """取消执行"""
        execution = self._executions.get(execution_id)
        if not execution:
            return False

        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False

        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow()

        self.logger.info("workflow_execution_cancelled", execution_id=execution_id)

        return True

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """获取工作流定义"""
        return self._workflows.get(workflow_id)

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """列出所有工作流"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "description": wf.description,
                "version": wf.version,
                "node_count": len(wf.nodes),
                "created_at": wf.created_at.isoformat(),
            }
            for wf in self._workflows.values()
        ]

    async def shutdown(self) -> None:
        """关闭工作流引擎"""
        self.logger.info("shutting_down_workflow_engine")

        for execution_id in list(self._executions.keys()):
            if self._executions[execution_id].status == WorkflowStatus.RUNNING:
                await self.cancel_execution(execution_id)

        self._is_running = False

        self.logger.info("workflow_engine_shutdown")
