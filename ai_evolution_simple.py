
"""
AI驱动进化引擎 - 完整可运行版本
基于硅基流动API的智能性能优化和自动进化
独立版本，无需额外依赖
"""

import asyncio
import time
import json
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests


# ==================== 配置 ====================

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


# ==================== 简单的日志系统 ====================

def log(level: str, *args, **kwargs):
    """简单的日志函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}]", *args, **kwargs)


# ==================== 数据模型 ====================

class PerformanceMetricType:
    """性能指标类型"""
    TASK_THROUGHPUT = "task_throughput"
    SUCCESS_RATE = "success_rate"
    RESPONSE_LATENCY = "response_latency"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"


class OptimizationPriority:
    """优化优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ==================== 性能监控器 ====================

class PerformanceMonitor:
    """性能监控器 - 收集系统性能指标"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history = []
        self.collection_interval = 1.0
        self._is_collecting = False
        self._collection_task = None
        
        self.task_count = 0
        self.task_success = 0
        self.task_failed = 0
        self.total_latency = 0.0
        
        log("info", "PerformanceMonitor initialized")
    
    async def start_collection(self):
        """开始性能收集"""
        if self._is_collecting:
            return
        
        self._is_collecting = True
        self._collection_task = asyncio.create_task(self._collect_loop())
        log("info", "Performance collection started")
    
    async def stop_collection(self):
        """停止性能收集"""
        self._is_collecting = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        log("info", "Performance collection stopped")
    
    async def _collect_loop(self):
        """收集循环"""
        while self._is_collecting:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                log("error", f"Collection error: {e}")
    
    async def _collect_metrics(self):
        """收集指标"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        throughput = self.task_count / max(time.time() - self.start_time, 1)
        
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "throughput": throughput
        })
        
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
    """AI分析引擎 - 使用硅基流动API分析性能数据"""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.model = DEFAULT_MODEL
        log("info", "AIAnalyzer initialized")
    
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
                log("error", f"API call failed: {response.text}")
                return None
                
        except Exception as e:
            log("error", f"API call error: {e}")
            return None
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> str:
        """分析性能数据"""
        system_prompt = """You are an expert performance analyst for AI agent systems.
Analyze the performance metrics and provide key findings, bottlenecks, and quick wins.
Be concise and actionable. Use Chinese if appropriate."""
        
        user_message = f"""Analyze these performance metrics:
- CPU: {metrics.get('cpu_percent', 0):.1f}%
- Memory: {metrics.get('memory_percent', 0):.1f}%
- Tasks: {metrics.get('task_count', 0)} total, {metrics.get('task_success', 0)} success, {metrics.get('task_failed', 0)} failed
- Success Rate: {metrics.get('success_rate', 0)*100:.1f}%
- Avg Latency: {metrics.get('average_latency', 0):.3f}s

Provide analysis with: 1) Key findings 2) Bottlenecks 3) Quick wins"""
        
        return self._call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]) or "Analysis unavailable"
    
    def generate_optimization_suggestions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        system_prompt = """You are an optimization expert for AI agent systems.
Generate specific, actionable optimization suggestions.
Return as JSON array with: title, description, priority (critical/high/medium/low), expected_improvement, category.
Return ONLY JSON array."""
        
        user_message = f"""Generate optimization suggestions for:
- CPU: {metrics.get('cpu_percent', 0):.1f}%
- Memory: {metrics.get('memory_percent', 0):.1f}%
- Success Rate: {metrics.get('success_rate', 0)*100:.1f}%

Return JSON array."""
        
        response = self._call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ], max_tokens=2048)
        
        if response:
            try:
                start_idx = response.find("[")
                end_idx = response.rfind("]")
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx+1]
                    return json.loads(json_str)
            except Exception:
                pass
        
        return self._generate_default_suggestions(metrics)
    
    def _generate_default_suggestions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成默认建议"""
        suggestions = []
        
        cpu = metrics.get("cpu_percent", 0)
        if cpu > 80:
            suggestions.append({
                "title": "High CPU Usage Detected",
                "description": f"CPU usage at {cpu:.1f}%, optimize workloads",
                "priority": "high",
                "expected_improvement": "Reduce CPU by 20-30%",
                "category": "performance"
            })
        
        memory = metrics.get("memory_percent", 0)
        if memory > 85:
            suggestions.append({
                "title": "High Memory Usage",
                "description": f"Memory at {memory:.1f}%, risk of OOM",
                "priority": "critical",
                "expected_improvement": "Reduce memory by 30-40%",
                "category": "reliability"
            })
        
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < 0.9:
            suggestions.append({
                "title": "Success Rate Below Target",
                "description": f"Success rate {success_rate*100:.1f}%, investigate failures",
                "priority": "high",
                "expected_improvement": "Improve to 95%+",
                "category": "reliability"
            })
        
        if not suggestions:
            suggestions.append({
                "title": "System Performance Optimal",
                "description": "All metrics within acceptable ranges",
                "priority": "low",
                "expected_improvement": "Maintain current state",
                "category": "performance"
            })
        
        return suggestions


# ==================== 进化引擎 ====================

class EvolutionEngine:
    """AI驱动的进化引擎"""
    
    def __init__(self, api_key: str = API_KEY):
        log("info", "EvolutionEngine initialized")
        
        self.monitor = PerformanceMonitor()
        self.analyzer = AIAnalyzer(api_key)
        
        self.current_stage_name = "Initializing"
        self.current_stage_number = 0
        
        self.optimization_history = []
        self._is_running = False
    
    async def start(self):
        """启动进化引擎"""
        if self._is_running:
            return
        
        self._is_running = True
        await self.monitor.start_collection()
        
        self.current_stage_name = "Learning"
        self.current_stage_number = 1
        
        log("info", f"Evolution engine started - Stage: {self.current_stage_name}")
    
    async def stop(self):
        """停止进化引擎"""
        self._is_running = False
        await self.monitor.stop_collection()
        
        log("info", "Evolution engine stopped")
    
    async def evolve(self) -> Dict[str, Any]:
        """执行一次进化迭代"""
        log("info", "Starting evolution iteration")
        
        metrics = self.monitor.get_current_metrics()
        analysis = self.analyzer.analyze_performance(metrics)
        suggestions = self.analyzer.generate_optimization_suggestions(metrics)
        
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "analysis": analysis,
            "suggestions": suggestions,
            "suggestions_count": len(suggestions)
        }
        
        self.optimization_history.append(optimization)
        
        if len(self.optimization_history) >= 10:
            self.current_stage_number += 1
            self.current_stage_name = self._get_next_stage_name()
        
        log("info", f"Evolution iteration completed - {len(suggestions)} suggestions")
        
        return optimization
    
    def _get_next_stage_name(self) -> str:
        """获取下一个阶段名称"""
        stages = [
            "Initializing", "Learning", "Analyzing", "Optimizing",
            "Scaling", "Advanced", "Expert", "Master"
        ]
        index = min(self.current_stage_number, len(stages) - 1)
        return stages[index]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        current_metrics = self.monitor.get_current_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": {
                "name": self.current_stage_name,
                "number": self.current_stage_number
            },
            "current_metrics": current_metrics,
            "evolution_history": {
                "total_iterations": len(self.optimization_history),
                "latest": self.optimization_history[-1] if self.optimization_history else None
            },
            "health": self._calculate_health(current_metrics)
        }
    
    def _calculate_health(self, metrics: Dict[str, Any]) -> str:
        """计算健康评分"""
        score = 100
        cpu = metrics.get("cpu_percent", 0)
        memory = metrics.get("memory_percent", 0)
        success_rate = metrics.get("success_rate", 1.0)
        
        if cpu > 90: score -= 30
        elif cpu > 80: score -= 15
        
        if memory > 90: score -= 30
        elif memory > 85: score -= 15
        
        if success_rate < 0.8: score -= 40
        elif success_rate < 0.9: score -= 20
        
        if score >= 80: return "healthy"
        elif score >= 60: return "warning"
        return "critical"


# ==================== 主演示系统 ====================

class PerpetualEvolutionSystem:
    """Agent永续循环自进化运行系统"""
    
    def __init__(self):
        log("info", "PerpetualEvolutionSystem initialized")
        self.evolution_engine = EvolutionEngine()
        self._tasks = []
    
    async def initialize(self):
        """初始化系统"""
        log("info", "Initializing system...")
        await self.evolution_engine.start()
        log("info", "System initialized")
    
    async def run_demo(self, duration_seconds: int = 60):
        """运行演示"""
        print("=" * 80)
        print("Agent 永续循环自进化运行系统 - AI驱动进化引擎演示")
        print("=" * 80)
        
        await self.initialize()
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
                
                dashboard = self.evolution_engine.get_dashboard_data()
                metrics = dashboard["current_metrics"]
                
                print(f"\n📊 当前指标:")
                print(f"  CPU: {metrics['cpu_percent']:.1f}%")
                print(f"  内存: {metrics['memory_percent']:.1f}%")
                print(f"  任务: {metrics['task_count']} (成功: {metrics['task_success']}, 失败: {metrics['task_failed']})")
                print(f"  成功率: {metrics['success_rate']*100:.1f}%")
                print(f"  延迟: {metrics['average_latency']:.3f}s")
                
                print(f"\n🏥 系统健康: {dashboard['health'].upper()}")
                print(f"🧬 进化阶段: {dashboard['stage']['name']} (Level {dashboard['stage']['number']})")
                
                optimization = await self.evolution_engine.evolve()
                
                print(f"\n💡 AI优化建议 ({len(optimization['suggestions'])}条):")
                priority_emoji = {
                    "critical": "🔴", "high": "🟠",
                    "medium": "🟡", "low": "🟢"
                }
                
                for i, suggestion in enumerate(optimization["suggestions"][:3], 1):
                    emoji = priority_emoji.get(suggestion.get("priority", "low"), "⚪")
                    print(f"\n  {emoji} {suggestion['title']}")
                    print(f"     {suggestion['description']}")
                    print(f"     预期改善: {suggestion.get('expected_improvement', 'N/A')}")
                
                print(f"\n🔍 AI分析:")
                analysis_lines = optimization["analysis"].split("\n")[:4]
                for line in analysis_lines:
                    if line.strip():
                        print(f"  {line}")
                
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            print("\n演示被中断")
        
        finally:
            await self.shutdown()
            
            print("\n" + "=" * 80)
            print("演示完成!")
            print("=" * 80)
            
            final = self.evolution_engine.get_dashboard_data()
            print(f"\n📈 最终统计:")
            print(f"  总迭代: {final['evolution_history']['total_iterations']}")
            print(f"  最终阶段: {final['stage']['name']}")
            print(f"  健康状态: {final['health']}")
    
    def _start_task_simulation(self):
        """启动任务模拟"""
        async def simulate():
            import random
            while True:
                success = random.random() > 0.15
                latency = random.uniform(0.05, 0.5)
                self.evolution_engine.monitor.record_task_execution(success, latency)
                await asyncio.sleep(random.uniform(0.1, 1.0))
        
        self._tasks.append(asyncio.create_task(simulate()))
    
    async def shutdown(self):
        """关闭系统"""
        log("info", "Shutting down...")
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await self.evolution_engine.stop()


# ==================== 主函数 ====================

async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 Agent 永续循环自进化运行系统")
    print("   AI驱动的性能优化和自动进化")
    print("=" * 80)
    print("\n功能:")
    print("  ✓ 实时性能监控")
    print("  ✓ AI驱动的性能分析")
    print("  ✓ 智能优化建议生成")
    print("  ✓ 自动进化阶段追踪")
    print("  ✓ 基于硅基流动API")
    print("\n按 Ctrl+C 停止演示\n")
    
    system = PerpetualEvolutionSystem()
    await system.run_demo(duration_seconds=60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")

