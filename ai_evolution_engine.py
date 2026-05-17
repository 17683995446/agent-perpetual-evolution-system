
"""
AI驱动进化引擎 - 完整的智能自进化系统
基于硅基流动API的智能性能优化和自动进化
"""

import asyncio
import time
import json
import psutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import requests

from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


# ==================== 配置 ====================

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


# ==================== 数据模型 ====================

class PerformanceMetricType(str, Enum):
    """性能指标类型"""
    TASK_THROUGHPUT = "task_throughput"
    SUCCESS_RATE = "success_rate"
    RESPONSE_LATENCY = "response_latency"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"
    AGENT_UTILIZATION = "agent_utilization"


class OptimizationPriority(str, Enum):
    """优化优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str
    title: str
    description: str
    priority: OptimizationPriority
    expected_improvement: str
    implementation_effort: str
    category: str
    steps: List[str] = field(default_factory=list)
    estimated_impact: float = 0.0
    confidence: float = 0.0


@dataclass
class EvolutionStage:
    """进化阶段"""
    stage_name: str
    stage_number: int
    status: str
    metrics: Dict[str, float] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ==================== 性能监控器 ====================

class PerformanceMonitor:
    """
    性能监控器
    
    收集系统性能指标，包括：
    - CPU使用率
    - 内存使用
    - 任务吞吐量
    - 响应延迟
    - 错误率
    """
    
    def __init__(self):
        self.logger = get_structured_logger(__name__)
        self.metrics_history: List[PerformanceMetric] = []
        self.collection_interval = 1.0
        self._is_collecting = False
        self._collection_task = None
        
        # 模拟任务数据
        self.task_count = 0
        self.task_success = 0
        self.task_failed = 0
        self.total_latency = 0.0
    
    async def start_collection(self):
        """开始性能收集"""
        if self._is_collecting:
            return
        
        self._is_collecting = True
        self._collection_task = asyncio.create_task(self._collect_loop())
        self.logger.info("Performance collection started")
    
    async def stop_collection(self):
        """停止性能收集"""
        self._is_collecting = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Performance collection stopped")
    
    async def _collect_loop(self):
        """收集循环"""
        while self._is_collecting:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error("Collection error", error=str(e))
    
    async def _collect_metrics(self):
        """收集指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        await self._record_metric(
            PerformanceMetricType.CPU_USAGE,
            cpu_percent,
            "%"
        )
        
        # 内存使用
        memory = psutil.virtual_memory()
        await self._record_metric(
            PerformanceMetricType.MEMORY_USAGE,
            memory.percent,
            "%"
        )
        
        # 任务吞吐量（每秒任务数）
        throughput = self.task_count / max(time.time() - self.start_time, 1)
        await self._record_metric(
            PerformanceMetricType.TASK_THROUGHPUT,
            throughput,
            "tasks/sec"
        )
        
        # 成功率
        total_tasks = self.task_success + self.task_failed
        if total_tasks > 0:
            success_rate = self.task_success / total_tasks
            await self._record_metric(
                PerformanceMetricType.SUCCESS_RATE,
                success_rate,
                "%"
            )
    
    def __init__(self):
        self.start_time = time.time()
    
    async def _record_metric(self, metric_type: PerformanceMetricType, value: float, unit: str):
        """记录指标"""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow()
        )
        self.metrics_history.append(metric)
        
        # 保持最近1000条记录
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def record_task_execution(self, success: bool, latency: float):
        """记录任务执行"""
        self.task_count += 1
        if success:
            self.task_success += 1
        else:
            self.task_failed += 1
        self.total_latency += latency
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "task_count": self.task_count,
            "task_success": self.task_success,
            "task_failed": self.task_failed,
            "success_rate": self.task_success / max(self.task_count, 1),
            "average_latency": self.total_latency / max(self.task_count, 1),
        }


# ==================== AI分析引擎 ====================

class AIAnalyzer:
    """
    AI分析引擎
    
    使用硅基流动API分析性能数据，生成优化建议
    """
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.model = DEFAULT_MODEL
        self.logger = get_structured_logger(__name__)
    
    def _call_api(self, messages: List[Dict[str, str]], max_tokens: int = 1024) -> Optional[str]:
        """调用硅基流动API"""
        url = self.base_url + "/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                choice = result.get("choices", [{}])[0]
                return choice.get("message", {}).get("content", "")
            else:
                self.logger.error("API call failed", status=response.status_code, error=response.text)
                return None
                
        except Exception as e:
            self.logger.error("API call error", error=str(e))
            return None
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> str:
        """分析性能数据"""
        system_prompt = """You are an expert performance analyst for AI agent systems.
Analyze the performance metrics and provide:
1. Key findings
2. Potential bottlenecks
3. Quick optimization wins
Be concise and actionable."""
        
        user_message = f"""Analyze these performance metrics:
{json.dumps(metrics, indent=2)}

Provide your analysis in plain text, structured by sections."""
        
        return self._call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]) or "Analysis unavailable"
    
    def generate_optimization_suggestions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        system_prompt = """You are an optimization expert for AI agent systems.
Generate specific, actionable optimization suggestions based on performance metrics.
Return your suggestions as a JSON array with this structure:
[
    {
        "title": "Suggestion title",
        "description": "Detailed description",
        "priority": "critical|high|medium|low",
        "expected_improvement": "What improvement to expect",
        "implementation_effort": "low|medium|high",
        "category": "performance|reliability|scalability",
        "steps": ["Step 1", "Step 2"]
    }
]
Return ONLY the JSON array, no other text."""
        
        user_message = f"""Generate optimization suggestions for these metrics:
{json.dumps(metrics, indent=2)}

Return ONLY a JSON array of suggestions."""
        
        response = self._call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ], max_tokens=2048)
        
        if response:
            try:
                # 尝试提取JSON
                start_idx = response.find("[")
                end_idx = response.rfind("]")
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx+1]
                    suggestions = json.loads(json_str)
                    return suggestions
            except Exception:
                pass
        
        # 返回默认建议
        return self._generate_default_suggestions(metrics)
    
    def _generate_default_suggestions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成默认建议"""
        suggestions = []
        
        cpu = metrics.get("cpu_percent", 0)
        if cpu > 80:
            suggestions.append({
                "title": "High CPU Usage Detected",
                "description": f"CPU usage is at {cpu}%, consider optimizing or scaling",
                "priority": "high",
                "expected_improvement": "Reduce CPU usage by 20-30%",
                "implementation_effort": "medium",
                "category": "performance",
                "steps": ["Profile current workloads", "Optimize hot paths", "Consider caching"]
            })
        
        memory = metrics.get("memory_percent", 0)
        if memory > 85:
            suggestions.append({
                "title": "High Memory Usage",
                "description": f"Memory usage is at {memory}%, risk of OOM",
                "priority": "critical",
                "expected_improvement": "Reduce memory usage by 30-40%",
                "implementation_effort": "high",
                "category": "reliability",
                "steps": ["Implement memory pooling", "Add garbage collection tuning", "Consider memory limits"]
            })
        
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < 0.9:
            suggestions.append({
                "title": "Low Success Rate",
                "description": f"Success rate is {success_rate*100:.1f}%, needs investigation",
                "priority": "high",
                "expected_improvement": "Improve success rate to 95%+",
                "implementation_effort": "medium",
                "category": "reliability",
                "steps": ["Analyze failure patterns", "Add retry logic", "Improve error handling"]
            })
        
        return suggestions if suggestions else [{
            "title": "System is Healthy",
            "description": "All metrics are within normal ranges",
            "priority": "low",
            "expected_improvement": "No immediate action needed",
            "implementation_effort": "none",
            "category": "performance",
            "steps": ["Continue monitoring"]
        }]


# ==================== 进化引擎 ====================

class EvolutionEngine:
    """
    AI驱动的进化引擎
    
    核心功能：
    1. 性能监控和数据分析
    2. AI驱动的优化建议生成
    3. 自动策略优化
    4. 进化阶段追踪
    """
    
    def __init__(self, api_key: str = API_KEY):
        self.logger = get_structured_logger(__name__)
        
        self.monitor = PerformanceMonitor()
        self.analyzer = AIAnalyzer(api_key)
        
        self.current_stage = EvolutionStage(
            stage_name="Initializing",
            stage_number=0,
            status="initializing"
        )
        
        self.optimization_history: List[Dict[str, Any]] = []
        self._is_running = False
    
    async def start(self):
        """启动进化引擎"""
        if self._is_running:
            return
        
        self._is_running = True
        await self.monitor.start_collection()
        
        # 设置初始阶段
        self.current_stage = EvolutionStage(
            stage_name="Learning",
            stage_number=1,
            status="running",
            started_at=datetime.utcnow()
        )
        
        self.logger.info("Evolution engine started", stage=self.current_stage.stage_name)
    
    async def stop(self):
        """停止进化引擎"""
        self._is_running = False
        await self.monitor.stop_collection()
        
        self.current_stage.status = "completed"
        self.current_stage.completed_at = datetime.utcnow()
        
        self.logger.info("Evolution engine stopped")
    
    async def analyze_current_state(self) -> Dict[str, Any]:
        """分析当前状态"""
        metrics = self.monitor.get_current_metrics()
        
        analysis = self.analyzer.analyze_performance(metrics)
        suggestions = self.analyzer.generate_optimization_suggestions(metrics)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "current_stage": self.current_stage.stage_name,
            "metrics": metrics,
            "analysis": analysis,
            "suggestions": suggestions,
            "evolution_level": self.current_stage.stage_number
        }
    
    async def evolve(self) -> Dict[str, Any]:
        """
        执行一次进化迭代
        
        收集数据 -> AI分析 -> 生成建议 -> 记录优化
        """
        self.logger.info("Starting evolution iteration")
        
        # 收集当前指标
        metrics = self.monitor.get_current_metrics()
        
        # AI分析
        analysis = self.analyzer.analyze_performance(metrics)
        suggestions = self.analyzer.generate_optimization_suggestions(metrics)
        
        # 记录优化
        optimization = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "analysis": analysis,
            "suggestions": suggestions,
            "suggestions_count": len(suggestions)
        }
        
        self.optimization_history.append(optimization)
        
        # 更新进化阶段
        if len(self.optimization_history) >= 10:
            self.current_stage.stage_number += 1
            self.current_stage.stage_name = self._get_next_stage_name()
        
        self.logger.info(
            "Evolution iteration completed",
            suggestions_count=len(suggestions)
        )
        
        return optimization
    
    def _get_next_stage_name(self) -> str:
        """获取下一个阶段名称"""
        stages = [
            "Initializing",
            "Learning",
            "Analyzing",
            "Optimizing",
            "Scaling",
            "Advanced",
            "Expert",
            "Master"
        ]
        
        index = min(self.current_stage.stage_number, len(stages) - 1)
        return stages[index]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        current_metrics = self.monitor.get_current_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": {
                "name": self.current_stage.stage_name,
                "number": self.current_stage.stage_number,
                "status": self.current_stage.status
            },
            "current_metrics": current_metrics,
            "evolution_history": {
                "total_iterations": len(self.optimization_history),
                "latest_optimization": self.optimization_history[-1] if self.optimization_history else None
            },
            "system_health": self._calculate_health_score(current_metrics)
        }
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> str:
        """计算健康评分"""
        score = 100
        
        cpu = metrics.get("cpu_percent", 0)
        if cpu > 90:
            score -= 30
        elif cpu > 80:
            score -= 15
        
        memory = metrics.get("memory_percent", 0)
        if memory > 90:
            score -= 30
        elif memory > 85:
            score -= 15
        
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < 0.8:
            score -= 40
        elif success_rate < 0.9:
            score -= 20
        
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "warning"
        else:
            return "critical"


# ==================== 主演示系统 ====================

class PerpetualEvolutionSystem:
    """
    Agent永续循环自进化运行系统
    
    整合所有组件，提供完整的自进化能力
    """
    
    def __init__(self):
        self.logger = get_structured_logger(__name__)
        self.evolution_engine = EvolutionEngine()
        self._tasks = []
    
    async def initialize(self):
        """初始化系统"""
        self.logger.info("Initializing Perpetual Evolution System")
        await self.evolution_engine.start()
        self.logger.info("System initialized successfully")
    
    async def run_demonstration(self, duration_seconds: int = 60):
        """
        运行演示
        
        Args:
            duration_seconds: 演示持续时间
        """
        print("=" * 80)
        print("Agent 永续循环自进化运行系统 - 演示")
        print("=" * 80)
        
        await self.initialize()
        
        # 模拟任务执行
        self._start_task_simulation()
        
        start_time = time.time()
        iteration = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                iteration += 1
                elapsed = time.time() - start_time
                
                print(f"\n{'='*80}")
                print(f"迭代 #{iteration} | 已运行: {elapsed:.1f}秒")
                print("="*80)
                
                # 获取仪表盘数据
                dashboard = self.evolution_engine.get_dashboard_data()
                
                # 打印当前指标
                print("\n📊 当前指标:")
                metrics = dashboard["current_metrics"]
                print(f"  CPU使用率: {metrics['cpu_percent']:.1f}%")
                print(f"  内存使用: {metrics['memory_percent']:.1f}%")
                print(f"  任务总数: {metrics['task_count']}")
                print(f"  成功率: {metrics['success_rate']*100:.1f}%")
                print(f"  平均延迟: {metrics['average_latency']:.3f}秒")
                
                # 打印系统健康状态
                print(f"\n🏥 系统健康: {dashboard['system_health'].upper()}")
                
                # 打印进化阶段
                stage = dashboard["stage"]
                print(f"\n🧬 进化阶段: {stage['name']} (Level {stage['number']})")
                
                # 执行AI分析
                optimization = await self.evolution_engine.evolve()
                
                # 打印优化建议
                print(f"\n💡 AI优化建议 (共{len(optimization['suggestions'])}条):")
                for i, suggestion in enumerate(optimization["suggestions"][:3], 1):
                    priority_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(suggestion.get("priority", "low"), "⚪")
                    
                    print(f"\n  {priority_emoji} {suggestion['title']}")
                    print(f"     {suggestion['description']}")
                    print(f"     优先级: {suggestion.get('priority', 'N/A')} | "
                          f"预期改善: {suggestion.get('expected_improvement', 'N/A')}")
                
                # 打印分析结果
                print(f"\n🔍 AI分析结果:")
                analysis_lines = optimization["analysis"].split("\n")[:5]
                for line in analysis_lines:
                    if line.strip():
                        print(f"  {line}")
                
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            print("\n\n演示被用户中断")
        
        finally:
            await self.shutdown()
            
            print("\n" + "=" * 80)
            print("演示完成!")
            print("=" * 80)
            
            # 打印最终统计
            print("\n📈 最终统计:")
            final_dashboard = self.evolution_engine.get_dashboard_data()
            print(f"  总迭代次数: {final_dashboard['evolution_history']['total_iterations']}")
            print(f"  最终进化阶段: {final_dashboard['stage']['name']}")
            print(f"  系统健康状态: {final_dashboard['system_health']}")
    
    def _start_task_simulation(self):
        """启动任务模拟"""
        async def simulate_tasks():
            """模拟任务执行"""
            while True:
                # 随机成功/失败
                import random
                success = random.random() > 0.15  # 85%成功率
                latency = random.uniform(0.05, 0.5)  # 50-500ms延迟
                
                self.evolution_engine.monitor.record_task_execution(success, latency)
                
                await asyncio.sleep(random.uniform(0.1, 1.0))
        
        self._tasks.append(asyncio.create_task(simulate_tasks()))
    
    async def shutdown(self):
        """关闭系统"""
        self.logger.info("Shutting down system")
        
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        await self.evolution_engine.stop()
        
        self.logger.info("System shutdown complete")


# ==================== 主函数 ====================

async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 Agent 永续循环自进化运行系统")
    print("=" * 80)
    print("\n系统特性:")
    print("  ✓ 实时性能监控")
    print("  ✓ AI驱动的性能分析")
    print("  ✓ 智能优化建议生成")
    print("  ✓ 自动进化阶段追踪")
    print("  ✓ 基于硅基流动API的智能分析")
    print("\n按 Ctrl+C 停止演示\n")
    
    system = PerpetualEvolutionSystem()
    await system.run_demonstration(duration_seconds=60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已正常退出")

