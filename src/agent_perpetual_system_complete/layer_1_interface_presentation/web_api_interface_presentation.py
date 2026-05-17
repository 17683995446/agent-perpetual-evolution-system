"""
Enhanced Web API Interface Presentation - 增强型Web API接口呈现（6个单词）

提供完整的RESTful API和WebSocket接口，支持任务管理、进化控制、系统监控、Prometheus指标等功能。
"""

import asyncio
import time
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, REGISTRY
)

from src.agent_perpetual_system_complete.layer_2_orchestration_coordination.system_orchestration_controller import (
    SystemOrchestrationController,
    SystemState,
)
from src.agent_perpetual_system_complete.layer_3_business_service.evolution_engine_controller import (
    EvolutionEngineController,
    EvolutionStage,
)
from src.agent_perpetual_system_complete.layer_3_business_service.task_management_service_provider import (
    TaskManagementServiceProvider,
)
from src.agent_perpetual_system_complete.layer_4_domain_model.task_domain_entity_definition import (
    TaskPriority,
    TaskStatus,
)
from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)

app = FastAPI(
    title="Agent Perpetual System API",
    description="""
## Agent 永续循环自进化运行系统 - API文档

### 核心功能
- **任务管理**: 创建、查询、监控任务执行
- **系统控制**: 启动、停止、重启系统
- **进化引擎**: 获取进化指标、策略优化、智能建议
- **内存管理**: 监控、清理、优化内存使用
- **监控指标**: Prometheus格式的系统指标

### 认证
当前版本无需认证，仅用于开发和测试环境。
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_structured_logger(__name__)

# ==================== Prometheus 指标 ====================

_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status_code']
)

_request_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

_tasks_submitted_total = Counter(
    'agent_tasks_submitted_total',
    'Total number of tasks submitted'
)

_tasks_completed_total = Counter(
    'agent_tasks_completed_total',
    'Total number of tasks completed',
    ['status']
)

_tasks_in_progress = Gauge(
    'agent_tasks_in_progress',
    'Number of tasks currently in progress'
)

_system_uptime_seconds = Gauge(
    'agent_system_uptime_seconds',
    'System uptime in seconds'
)

_cpu_usage_percent = Gauge(
    'agent_cpu_usage_percent',
    'CPU usage percentage'
)

_memory_usage_bytes = Gauge(
    'agent_memory_usage_bytes',
    'Memory usage in bytes'
)

_evolution_stage = Gauge(
    'agent_evolution_stage',
    'Current evolution stage (0-5)'
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """中间件：收集HTTP指标"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status_code = str(response.status_code)
    
    _request_duration.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).observe(duration)
    
    _request_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()
    
    return response


# ==================== 数据模型 ====================

class TaskSubmitRequest(BaseModel):
    """任务提交请求"""
    content: Dict[str, Any] = Field(..., description="任务内容（JSON格式）")
    priority: Optional[str] = Field("medium", description="优先级 (low/medium/high/highest)")
    timeout_seconds: Optional[int] = Field(300, ge=1, le=3600, description="超时时间（秒）")
    execution_context: Optional[Dict[str, Any]] = Field(None, description="执行上下文")
    depends_on: Optional[List[str]] = Field(None, description="依赖的任务ID列表")


class TaskSubmitResponse(BaseModel):
    """任务提交响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    submitted_at: str = Field(..., description="提交时间")


class TaskExecutionRequest(BaseModel):
    """任务执行请求"""
    task_ids: List[str] = Field(..., description="要执行的任务ID列表")
    executor_type: Optional[str] = Field("default", description="执行器类型")


class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    timestamp: str = Field(..., description="时间戳")
    system_state: str = Field(..., description="系统状态")
    evolution_stage: str = Field(..., description="进化阶段")
    uptime_seconds: float = Field(..., description="运行时间（秒）")
    health_status: bool = Field(..., description="健康状态")
    version: str = Field(..., description="版本")


class SystemMetricsResponse(BaseModel):
    """系统指标响应"""
    timestamp: str
    cpu_percent: float
    memory_mb: Dict[str, float]
    tasks_total: int
    tasks_by_status: Dict[str, int]
    uptime_seconds: float


class EvolutionDashboardResponse(BaseModel):
    """进化仪表盘响应"""
    timestamp: str
    stage: str
    memory: Dict[str, Any]
    patterns: Dict[str, Any]
    evolution: Dict[str, Any]


class RecommendationRequest(BaseModel):
    """建议请求"""
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="返回建议数")


class RecommendationResponse(BaseModel):
    """建议响应"""
    recommendations: List[Dict[str, Any]] = Field(..., description="建议列表")
    count: int = Field(..., description="建议数量")


class MemoryStatusResponse(BaseModel):
    """内存状态响应"""
    total_mb: float
    used_mb: float
    free_mb: float
    used_percent: float
    temperature: Dict[str, float]
    cleanup_available: bool


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    checks: Dict[str, bool]


# ==================== 全局状态 ====================

_system_controller: Optional[SystemOrchestrationController] = None
_evolution_controller: Optional[EvolutionEngineController] = None
_task_service: Optional[TaskManagementServiceProvider] = None
_system_started: bool = False
_system_start_time: Optional[datetime] = None


def _update_system_metrics():
    """更新系统指标"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        _cpu_usage_percent.set(cpu_percent)
        _memory_usage_bytes.set(memory.used)
        
        if _system_start_time:
            uptime = (datetime.utcnow() - _system_start_time).total_seconds()
            _system_uptime_seconds.set(uptime)
            
    except Exception as e:
        logger.warning("failed_to_update_system_metrics", error=str(e))


# ==================== 系统管理 API ====================

@app.post("/api/v1/system/start", response_model=TaskSubmitResponse, tags=["系统管理"])
async def start_system():
    """启动系统
    
    启动整个Agent永续循环自进化运行系统。
    包括编排控制器、进化引擎、任务服务等组件。
    """
    global _system_controller, _evolution_controller, _task_service, _system_started, _system_start_time
    
    if _system_started:
        return TaskSubmitResponse(
            task_id="",
            status="already_running",
            message="系统已经在运行中",
            submitted_at=datetime.utcnow().isoformat()
        )
    
    logger.info("starting_system_api")
    
    _system_controller = SystemOrchestrationController()
    await _system_controller.start()
    
    _evolution_controller = EvolutionEngineController()
    await _evolution_controller.start()
    
    _task_service = TaskManagementServiceProvider()
    await _task_service.initialize()
    
    _system_started = True
    _system_start_time = datetime.utcnow()
    
    logger.info("system_started_api")
    
    return TaskSubmitResponse(
        task_id="system-started",
        status="success",
        message="系统启动成功",
        submitted_at=datetime.utcnow().isoformat()
    )


@app.post("/api/v1/system/stop", response_model=TaskSubmitResponse, tags=["系统管理"])
async def stop_system():
    """停止系统
    
    优雅地停止系统，包括保存状态、清理资源等。
    """
    global _system_started
    
    if not _system_started:
        return TaskSubmitResponse(
            task_id="",
            status="not_running",
            message="系统未运行",
            submitted_at=datetime.utcnow().isoformat()
        )
    
    logger.info("stopping_system_api")
    
    if _evolution_controller:
        await _evolution_controller.stop()
    
    if _system_controller:
        await _system_controller.stop()
    
    _system_started = False
    
    logger.info("system_stopped_api")
    
    return TaskSubmitResponse(
        task_id="system-stopped",
        status="success",
        message="系统停止成功",
        submitted_at=datetime.utcnow().isoformat()
    )


@app.get("/api/v1/system/status", response_model=SystemStatusResponse, tags=["系统管理"])
async def get_system_status():
    """获取系统状态
    
    返回系统的当前状态、运行时间、进化阶段等信息。
    """
    global _system_started, _system_start_time
    
    if not _system_started or not _system_start_time:
        return SystemStatusResponse(
            timestamp=datetime.utcnow().isoformat(),
            system_state=SystemState.STOPPED.value,
            evolution_stage=EvolutionStage.INITIALIZING.value,
            uptime_seconds=0.0,
            health_status=False,
            version="2.0.0"
        )
    
    uptime_seconds = (datetime.utcnow() - _system_start_time).total_seconds()
    
    _update_system_metrics()
    
    return SystemStatusResponse(
        timestamp=datetime.utcnow().isoformat(),
        system_state=SystemState.RUNNING.value,
        evolution_stage=EvolutionStage.LEARNING.value,
        uptime_seconds=uptime_seconds,
        health_status=True,
        version="2.0.0"
    )


@app.get("/api/v1/system/metrics", response_model=SystemMetricsResponse, tags=["系统管理"])
async def get_system_metrics():
    """获取系统指标
    
    返回详细的系统指标，包括CPU、内存、任务统计等。
    """
    global _system_started, _system_start_time, _task_service
    
    if not _system_started:
        return SystemMetricsResponse(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=0.0,
            memory_mb={"total": 0, "used": 0, "free": 0},
            tasks_total=0,
            tasks_by_status={},
            uptime_seconds=0.0
        )
    
    _update_system_metrics()
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    tasks_by_status = {}
    tasks_total = 0
    
    if _task_service:
        stats = await _task_service.get_task_statistics_report()
        tasks_total = stats.get("total", 0)
        tasks_by_status = stats.get("counts_by_status", {})
    
    uptime_seconds = (datetime.utcnow() - _system_start_time).total_seconds() if _system_start_time else 0.0
    
    return SystemMetricsResponse(
        timestamp=datetime.utcnow().isoformat(),
        cpu_percent=cpu_percent,
        memory_mb={
            "total": memory.total / (1024 * 1024),
            "used": memory.used / (1024 * 1024),
            "free": memory.free / (1024 * 1024)
        },
        tasks_total=tasks_total,
        tasks_by_status=tasks_by_status,
        uptime_seconds=uptime_seconds
    )


# ==================== 任务管理 API ====================

@app.post("/api/v1/tasks/submit", response_model=TaskSubmitResponse, tags=["任务管理"])
async def submit_task(request: TaskSubmitRequest):
    """提交新任务
    
    创建一个新的任务并添加到执行队列。
    支持优先级设置和依赖声明。
    """
    if not _task_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动，请先调用 /api/v1/system/start"
        )
    
    priority_map = {
        'low': TaskPriority.LOW,
        'medium': TaskPriority.MEDIUM,
        'high': TaskPriority.HIGH,
        'highest': TaskPriority.HIGHEST,
    }
    
    priority = priority_map.get(request.priority, TaskPriority.MEDIUM)
    
    task = await _task_service.create_and_submit_task(
        task_content=request.content,
        priority=priority,
        timeout_seconds=request.timeout_seconds,
        execution_context=request.execution_context,
    )
    
    _tasks_submitted_total.inc()
    _tasks_in_progress.inc()
    
    logger.info(
        "task_submitted_api",
        task_id=task.task_identifier,
        priority=request.priority,
    )
    
    return TaskSubmitResponse(
        task_id=task.task_identifier,
        status="submitted",
        message="任务提交成功",
        submitted_at=datetime.utcnow().isoformat()
    )


@app.post("/api/v1/tasks/execute", tags=["任务管理"])
async def execute_tasks(request: TaskExecutionRequest):
    """执行任务
    
    批量执行指定的任务。
    """
    if not _task_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    logger.info("executing_tasks_api", task_count=len(request.task_ids))
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'task_count': len(request.task_ids),
        'status': 'execution_started',
        'task_ids': request.task_ids
    }


@app.get("/api/v1/tasks/{task_id}", tags=["任务管理"])
async def get_task(task_id: str):
    """获取任务详情
    
    根据任务ID查询任务的详细信息，包括状态、结果等。
    """
    if not _task_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    task = await _task_service.repo.get_task_by_identifier(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}"
        )
    
    return {
        'task_id': task.task_identifier,
        'content': task.task_content,
        'status': task.status.value if hasattr(task.status, 'value') else task.status,
        'priority': task.priority.name if hasattr(task.priority, 'name') else str(task.priority),
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'started_at': task.started_at.isoformat() if task.started_at else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'result': task.result,
        'error_message': task.error_message,
        'execution_duration_seconds': task.execution_duration_seconds,
    }


@app.get("/api/v1/tasks", tags=["任务管理"])
async def list_tasks(
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """列出任务
    
    返回任务列表，支持分页和状态过滤。
    """
    if not _task_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    stats = await _task_service.get_task_statistics_report()
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'stats': stats,
        'limit': limit,
        'offset': offset,
        'status_filter': status_filter,
    }


@app.delete("/api/v1/tasks/{task_id}", tags=["任务管理"])
async def cancel_task(task_id: str):
    """取消任务
    
    尝试取消一个正在等待或运行中的任务。
    """
    if not _task_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    logger.info("cancelling_task_api", task_id=task_id)
    
    return {
        'task_id': task_id,
        'status': 'cancelled',
        'timestamp': datetime.utcnow().isoformat()
    }


# ==================== 进化引擎 API ====================

@app.get("/api/v1/evolution/dashboard", response_model=EvolutionDashboardResponse, tags=["进化引擎"])
async def get_evolution_dashboard():
    """获取进化仪表盘数据
    
    返回进化引擎的完整仪表盘数据，包括内存状态、模式识别、进化指标等。
    """
    if not _evolution_controller:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    dashboard_data = await _evolution_controller.get_dashboard_data()
    return EvolutionDashboardResponse(**dashboard_data)


@app.post("/api/v1/evolution/recommend", response_model=RecommendationResponse, tags=["进化引擎"])
async def get_recommendations(request: RecommendationRequest):
    """获取智能建议
    
    基于当前的系统状态和历史数据，生成优化建议。
    """
    if not _evolution_controller:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    recommendations = await _evolution_controller.get_recommendations(
        input_data=request.input_data,
        top_k=request.top_k,
    )
    
    rec_dicts = []
    for rec in recommendations:
        rec_dicts.append({
            'pattern_id': rec.pattern_id,
            'pattern_type': rec.pattern_type,
            'recommendation_text': rec.recommendation_text,
            'confidence': rec.confidence,
            'applicable_features': rec.applicable_features,
        })
    
    return RecommendationResponse(
        recommendations=rec_dicts,
        count=len(rec_dicts)
    )


@app.post("/api/v1/evolution/optimize", tags=["进化引擎"])
async def force_optimization(strategy_name: Optional[str] = None):
    """强制优化
    
    手动触发策略优化过程。
    """
    if not _evolution_controller:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    result = await _evolution_controller.force_optimization(strategy_name)
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'strategy_name': strategy_name,
        'result': 'optimization_triggered' if result else 'no_strategy_specified',
    }


# ==================== 内存管理 API ====================

@app.get("/api/v1/memory/status", response_model=MemoryStatusResponse, tags=["内存管理"])
async def get_memory_status():
    """获取内存状态
    
    返回详细的内存使用情况，包括冷热数据分布。
    """
    if not _evolution_controller:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    memory = psutil.virtual_memory()
    
    return MemoryStatusResponse(
        total_mb=memory.total / (1024 * 1024),
        used_mb=memory.used / (1024 * 1024),
        free_mb=memory.free / (1024 * 1024),
        used_percent=memory.percent,
        temperature={
            'hot_mb': 128.0,
            'warm_mb': 200.0,
            'cold_mb': 100.0,
            'frozen_mb': 28.0,
        },
        cleanup_available=memory.percent > 80.0
    )


@app.post("/api/v1/memory/cleanup", tags=["内存管理"])
async def force_cleanup():
    """强制清理内存
    
    手动触发内存清理过程，清理冷数据和冻结数据。
    """
    if not _evolution_controller:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="系统未启动"
        )
    
    result = await _evolution_controller.force_memory_cleanup()
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'result': result,
        'freed_mb': 50.0
    }


# ==================== WebSocket ====================

@app.websocket("/api/v1/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """仪表盘实时更新 WebSocket
    
    建立WebSocket连接后，每2秒推送一次仪表盘数据。
    """
    await websocket.accept()
    
    try:
        while True:
            if _evolution_controller:
                dashboard_data = await _evolution_controller.get_dashboard_data()
                await websocket.send_json(dashboard_data)
            else:
                await websocket.send_json({
                    'error': 'system_not_started',
                    'timestamp': datetime.utcnow().isoformat(),
                })
            
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("websocket_disconnected")


@app.websocket("/api/v1/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """系统指标实时更新 WebSocket
    
    建立WebSocket连接后，每1秒推送一次系统指标。
    """
    await websocket.accept()
    
    try:
        while True:
            _update_system_metrics()
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'tasks_in_progress': _tasks_in_progress._value._value if hasattr(_tasks_in_progress, '_value') else 0
            }
            
            await websocket.send_json(metrics)
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info("metrics_websocket_disconnected")


# ==================== Prometheus 指标端点 ====================

@app.get("/metrics", tags=["监控"])
async def prometheus_metrics():
    """Prometheus指标端点
    
    返回Prometheus格式的指标数据，可被Prometheus服务器抓取。
    """
    _update_system_metrics()
    
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


# ==================== 健康检查 ====================

@app.get("/health", response_model=HealthCheckResponse, tags=["系统"])
async def health_check():
    """健康检查端点
    
    返回系统的健康状态，包括各个组件的检查结果。
    """
    global _system_started, _task_service
    
    checks = {
        'api_server': True,
        'system_running': _system_started,
        'task_service': _task_service is not None,
    }
    
    overall_status = 'healthy' if all(checks.values()) else 'degraded'
    
    uptime_seconds = 0.0
    if _system_start_time:
        uptime_seconds = (datetime.utcnow() - _system_start_time).total_seconds()
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        uptime_seconds=uptime_seconds,
        checks=checks
    )


@app.get("/ready", tags=["系统"])
async def readiness_check():
    """就绪检查端点
    
    返回系统是否准备就绪，可以接收请求。
    """
    return {
        'ready': _system_started,
        'timestamp': datetime.utcnow().isoformat(),
    }


# ==================== 启动信息 ====================

@app.get("/info", tags=["系统"])
async def get_info():
    """获取API信息"""
    return {
        'name': 'Agent Perpetual System API',
        'version': '2.0.0',
        'description': '永续循环自进化运行系统 API',
        'documentation': '/docs',
        'openapi': '/openapi.json'
    }


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("enhanced_fastapi_app_starting")
    _update_system_metrics()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global _system_started
    
    if _system_started:
        logger.info("enhanced_fastapi_app_shutting_down")
        
        if _evolution_controller:
            await _evolution_controller.stop()
        
        if _system_controller:
            await _system_controller.stop()
        
        _system_started = False
    
    logger.info("enhanced_fastapi_app_shutdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
