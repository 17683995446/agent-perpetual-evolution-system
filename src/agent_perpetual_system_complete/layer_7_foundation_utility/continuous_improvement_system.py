"""
Continuous Improvement System - 持续改进系统
在大规模实践中发现问题和解决问题
"""

import asyncio
import time
import json
import uuid
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random


class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(Enum):
    """问题状态"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class IssueCategory(Enum):
    """问题类别"""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SECURITY = "security"
    FUNCTIONAL = "functional"
    USABILITY = "usability"
    DOCUMENTATION = "documentation"


@dataclass
class Issue:
    """问题数据结构"""
    issue_id: str
    title: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    status: IssueStatus
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    reproduction_steps: List[str] = field(default_factory=list)
    impact: str = ""
    solution: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IssueStatistics:
    """问题统计"""
    total_issues: int = 0
    open_issues: int = 0
    resolved_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    average_resolution_time: float = 0.0
    resolution_rate: float = 0.0


class IssueDetector:
    """问题检测器 - 自动发现问题"""
    
    def __init__(self):
        self.detectors: List[Callable] = []
        self.detected_issues: List[Issue] = []
        self.logger = None
    
    def register_detector(self, detector: Callable):
        """注册问题检测器"""
        self.detectors.append(detector)
    
    async def detect_issues(self) -> List[Issue]:
        """执行所有问题检测"""
        all_issues = []
        
        for detector in self.detectors:
            try:
                issues = await detector()
                if issues:
                    all_issues.extend(issues)
            except Exception as e:
                # 创建检测失败问题
                issue = Issue(
                    issue_id=f"detector-error-{uuid.uuid4().hex}",
                    title=f"检测器运行失败: {detector.__name__}",
                    description=f"检测器执行时发生错误: {str(e)}",
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.RELIABILITY,
                    status=IssueStatus.OPEN,
                    reported_at=datetime.now()
                )
                all_issues.append(issue)
        
        self.detected_issues.extend(all_issues)
        return all_issues
    
    async def detect_performance_issues(self) -> List[Issue]:
        """性能问题检测"""
        issues = []
        
        # 模拟一些性能问题检测
        cpu_usage = 0.85 + random.random() * 0.2
        if cpu_usage > 0.9:
            issues.append(Issue(
                issue_id=f"perf-high-cpu-{uuid.uuid4().hex}",
                title="CPU使用率过高",
                description=f"当前CPU使用率: {cpu_usage:.1%}",
                severity=IssueSeverity.HIGH,
                category=IssueCategory.PERFORMANCE,
                status=IssueStatus.OPEN,
                reported_at=datetime.now(),
                tags=["performance", "cpu"]
            ))
        
        memory_usage = 0.80 + random.random() * 0.2
        if memory_usage > 0.9:
            issues.append(Issue(
                issue_id=f"perf-high-memory-{uuid.uuid4().hex}",
                title="内存使用率过高",
                description=f"当前内存使用率: {memory_usage:.1%}",
                severity=IssueSeverity.HIGH,
                category=IssueCategory.PERFORMANCE,
                status=IssueStatus.OPEN,
                reported_at=datetime.now(),
                tags=["performance", "memory"]
            ))
        
        return issues
    
    async def detect_reliability_issues(self) -> List[Issue]:
        """可靠性问题检测"""
        issues = []
        
        error_rate = 0.05 + random.random() * 0.1
        if error_rate > 0.1:
            issues.append(Issue(
                issue_id=f"reliability-high-error-{uuid.uuid4().hex}",
                title="错误率过高",
                description=f"当前错误率: {error_rate:.1%}",
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.RELIABILITY,
                status=IssueStatus.OPEN,
                reported_at=datetime.now(),
                tags=["reliability", "errors"]
            ))
        
        response_time = 0.2 + random.random() * 0.5
        if response_time > 0.5:
            issues.append(Issue(
                issue_id=f"reliability-slow-response-{uuid.uuid4().hex}",
                title="响应时间过长",
                description=f"平均响应时间: {response_time:.2f}秒",
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.PERFORMANCE,
                status=IssueStatus.OPEN,
                reported_at=datetime.now(),
                tags=["performance", "response-time"]
            ))
        
        return issues


class IssueManager:
    """问题管理器 - 追踪和管理问题"""
    
    def __init__(self):
        self.issues: Dict[str, Issue] = {}
        self.issue_history: deque = deque(maxlen=1000)
        self.history: List[Dict[str, Any]] = []
    
    def create_issue(self, title: str, description: str, 
                    severity: IssueSeverity, category: IssueCategory,
                    tags: Optional[List[str]] = None) -> Issue:
        """创建新问题"""
        issue = Issue(
            issue_id=f"issue-{uuid.uuid4().hex}",
            title=title,
            description=description,
            severity=severity,
            category=category,
            status=IssueStatus.OPEN,
            reported_at=datetime.now(),
            tags=tags or []
        )
        self.issues[issue.issue_id] = issue
        self.issue_history.append(issue)
        return issue
    
    def update_issue(self, issue_id: str, **kwargs) -> Optional[Issue]:
        """更新问题"""
        if issue_id not in self.issues:
            return None
        
        issue = self.issues[issue_id]
        
        for key, value in kwargs.items():
            if hasattr(issue, key):
                setattr(issue, key, value)
        
        if 'status' in kwargs and kwargs['status'] == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.now()
        
        self.issue_history.append(issue)
        return issue
    
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """获取问题详情"""
        return self.issues.get(issue_id)
    
    def get_issues_by_severity(self, severity: IssueSeverity) -> List[Issue]:
        """按严重程度获取问题"""
        return [issue for issue in self.issues.values() 
                if issue.severity == severity]
    
    def get_issues_by_status(self, status: IssueStatus) -> List[Issue]:
        """按状态获取问题"""
        return [issue for issue in self.issues.values() 
                if issue.status == status]
    
    def get_statistics(self) -> IssueStatistics:
        """获取问题统计"""
        stats = IssueStatistics()
        
        for issue in self.issues.values():
            stats.total_issues += 1
            
            if issue.status == IssueStatus.OPEN:
                stats.open_issues += 1
            elif issue.status == IssueStatus.RESOLVED:
                stats.resolved_issues += 1
            
            if issue.severity == IssueSeverity.CRITICAL:
                stats.critical_issues += 1
            elif issue.severity == IssueSeverity.HIGH:
                stats.high_issues += 1
            elif issue.severity == IssueSeverity.MEDIUM:
                stats.medium_issues += 1
            elif issue.severity == IssueSeverity.LOW:
                stats.low_issues += 1
        
        if stats.total_issues > 0:
            stats.resolution_rate = (stats.resolved_issues / stats.total_issues)
        
        # 计算平均解决时间
        resolved_issues = [issue for issue in self.issues.values() 
                          if issue.status == IssueStatus.RESOLVED and issue.resolved_at]
        
        if resolved_issues:
            total_time = sum((issue.resolved_at - issue.reported_at).total_seconds() 
                           for issue in resolved_issues)
            stats.average_resolution_time = total_time / len(resolved_issues)
        
        return stats


class RegressionTestRunner:
    """回归测试运行器"""
    
    def __init__(self):
        self.tests: List[Dict] = []
        self.test_results: Dict[str, Any] = {}
    
    def register_test(self, test_name: str, test_func: Callable, 
                     category: str = "general"):
        """注册测试"""
        self.tests.append({
            'name': test_name,
            'func': test_func,
            'category': category
        })
    
    async def run_regression_tests(self) -> Dict[str, Any]:
        """运行回归测试"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for test in self.tests:
            results['total'] += 1
            test_name = test['name']
            
            try:
                if asyncio.iscoroutinefunction(test['func']):
                    await test['func']()
                else:
                    test['func']()
                
                results['passed'] += 1
                results['details'].append({
                    'name': test_name,
                    'status': 'passed',
                    'category': test['category']
                })
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'name': test_name,
                    'status': 'failed',
                    'error': str(e),
                    'category': test['category']
                })
        
        return results


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts: List[Dict] = []
        self.thresholds = {
            'cpu': 0.85,
            'memory': 0.85,
            'error_rate': 0.1,
            'response_time': 0.5
        }
    
    def add_metric(self, metric_name: str, value: float, timestamp: datetime):
        """添加性能指标"""
        self.metrics_history.append({
            'name': metric_name,
            'value': value,
            'timestamp': timestamp
        })
        
        # 检查阈值
        if metric_name in self.thresholds:
            if value > self.thresholds[metric_name]:
                self.alerts.append({
                    'type': 'threshold_exceeded',
                    'metric': metric_name,
                    'value': value,
                    'threshold': self.thresholds[metric_name],
                    'timestamp': timestamp
                })
    
    def get_recent_metrics(self, count: int = 100) -> List[Dict]:
        """获取最近的指标"""
        return list(self.metrics_history)[-count:]
    
    def get_alerts(self) -> List[Dict]:
        """获取告警"""
        return self.alerts


class ContinuousImprovementSystem:
    """持续改进系统 - 完整的CI/CD和问题解决系统"""
    
    def __init__(self):
        self.issue_detector = IssueDetector()
        self.issue_manager = IssueManager()
        self.test_runner = RegressionTestRunner()
        self.performance_monitor = PerformanceMonitor()
        
        # 注册默认检测器
        self.issue_detector.register_detector(self.issue_detector.detect_performance_issues)
        self.issue_detector.register_detector(self.issue_detector.detect_reliability_issues)
        
        # 注册示例测试
        self._register_example_tests()
    
    def _register_example_tests(self):
        """注册示例测试"""
        
        async def test_basic_functionality():
            # 基础功能测试
            await asyncio.sleep(0.01)
            assert 1 + 1 == 2
        
        async def test_performance_basic():
            # 性能测试
            start = time.time()
            for i in range(1000):
                _ = i * i
            duration = time.time() - start
            assert duration < 1.0
        
        self.test_runner.register_test("基础功能测试", test_basic_functionality, "functional")
        self.test_runner.register_test("基础性能测试", test_performance_basic, "performance")
    
    async def run_continuous_improvement_cycle(self) -> Dict[str, Any]:
        """运行完整的持续改进周期"""
        results = {
            'cycle_start': datetime.now(),
            'issues_found': [],
            'tests_run': {},
            'improvements_made': []
        }
        
        # 1. 检测问题
        detected_issues = await self.issue_detector.detect_issues()
        results['issues_found'] = detected_issues
        
        for issue in detected_issues:
            self.issue_manager.create_issue(
                title=issue.title,
                description=issue.description,
                severity=issue.severity,
                category=issue.category,
                tags=issue.tags
            )
        
        # 2. 运行回归测试
        test_results = await self.test_runner.run_regression_tests()
        results['tests_run'] = test_results
        
        # 3. 模拟改进
        if detected_issues:
            for issue in detected_issues[:3]:
                if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                    results['improvements_made'].append({
                        'issue_id': issue.issue_id,
                        'action': 'mitigation_applied',
                        'timestamp': datetime.now()
                    })
        
        # 4. 模拟性能监控
        metrics = ['cpu', 'memory', 'error_rate', 'response_time']
        for metric in metrics:
            value = random.uniform(0.3, 0.9)
            self.performance_monitor.add_metric(metric, value, datetime.now())
        
        results['cycle_end'] = datetime.now()
        return results
    
    def get_improvement_report(self) -> Dict[str, Any]:
        """获取改进报告"""
        stats = self.issue_manager.get_statistics()
        
        return {
            'report_date': datetime.now().isoformat(),
            'issue_statistics': {
                'total': stats.total_issues,
                'open': stats.open_issues,
                'resolved': stats.resolved_issues,
                'critical': stats.critical_issues,
                'high': stats.high_issues,
                'medium': stats.medium_issues,
                'low': stats.low_issues,
                'resolution_rate': stats.resolution_rate,
                'avg_resolution_time': stats.average_resolution_time
            },
            'performance_alerts': len(self.performance_monitor.alerts),
            'recent_metrics': self.performance_monitor.get_recent_metrics(20)
        }


async def main():
    """演示持续改进系统"""
    print("="*80)
    print("🚀 Agent永续自进化系统 - 持续改进演示")
    print("="*80)
    
    cis = ContinuousImprovementSystem()
    
    print("\n📊 开始持续改进周期...")
    
    for cycle in range(3):
        print(f"\n--- 改进周期 #{cycle + 1} ---")
        
        results = await cis.run_continuous_improvement_cycle()
        
        print(f"发现问题数: {len(results['issues_found'])}")
        print(f"测试通过: {results['tests_run']['passed']}/{results['tests_run']['total']}")
        print(f"实施改进: {len(results['improvements_made'])}")
        
        await asyncio.sleep(1)
    
    print("\n📈 改进报告:")
    report = cis.get_improvement_report()
    
    print(f"\n问题统计:")
    print(f"  总计: {report['issue_statistics']['total']}")
    print(f"  打开: {report['issue_statistics']['open']}")
    print(f"  解决: {report['issue_statistics']['resolved']}")
    print(f"  解决率: {report['issue_statistics']['resolution_rate']:.1%}")
    
    print(f"\n性能告警: {report['performance_alerts']}")
    
    print("\n✅ 持续改进系统演示完成!")


if __name__ == "__main__":
    asyncio.run(main())

