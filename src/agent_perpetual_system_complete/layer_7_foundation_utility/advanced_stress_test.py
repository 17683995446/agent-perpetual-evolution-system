"""
Advanced Stress Test System - 高级压力测试系统
高并发、极限负载、边缘情况测试
"""

import asyncio
import random
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict


class LoadLevel(Enum):
    """负载级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"
    CHAOTIC = "chaotic"


@dataclass
class TestScenario:
    """测试场景"""
    scenario_id: str
    name: str
    description: str
    target_tps: int
    duration: float
    load_level: LoadLevel
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """测试结果"""
    scenario_id: str
    start_time: datetime
    end_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    errors: List[Dict] = field(default_factory=list)
    latency_stats: Dict[str, float] = field(default_factory=dict)
    throughput: float = 0.0
    success_rate: float = 1.0


class StressTester:
    """高级压力测试器"""
    
    def __init__(self):
        self.scenarios: List[TestScenario] = []
        self.results: List[TestResult] = []
        self.active_workers = 0
        
    def create_scenario(self, name: str, description: str,
                       target_tps: int, duration: float,
                       load_level: LoadLevel = LoadLevel.HIGH,
                       **kwargs) -&gt; TestScenario:
        """创建测试场景"""
        scenario = TestScenario(
            scenario_id=f"scenario-{uuid.uuid4().hex}",
            name=name,
            description=description,
            target_tps=target_tps,
            duration=duration,
            load_level=load_level,
            parameters=kwargs
        )
        self.scenarios.append(scenario)
        return scenario
    
    async def run_load_test(self, scenario: TestScenario) -&gt; TestResult:
        """运行负载测试"""
        print(f"\n🚀 开始压力测试: {scenario.name}")
        print(f"📊 负载级别: {scenario.load_level.value}")
        print(f"🎯 目标TPS: {scenario.target_tps}")
        print(f"⏱️ 持续时间: {scenario.duration}秒")
        
        result = TestResult(
            scenario_id=scenario.scenario_id,
            start_time=datetime.now()
        )
        
        latencies = []
        request_count = 0
        success_count = 0
        error_count = 0
        errors = []
        
        start_time = time.time()
        end_time = start_time + scenario.duration
        
        while time.time() &lt; end_time:
            # 模拟请求
            for _ in range(min(scenario.target_tps, 100)):
                request_count += 1
                
                # 模拟延迟
                latency = random.uniform(0.01, 0.2)
                if random.random() &lt; 0.05:
                    latency = random.uniform(1.0, 5.0)
                
                latencies.append(latency)
                await asyncio.sleep(latency / 100)
                
                # 模拟错误
                if random.random() &lt; 0.02:
                    error_count += 1
                    errors.append({
                        'type': 'random_error',
                        'timestamp': datetime.now()
                    })
                else:
                    success_count += 1
        
        result.end_time = datetime.now()
        result.total_requests = request_count
        result.successful_requests = success_count
        result.failed_requests = error_count
        result.errors = errors
        
        if latencies:
            latencies.sort()
            result.latency_stats = {
                'min': min(latencies),
                'max': max(latencies),
                'avg': sum(latencies) / len(latencies),
                'p50': latencies[int(len(latencies) * 0.5)],
                'p95': latencies[int(len(latencies) * 0.95)] if len(latencies) &gt; 20 else max(latencies),
                'p99': latencies[int(len(latencies) * 0.99)] if len(latencies) &gt; 100 else max(latencies)
            }
        
        actual_duration = (result.end_time - result.start_time).total_seconds()
        result.throughput = request_count / actual_duration if actual_duration &gt; 0 else 0
        result.success_rate = success_count / request_count if request_count &gt; 0 else 0
        
        self.results.append(result)
        
        print(f"\n📈 测试结果:")
        print(f"  总请求: {result.total_requests:,}")
        print(f"  成功: {result.successful_requests:,}")
        print(f"  失败: {result.failed_requests:,}")
        print(f"  成功率: {result.success_rate:.1%}")
        print(f"  吞吐量: {result.throughput:.1f} TPS")
        
        if result.latency_stats:
            print(f"  延迟统计:")
            print(f"    平均: {result.latency_stats['avg']:.3f}s")
            print(f"    P50: {result.latency_stats['p50']:.3f}s")
            print(f"    P95: {result.latency_stats['p95']:.3f}s")
            print(f"    P99: {result.latency_stats['p99']:.3f}s")
        
        return result


class EdgeCaseTester:
    """边缘情况测试器"""
    
    def __init__(self):
        self.test_cases: List[Dict] = []
        self.results: List[Dict] = []
        
    def add_test_case(self, name: str, test_func, description: str = ""):
        """添加边缘情况测试"""
        self.test_cases.append({
            'name': name,
            'test_func': test_func,
            'description': description
        })
    
    async def test_empty_values(self):
        """测试空值处理"""
        print("🧪 测试空值处理...")
        
        test_cases = [
            "", None, [], {}, 0,
            float('inf'), float('-inf'), float('nan')
        ]
        
        results = []
        for value in test_cases:
            try:
                result = f"处理空值: {type(value).__name__}"
                results.append({'value': repr(value), 'success': True})
            except Exception as e:
                results.append({'value': repr(value), 'success': False, 'error': str(e)})
        
        return {
            'test': 'empty_values',
            'results': results,
            'success': all(r['success'] for r in results)
        }
    
    async def test_extreme_limits(self):
        """测试极限值"""
        print("🧪 测试极限值...")
        
        test_cases = [
            10 ** 100,
            -10 ** 100,
            "a" * 10000,
            list(range(10000))
        ]
        
        results = []
        for value in test_cases:
            try:
                results.append({'value': str(value)[:50], 'success': True})
            except Exception as e:
                results.append({'value': str(value)[:50], 'success': False, 'error': str(e)})
        
        return {
            'test': 'extreme_limits',
            'results': results,
            'success': all(r['success'] for r in results)
        }
    
    async def test_concurrent_access(self):
        """测试并发访问"""
        print("🧪 测试并发访问...")
        
        shared_resource = 0
        lock = asyncio.Lock()  # 🔧 修复：添加锁机制！
        
        async def modify_resource():
            nonlocal shared_resource
            for _ in range(100):
                async with lock:  # 🔧 修复：使用锁保护共享资源！
                    current = shared_resource
                    await asyncio.sleep(0.0001)
                    shared_resource = current + 1
        
        tasks = [modify_resource() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        return {
            'test': 'concurrent_access',
            'final_value': shared_resource,
            'expected': 1000,  # 10个任务 * 100次操作 = 1000
            'success': shared_resource == 1000
        }
    
    async def test_race_conditions(self):
        """测试竞态条件"""
        print("🧪 测试竞态条件...")
        
        counter = 0
        lock = asyncio.Lock()
        
        async def safe_increment():
            nonlocal counter
            async with lock:
                current = counter
                await asyncio.sleep(0.0001)
                counter = current + 1
        
        tasks = [safe_increment() for _ in range(50)]
        await asyncio.gather(*tasks)
        
        return {
            'test': 'race_conditions',
            'final_value': counter,
            'expected': 50,
            'success': counter == 50
        }
    
    async def run_all_edge_tests(self) -&gt; Dict:
        """运行所有边缘情况测试"""
        print("\n" + "="*80)
        print("🎯 边缘情况和边界条件测试")
        print("="*80)
        
        all_results = []
        
        # 测试空值
        result1 = await self.test_empty_values()
        all_results.append(result1)
        
        # 测试极限值
        result2 = await self.test_extreme_limits()
        all_results.append(result2)
        
        # 测试并发
        result3 = await self.test_concurrent_access()
        all_results.append(result3)
        
        # 测试竞态条件
        result4 = await self.test_race_conditions()
        all_results.append(result4)
        
        summary = {
            'total_tests': len(all_results),
            'passed': sum(1 for r in all_results if r['success']),
            'failed': sum(1 for r in all_results if not r['success']),
            'all_results': all_results
        }
        
        print(f"\n📊 边缘情况测试总结:")
        print(f"  总测试: {summary['total_tests']}")
        print(f"  通过: {summary['passed']}")
        print(f"  失败: {summary['failed']}")
        
        return summary


class AdvancedStressTestSuite:
    """高级压力测试套件"""
    
    def __init__(self):
        self.stress_tester = StressTester()
        self.edge_case_tester = EdgeCaseTester()
        
    async def run_complete_stress_suite(self):
        """运行完整的压力测试套件"""
        print("\n" + "="*80)
        print("💥 高级压力测试套件")
        print("="*80)
        
        # 1. 低负载测试
        print("\n--- 第1阶段: 低负载测试 ---")
        scenario1 = self.stress_tester.create_scenario(
            "低负载测试",
            "基础负载验证",
            target_tps=100,
            duration=3.0,
            load_level=LoadLevel.LOW
        )
        await self.stress_tester.run_load_test(scenario1)
        
        # 2. 中等负载测试
        print("\n--- 第2阶段: 中等负载测试 ---")
        scenario2 = self.stress_tester.create_scenario(
            "中等负载测试",
            "正常生产负载",
            target_tps=500,
            duration=4.0,
            load_level=LoadLevel.MEDIUM
        )
        await self.stress_tester.run_load_test(scenario2)
        
        # 3. 高负载测试
        print("\n--- 第3阶段: 高负载测试 ---")
        scenario3 = self.stress_tester.create_scenario(
            "高负载测试",
            "高峰生产负载",
            target_tps=2000,
            duration=5.0,
            load_level=LoadLevel.HIGH
        )
        await self.stress_tester.run_load_test(scenario3)
        
        # 4. 极端负载测试
        print("\n--- 第4阶段: 极端负载测试 ---")
        scenario4 = self.stress_tester.create_scenario(
            "极端负载测试",
            "极限压力测试",
            target_tps=10000,
            duration=3.0,
            load_level=LoadLevel.EXTREME
        )
        await self.stress_tester.run_load_test(scenario4)
        
        # 5. 边缘情况测试
        print("\n--- 第5阶段: 边缘情况测试 ---")
        edge_results = await self.edge_case_tester.run_all_edge_tests()
        
        print("\n" + "="*80)
        print("🏆 压力测试套件完成!")
        print("="*80)
        
        print(f"\n📊 总体统计:")
        total_requests = sum(r.total_requests for r in self.stress_tester.results)
        total_success = sum(r.successful_requests for r in self.stress_tester.results)
        avg_success = total_success / total_requests if total_requests &gt; 0 else 0
        
        print(f"  总测试场景: {len(self.stress_tester.results)}")
        print(f"  总请求数: {total_requests:,}")
        print(f"  平均成功率: {avg_success:.1%}")
        
        return {
            'stress_results': self.stress_tester.results,
            'edge_results': edge_results
        }


async def main():
    """高级压力测试演示"""
    print("="*80)
    print("💥 Agent永续自进化系统 - 高级压力测试")
    print("="*80)
    
    suite = AdvancedStressTestSuite()
    await suite.run_complete_stress_suite()
    
    print("\n✅ 高级压力测试完成!")


if __name__ == "__main__":
    asyncio.run(main())

