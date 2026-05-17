"""
Performance Monitor Service - 性能监控服务（4个单词）

提供系统性能监控、指标采集、趋势分析功能。
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_tasks: int
    requests_per_second: float
    average_response_time: float
    error_rate: float


@dataclass
class PerformanceAlert:
    """性能告警"""
    alert_id: str
    level: AlertLevel
    metric: str
    message: str
    threshold_value: float
    current_value: float
    timestamp: datetime


class PerformanceMonitorService:
    """
    性能监控服务
    
    核心职责：
    1. 实时性能指标采集
    2. 性能趋势分析
    3. 告警条件检测
    4. 历史数据存储和查询
    """

    def __init__(
        self,
        history_size: int = 3600,  # 默认保留1小时数据
        check_interval_seconds: int = 10,
    ):
        self.logger = get_structured_logger(__name__)
        self.history_size = history_size
        self.check_interval_seconds = check_interval_seconds

        # 性能历史数据
        self._performance_history: deque[PerformanceSnapshot] = deque(maxlen=history_size)
        self._alerts: deque[PerformanceAlert] = deque(maxlen=1000)

        # 告警阈值配置
        self._alert_thresholds: Dict[str, Dict[str, float]] = {
            "cpu": {"warning": 80.0, "critical": 95.0},
            "memory": {"warning": 80.0, "critical": 95.0},
            "disk": {"warning": 90.0, "critical": 98.0},
            "error_rate": {"warning": 5.0, "critical": 20.0},
        }

        # 请求统计
        self._request_count = 0
        self._error_count = 0
        self._response_time_sum = 0.0
        self._last_reset_time = datetime.utcnow()

        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self):
        """启动性能监控服务"""
        if self._is_running:
            self.logger.warning("performance_monitor_already_running")
            return

        self.logger.info("starting_performance_monitor_service")
        self._is_running = True
        self._last_reset_time = datetime.utcnow()

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.info("performance_monitor_service_started")

    async def stop(self):
        """停止性能监控服务"""
        if not self._is_running:
            self.logger.warning("performance_monitor_not_running")
            return

        self.logger.info("stopping_performance_monitor_service")
        self._is_running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self.logger.info("performance_monitor_service_stopped")

    def record_request(self, response_time_seconds: float, is_error: bool = False):
        """
        记录请求性能数据
        
        Args:
            response_time_seconds: 响应时间（秒）
            is_error: 是否是错误请求
        """
        self._request_count += 1
        self._response_time_sum += response_time_seconds
        if is_error:
            self._error_count += 1

    def record_task_completion(self, duration_seconds: float, is_success: bool):
        """
        记录任务完成性能数据
        
        Args:
            duration_seconds: 任务执行时长（秒）
            is_success: 是否成功
        """
        if not is_success:
            self._error_count += 1

    async def _monitoring_loop(self):
        """监控主循环"""
        self.logger.info("performance_monitoring_loop_started")

        while self._is_running:
            try:
                await asyncio.sleep(self.check_interval_seconds)

                # 采集性能快照
                snapshot = await self._collect_snapshot()
                self._performance_history.append(snapshot)

                # 检查告警条件
                await self._check_alerts(snapshot)

                # 定期重置计数器（每分钟）
                now = datetime.utcnow()
                if (now - self._last_reset_time).total_seconds() >= 60:
                    self._reset_counters()
                    self._last_reset_time = now

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("performance_monitoring_loop_error", error=str(e))

        self.logger.info("performance_monitoring_loop_stopped")

    async def _collect_snapshot(self) -> PerformanceSnapshot:
        """
        采集性能快照
        
        Returns:
            性能快照对象
        """
        cpu_percent = 0.0
        memory_percent = 0.0
        disk_percent = 0.0

        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

        except ImportError:
            self.logger.debug("psutil_not_available_using_default_metrics")
        except Exception as e:
            self.logger.error("failed_to_collect_system_metrics", error=str(e))

        # 计算请求相关指标
        now = datetime.utcnow()
        time_span = (now - self._last_reset_time).total_seconds()

        requests_per_second = 0.0
        average_response_time = 0.0
        error_rate = 0.0

        if time_span > 0 and self._request_count > 0:
            requests_per_second = self._request_count / time_span
            average_response_time = self._response_time_sum / self._request_count
            error_rate = (self._error_count / self._request_count) * 100

        return PerformanceSnapshot(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            active_tasks=0,  # 实际应从任务服务获取
            requests_per_second=requests_per_second,
            average_response_time=average_response_time,
            error_rate=error_rate,
        )

    async def _check_alerts(self, snapshot: PerformanceSnapshot):
        """
        检查告警条件
        
        Args:
            snapshot: 当前性能快照
        """
        alerts = []

        # 检查CPU
        if snapshot.cpu_percent > self._alert_thresholds["cpu"]["critical"]:
            alerts.append(self._create_alert(
                metric="cpu",
                level=AlertLevel.CRITICAL,
                message=f"CPU usage critically high: {snapshot.cpu_percent}%",
                threshold_value=self._alert_thresholds["cpu"]["critical"],
                current_value=snapshot.cpu_percent,
            ))
        elif snapshot.cpu_percent > self._alert_thresholds["cpu"]["warning"]:
            alerts.append(self._create_alert(
                metric="cpu",
                level=AlertLevel.WARNING,
                message=f"CPU usage high: {snapshot.cpu_percent}%",
                threshold_value=self._alert_thresholds["cpu"]["warning"],
                current_value=snapshot.cpu_percent,
            ))

        # 检查内存
        if snapshot.memory_percent > self._alert_thresholds["memory"]["critical"]:
            alerts.append(self._create_alert(
                metric="memory",
                level=AlertLevel.CRITICAL,
                message=f"Memory usage critically high: {snapshot.memory_percent}%",
                threshold_value=self._alert_thresholds["memory"]["critical"],
                current_value=snapshot.memory_percent,
            ))
        elif snapshot.memory_percent > self._alert_thresholds["memory"]["warning"]:
            alerts.append(self._create_alert(
                metric="memory",
                level=AlertLevel.WARNING,
                message=f"Memory usage high: {snapshot.memory_percent}%",
                threshold_value=self._alert_thresholds["memory"]["warning"],
                current_value=snapshot.memory_percent,
            ))

        # 检查磁盘
        if snapshot.disk_percent > self._alert_thresholds["disk"]["critical"]:
            alerts.append(self._create_alert(
                metric="disk",
                level=AlertLevel.CRITICAL,
                message=f"Disk usage critically high: {snapshot.disk_percent}%",
                threshold_value=self._alert_thresholds["disk"]["critical"],
                current_value=snapshot.disk_percent,
            ))
        elif snapshot.disk_percent > self._alert_thresholds["disk"]["warning"]:
            alerts.append(self._create_alert(
                metric="disk",
                level=AlertLevel.WARNING,
                message=f"Disk usage high: {snapshot.disk_percent}%",
                threshold_value=self._alert_thresholds["disk"]["warning"],
                current_value=snapshot.disk_percent,
            ))

        # 检查错误率
        if snapshot.error_rate > self._alert_thresholds["error_rate"]["critical"]:
            alerts.append(self._create_alert(
                metric="error_rate",
                level=AlertLevel.CRITICAL,
                message=f"Error rate critically high: {snapshot.error_rate}%",
                threshold_value=self._alert_thresholds["error_rate"]["critical"],
                current_value=snapshot.error_rate,
            ))
        elif snapshot.error_rate > self._alert_thresholds["error_rate"]["warning"]:
            alerts.append(self._create_alert(
                metric="error_rate",
                level=AlertLevel.WARNING,
                message=f"Error rate high: {snapshot.error_rate}%",
                threshold_value=self._alert_thresholds["error_rate"]["warning"],
                current_value=snapshot.error_rate,
            ))

        # 记录告警
        for alert in alerts:
            self._alerts.append(alert)
            self.logger.warning(
                "performance_alert",
                alert_id=alert.alert_id,
                level=alert.level.value,
                metric=alert.metric,
                message=alert.message,
            )

    def _create_alert(
        self,
        metric: str,
        level: AlertLevel,
        message: str,
        threshold_value: float,
        current_value: float,
    ) -> PerformanceAlert:
        """
        创建告警对象
        
        Returns:
            性能告警对象
        """
        import uuid
        return PerformanceAlert(
            alert_id=str(uuid.uuid4()),
            level=level,
            metric=metric,
            message=message,
            threshold_value=threshold_value,
            current_value=current_value,
            timestamp=datetime.utcnow(),
        )

    def _reset_counters(self):
        """重置计数器"""
        self._request_count = 0
        self._error_count = 0
        self._response_time_sum = 0.0

    def get_current_snapshot(self) -> Optional[PerformanceSnapshot]:
        """
        获取最新性能快照
        
        Returns:
            最新性能快照，如果没有则返回None
        """
        if not self._performance_history:
            return None
        return self._performance_history[-1]

    def get_history(
        self,
        last_minutes: Optional[int] = None,
    ) -> List[PerformanceSnapshot]:
        """
        获取性能历史数据
        
        Args:
            last_minutes: 最近多少分钟的数据，None表示全部
            
        Returns:
            性能快照列表
        """
        if not last_minutes:
            return list(self._performance_history)

        cutoff_time = datetime.utcnow() - timedelta(minutes=last_minutes)
        return [
            snapshot for snapshot in self._performance_history
            if snapshot.timestamp >= cutoff_time
        ]

    def get_recent_alerts(
        self,
        count: int = 50,
        level: Optional[AlertLevel] = None,
    ) -> List[PerformanceAlert]:
        """
        获取最近的告警
        
        Args:
            count: 返回数量
            level: 告警级别过滤
            
        Returns:
            告警列表
        """
        alerts = list(self._alerts)

        if level:
            alerts = [alert for alert in alerts if alert.level == level]

        return alerts[-count:]

    def get_statistics(
        self,
        last_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取统计数据
        
        Args:
            last_minutes: 时间范围
            
        Returns:
            统计数据字典
        """
        history = self.get_history(last_minutes)

        if not history:
            return {}

        cpu_values = [s.cpu_percent for s in history]
        memory_values = [s.memory_percent for s in history]
        disk_values = [s.disk_percent for s in history]

        return {
            "sample_count": len(history),
            "cpu": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": sum(cpu_values) / len(cpu_values),
            },
            "memory": {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": sum(memory_values) / len(memory_values),
            },
            "disk": {
                "min": min(disk_values),
                "max": max(disk_values),
                "avg": sum(disk_values) / len(disk_values),
            },
        }

    def update_alert_threshold(
        self,
        metric: str,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
    ):
        """
        更新告警阈值
        
        Args:
            metric: 指标名称
            warning_threshold: 警告阈值
            critical_threshold: 严重阈值
        """
        if metric not in self._alert_thresholds:
            self.logger.warning("unknown_metric_for_alert_threshold", metric=metric)
            return

        if warning_threshold is not None:
            self._alert_thresholds[metric]["warning"] = warning_threshold

        if critical_threshold is not None:
            self._alert_thresholds[metric]["critical"] = critical_threshold

        self.logger.info(
            "alert_threshold_updated",
            metric=metric,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
        )
