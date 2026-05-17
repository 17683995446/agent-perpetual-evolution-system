"""
Prometheus Metrics Collector - Prometheus指标收集器（5个单词）

提供完整的Prometheus指标收集、暴露和监控功能。
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    start_http_server,
    REGISTRY,
)

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricDefinition:
    """指标定义"""
    name: str
    description: str
    metric_type: MetricType
    labels: list[str] = field(default_factory=list)
    buckets: Optional[list[float]] = None


@dataclass
class SystemHealthStatus:
    """系统健康状态"""
    status: str
    uptime_seconds: float
    memory_usage_percent: float
    cpu_usage_percent: float
    disk_usage_percent: float
    active_tasks: int
    active_connections: int
    timestamp: datetime


class PrometheusMetricsCollector:
    """
    Prometheus指标收集器
    
    核心职责：
    1. 收集系统级指标（CPU、内存、磁盘等）
    2. 收集业务级指标（任务、进化等）
    3. 暴露Prometheus指标端点
    4. 提供指标查询和聚合
    """

    def __init__(self, port: int = 8001):
        self.logger = get_structured_logger(__name__)
        self.port = port
        self._metrics: Dict[str, Any] = {}
        self._start_time = datetime.utcnow()
        self._server_started = False

        # 系统级指标
        self._init_system_metrics()
        # 业务级指标
        self._init_business_metrics()

    def _init_system_metrics(self):
        """初始化系统级指标"""
        # 请求计数器
        self._metrics["http_requests_total"] = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
        )
        
        # 活跃连接数
        self._metrics["active_connections"] = Gauge(
            "active_connections",
            "Number of active connections",
        )
        
        # 内存使用
        self._metrics["memory_usage_bytes"] = Gauge(
            "memory_usage_bytes",
            "Memory usage in bytes",
        )
        
        # 内存使用率
        self._metrics["memory_usage_percent"] = Gauge(
            "memory_usage_percent",
            "Memory usage percentage",
        )
        
        # CPU使用率
        self._metrics["cpu_usage_percent"] = Gauge(
            "cpu_usage_percent",
            "CPU usage percentage",
        )
        
        # 磁盘使用率
        self._metrics["disk_usage_percent"] = Gauge(
            "disk_usage_percent",
            "Disk usage percentage",
        )
        
        # 系统运行时间
        self._metrics["system_uptime_seconds"] = Gauge(
            "system_uptime_seconds",
            "System uptime in seconds",
        )

    def _init_business_metrics(self):
        """初始化业务级指标"""
        # 任务相关指标
        self._metrics["tasks_total"] = Counter(
            "tasks_total",
            "Total number of tasks",
            ["status", "priority"],
        )
        
        self._metrics["active_tasks"] = Gauge(
            "active_tasks",
            "Number of active tasks",
        )
        
        self._metrics["task_duration_seconds"] = Histogram(
            "task_duration_seconds",
            "Task duration in seconds",
            ["status"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
        )
        
        # 进化相关指标
        self._metrics["evolution_stage"] = Gauge(
            "evolution_stage",
            "Current evolution stage (1=Initializing, 2=Learning, 3=Optimizing, 4=Maturing, 5=Stable)",
        )
        
        self._metrics["patterns_learned_total"] = Counter(
            "patterns_learned_total",
            "Total number of patterns learned",
        )
        
        self._metrics["optimizations_performed_total"] = Counter(
            "optimizations_performed_total",
            "Total number of optimizations performed",
        )
        
        # 内存清理指标
        self._metrics["memory_cleanup_total"] = Counter(
            "memory_cleanup_total",
            "Total number of memory cleanups",
        )
        
        self._metrics["memory_cleaned_bytes"] = Counter(
            "memory_cleaned_bytes",
            "Total bytes cleaned from memory",
        )

    def start_metrics_server(self, port: Optional[int] = None):
        """
        启动Prometheus指标服务器
        
        Args:
            port: 指标服务器端口，默认8001
        """
        actual_port = port or self.port
        if not self._server_started:
            try:
                start_http_server(actual_port)
                self._server_started = True
                self.logger.info(
                    "prometheus_metrics_server_started",
                    port=actual_port,
                    endpoint=f"http://0.0.0.0:{actual_port}/metrics",
                )
            except Exception as e:
                self.logger.error(
                    "failed_to_start_metrics_server",
                    error=str(e),
                    port=actual_port,
                )

    def increment_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
    ):
        """
        增加HTTP请求计数
        
        Args:
            method: HTTP方法
            endpoint: 端点路径
            status_code: 状态码
        """
        self._metrics["http_requests_total"].labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).inc()

    def set_active_connections(self, count: int):
        """
        设置活跃连接数
        
        Args:
            count: 活跃连接数
        """
        self._metrics["active_connections"].set(count)

    def update_memory_usage(self, usage_bytes: int, usage_percent: float):
        """
        更新内存使用指标
        
        Args:
            usage_bytes: 内存使用量（字节）
            usage_percent: 内存使用率
        """
        self._metrics["memory_usage_bytes"].set(usage_bytes)
        self._metrics["memory_usage_percent"].set(usage_percent)

    def update_cpu_usage(self, usage_percent: float):
        """
        更新CPU使用指标
        
        Args:
            usage_percent: CPU使用率
        """
        self._metrics["cpu_usage_percent"].set(usage_percent)

    def update_disk_usage(self, usage_percent: float):
        """
        更新磁盘使用指标
        
        Args:
            usage_percent: 磁盘使用率
        """
        self._metrics["disk_usage_percent"].set(usage_percent)

    def update_uptime(self):
        """更新系统运行时间"""
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        self._metrics["system_uptime_seconds"].set(uptime)

    def increment_task_count(
        self,
        status: str,
        priority: str,
    ):
        """
        增加任务计数
        
        Args:
            status: 任务状态
            priority: 任务优先级
        """
        self._metrics["tasks_total"].labels(
            status=status,
            priority=priority,
        ).inc()

    def set_active_tasks(self, count: int):
        """
        设置活跃任务数
        
        Args:
            count: 活跃任务数
        """
        self._metrics["active_tasks"].set(count)

    def observe_task_duration(
        self,
        status: str,
        duration_seconds: float,
    ):
        """
        记录任务时长
        
        Args:
            status: 任务状态
            duration_seconds: 执行时长（秒）
        """
        self._metrics["task_duration_seconds"].labels(
            status=status,
        ).observe(duration_seconds)

    def set_evolution_stage(self, stage: int):
        """
        设置进化阶段
        
        Args:
            stage: 进化阶段 (1-5)
        """
        self._metrics["evolution_stage"].set(stage)

    def increment_patterns_learned(self):
        """增加学习到的模式计数"""
        self._metrics["patterns_learned_total"].inc()

    def increment_optimizations_performed(self):
        """增加执行的优化计数"""
        self._metrics["optimizations_performed_total"].inc()

    def record_memory_cleanup(self, cleaned_bytes: int):
        """
        记录内存清理
        
        Args:
            cleaned_bytes: 清理的字节数
        """
        self._metrics["memory_cleanup_total"].inc()
        self._metrics["memory_cleaned_bytes"].inc(cleaned_bytes)

    async def collect_system_metrics(self):
        """
        收集系统级指标
        
        定期调用此方法来更新系统指标
        """
        try:
            import psutil
            
            # 更新运行时间
            self.update_uptime()
            
            # 更新CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.update_cpu_usage(cpu_percent)
            
            # 更新内存使用
            memory = psutil.virtual_memory()
            self.update_memory_usage(
                usage_bytes=memory.used,
                usage_percent=memory.percent,
            )
            
            # 更新磁盘使用
            disk = psutil.disk_usage('/')
            self.update_disk_usage(disk.percent)
            
        except ImportError:
            self.logger.debug("psutil_not_available_skipping_system_metrics")
        except Exception as e:
            self.logger.error("failed_to_collect_system_metrics", error=str(e))

    def get_system_health_status(self) -> SystemHealthStatus:
        """
        获取系统健康状态
        
        Returns:
            系统健康状态对象
        """
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return SystemHealthStatus(
            status="healthy",
            uptime_seconds=uptime,
            memory_usage_percent=self._get_metric_value(
                "memory_usage_percent", 0.0
            ),
            cpu_usage_percent=self._get_metric_value(
                "cpu_usage_percent", 0.0
            ),
            disk_usage_percent=self._get_metric_value(
                "disk_usage_percent", 0.0
            ),
            active_tasks=self._get_metric_value(
                "active_tasks", 0
            ),
            active_connections=self._get_metric_value(
                "active_connections", 0
            ),
            timestamp=datetime.utcnow(),
        )

    def _get_metric_value(self, metric_name: str, default: Any) -> Any:
        """
        获取指标当前值（辅助方法）
        
        Args:
            metric_name: 指标名称
            default: 默认值
            
        Returns:
            指标值
        """
        try:
            metric = self._metrics.get(metric_name)
            if metric is not None:
                # 使用 Prometheus 的内部 API 获取值
                # 注意：这是一个简化实现，实际生产环境可能需要更复杂的逻辑
                return metric.__dict__.get('_value', default)
            return default
        except Exception:
            return default
