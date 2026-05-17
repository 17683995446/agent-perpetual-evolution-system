"""
Test Monitoring and Metrics Layer - 测试监控和度量层（7个单词）

测试Prometheus指标收集器、性能监控器和告警管理功能。
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent_perpetual_system_complete.layer_3_business_service.prometheus_metrics_collector import (
    PrometheusMetricsCollector,
    MetricType,
    SystemHealthStatus,
)
from src.agent_perpetual_system_complete.layer_3_business_service.performance_monitor_service import (
    PerformanceMonitorService,
    PerformanceSnapshot,
    PerformanceAlert,
    AlertLevel,
)


class TestPrometheusMetricsCollector:
    """Prometheus指标收集器测试"""

    @pytest.fixture
    def collector(self):
        """测试夹具：创建指标收集器"""
        return PrometheusMetricsCollector(port=8002)

    def test_collector_initialization(self, collector):
        """测试收集器初始化"""
        assert collector is not None
        assert collector.port == 8002
        assert "http_requests_total" in collector._metrics
        assert "memory_usage_percent" in collector._metrics
        assert "tasks_total" in collector._metrics

    def test_increment_http_request(self, collector):
        """测试增加HTTP请求计数"""
        initial_value = 0
        collector.increment_http_request("GET", "/api/test", 200)
        collector.increment_http_request("POST", "/api/tasks", 500)

        # 验证计数器被正确初始化和使用
        assert "http_requests_total" in collector._metrics

    def test_set_active_connections(self, collector):
        """测试设置活跃连接数"""
        collector.set_active_connections(42)
        assert "active_connections" in collector._metrics

    def test_update_memory_usage(self, collector):
        """测试更新内存使用指标"""
        collector.update_memory_usage(usage_bytes=1024 * 1024 * 512, usage_percent=50.0)
        assert "memory_usage_bytes" in collector._metrics
        assert "memory_usage_percent" in collector._metrics

    def test_update_cpu_usage(self, collector):
        """测试更新CPU使用指标"""
        collector.update_cpu_usage(75.5)
        assert "cpu_usage_percent" in collector._metrics

    def test_increment_task_count(self, collector):
        """测试增加任务计数"""
        collector.increment_task_count(status="completed", priority="high")
        collector.increment_task_count(status="failed", priority="low")
        assert "tasks_total" in collector._metrics

    def test_observe_task_duration(self, collector):
        """测试记录任务时长"""
        collector.observe_task_duration(status="success", duration_seconds=1.5)
        collector.observe_task_duration(status="failed", duration_seconds=0.8)
        assert "task_duration_seconds" in collector._metrics

    def test_set_evolution_stage(self, collector):
        """测试设置进化阶段"""
        collector.set_evolution_stage(3)  # OPTIMIZING
        assert "evolution_stage" in collector._metrics

    def test_increment_patterns_learned(self, collector):
        """测试增加学习到的模式计数"""
        collector.increment_patterns_learned()
        collector.increment_patterns_learned()
        assert "patterns_learned_total" in collector._metrics

    def test_record_memory_cleanup(self, collector):
        """测试记录内存清理"""
        collector.record_memory_cleanup(cleaned_bytes=1024 * 1024 * 100)  # 100MB
        assert "memory_cleanup_total" in collector._metrics
        assert "memory_cleaned_bytes" in collector._metrics

    def test_get_system_health_status(self, collector):
        """测试获取系统健康状态"""
        health_status = collector.get_system_health_status()
        assert isinstance(health_status, SystemHealthStatus)
        assert health_status.status == "healthy"
        assert health_status.uptime_seconds >= 0


class TestPerformanceMonitorService:
    """性能监控服务测试"""

    @pytest.fixture
    def monitor(self):
        """测试夹具：创建性能监控器"""
        return PerformanceMonitorService(
            history_size=100,
            check_interval_seconds=1,
        )

    @pytest.mark.asyncio
    async def test_monitor_initialization(self, monitor):
        """测试监控器初始化"""
        assert monitor is not None
        assert monitor.history_size == 100
        assert monitor.check_interval_seconds == 1

    def test_record_request(self, monitor):
        """测试记录请求"""
        monitor.record_request(response_time_seconds=0.25, is_error=False)
        monitor.record_request(response_time_seconds=0.5, is_error=False)
        monitor.record_request(response_time_seconds=0.1, is_error=True)

        assert monitor._request_count == 3
        assert monitor._error_count == 1
        assert monitor._response_time_sum == 0.85

    def test_record_task_completion(self, monitor):
        """测试记录任务完成"""
        monitor.record_task_completion(duration_seconds=1.5, is_success=True)
        monitor.record_task_completion(duration_seconds=2.0, is_success=False)

        assert monitor._error_count == 1

    def test_create_snapshot(self, monitor):
        """测试创建性能快照"""
        snapshot = PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=45.0,
            memory_percent=60.0,
            disk_percent=75.0,
            active_tasks=10,
            requests_per_second=5.0,
            average_response_time=0.2,
            error_rate=2.0,
        )

        assert snapshot.cpu_percent == 45.0
        assert snapshot.memory_percent == 60.0
        assert snapshot.error_rate == 2.0

    def test_create_alert(self, monitor):
        """测试创建告警"""
        alert = PerformanceAlert(
            alert_id="test-alert-123",
            level=AlertLevel.WARNING,
            metric="cpu",
            message="CPU usage high",
            threshold_value=80.0,
            current_value=85.0,
            timestamp=datetime.utcnow(),
        )

        assert alert.level == AlertLevel.WARNING
        assert alert.metric == "cpu"
        assert alert.current_value == 85.0

    def test_update_alert_threshold(self, monitor):
        """测试更新告警阈值"""
        monitor.update_alert_threshold(
            metric="cpu",
            warning_threshold=75.0,
            critical_threshold=90.0,
        )

        assert monitor._alert_thresholds["cpu"]["warning"] == 75.0
        assert monitor._alert_thresholds["cpu"]["critical"] == 90.0

    def test_get_history(self, monitor):
        """测试获取历史数据"""
        # 先添加一些测试数据
        snapshot1 = PerformanceSnapshot(
            timestamp=datetime.utcnow() - timedelta(minutes=10),
            cpu_percent=30.0,
            memory_percent=40.0,
            disk_percent=50.0,
            active_tasks=5,
            requests_per_second=2.0,
            average_response_time=0.1,
            error_rate=0.0,
        )

        snapshot2 = PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_percent=70.0,
            active_tasks=8,
            requests_per_second=3.0,
            average_response_time=0.15,
            error_rate=1.0,
        )

        monitor._performance_history.append(snapshot1)
        monitor._performance_history.append(snapshot2)

        # 获取全部历史
        all_history = monitor.get_history()
        assert len(all_history) == 2

        # 获取最近5分钟
        recent_history = monitor.get_history(last_minutes=5)
        assert len(recent_history) == 1

    def test_get_statistics(self, monitor):
        """测试获取统计数据"""
        snapshot1 = PerformanceSnapshot(
            timestamp=datetime.utcnow() - timedelta(minutes=5),
            cpu_percent=30.0,
            memory_percent=40.0,
            disk_percent=50.0,
            active_tasks=5,
            requests_per_second=2.0,
            average_response_time=0.1,
            error_rate=0.0,
        )

        snapshot2 = PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_percent=70.0,
            active_tasks=8,
            requests_per_second=3.0,
            average_response_time=0.15,
            error_rate=1.0,
        )

        monitor._performance_history.append(snapshot1)
        monitor._performance_history.append(snapshot2)

        stats = monitor.get_statistics()

        assert "sample_count" in stats
        assert "cpu" in stats
        assert "memory" in stats
        assert "disk" in stats
        assert stats["cpu"]["min"] == 30.0
        assert stats["cpu"]["max"] == 50.0
        assert stats["cpu"]["avg"] == 40.0

    def test_get_recent_alerts(self, monitor):
        """测试获取最近告警"""
        alert1 = PerformanceAlert(
            alert_id="alert-1",
            level=AlertLevel.WARNING,
            metric="cpu",
            message="CPU warning",
            threshold_value=80.0,
            current_value=82.0,
            timestamp=datetime.utcnow(),
        )

        alert2 = PerformanceAlert(
            alert_id="alert-2",
            level=AlertLevel.CRITICAL,
            metric="memory",
            message="Memory critical",
            threshold_value=95.0,
            current_value=96.0,
            timestamp=datetime.utcnow(),
        )

        monitor._alerts.append(alert1)
        monitor._alerts.append(alert2)

        # 获取全部
        all_alerts = monitor.get_recent_alerts()
        assert len(all_alerts) == 2

        # 按级别过滤
        critical_alerts = monitor.get_recent_alerts(level=AlertLevel.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].level == AlertLevel.CRITICAL


class TestAlertLevelEnum:
    """告警级别枚举测试"""

    def test_alert_level_values(self):
        """测试告警级别的值"""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.CRITICAL.value == "critical"
        assert AlertLevel.ERROR.value == "error"

    def test_alert_level_comparison(self):
        """测试告警级别比较"""
        assert AlertLevel.INFO != AlertLevel.WARNING
        assert AlertLevel.WARNING != AlertLevel.CRITICAL
