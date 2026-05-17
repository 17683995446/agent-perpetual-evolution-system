"""
Advanced Chaos Engineering System - 高级混沌工程系统
针对复杂高难度场景的故障注入和系统验证
"""

import asyncio
import random
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict


class FaultType(Enum):
    """故障类型"""
    LATENCY = "latency"
    ERROR = "error"
    DISK = "disk"
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    SERVICE_DOWN = "service_down"
    DATABASE_DOWN = "database_down"
    RATE_LIMIT = "rate_limit"


@dataclass
class FaultInjection:
    """故障注入配置"""
    injection_id: str
    fault_type: FaultType
    target_service: str
    severity: float
    duration: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    active: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class FaultInjector:
    """高级故障注入器"""
    
    def __init__(self):
        self.active_injections: Dict[str, FaultInjection] = {}
        self.injection_history: List[Dict] = []
        self.detected_issues: List[Dict] = []
        
    async def inject_fault(self, fault):
        """注入故障"""
        fault.active = True
        self.active_injections[fault.injection_id] = fault
        
        injection_record = {
            'injection_id': fault.injection_id,
            'fault_type': fault.fault_type.value,
            'target': fault.target_service,
            'severity': fault.severity,
            'duration': fault.duration,
            'injected_at': datetime.now()
        }
        self.injection_history.append(injection_record)
        
        print(f"🎯 注入故障: {fault.fault_type.value} → {fault.target_service}")
        
        await asyncio.sleep(fault.duration)
        
        if fault.injection_id in self.active_injections:
            del self.active_injections[fault.injection_id]
            
        return fault.injection_id
    
    async def inject_latency(self, target_service,
                           min_latency=0.1,
                           max_latency=2.0,
                           duration=10.0):
        """注入延迟故障"""
        fault = FaultInjection(
            injection_id=f"latency-{uuid.uuid4().hex}",
            fault_type=FaultType.LATENCY,
            target_service=target_service,
            severity=0.5,
            duration=duration,
            parameters={'min_latency': min_latency, 'max_latency': max_latency}
        )
        return await self.inject_fault(fault)
    
    async def inject_error(self, target_service,
                          error_rate=0.5,
                          duration=10.0):
        """注入错误故障"""
        fault = FaultInjection(
            injection_id=f"error-{uuid.uuid4().hex}",
            fault_type=FaultType.ERROR,
            target_service=target_service,
            severity=0.7,
            duration=duration,
            parameters={'error_rate': error_rate}
        )
        return await self.inject_fault(fault)
    
    async def inject_network_partition(self, target_service,
                                     partition_size=0.3,
                                     duration=15.0):
        """注入网络分区故障"""
        fault = FaultInjection(
            injection_id=f"network-{uuid.uuid4().hex}",
            fault_type=FaultType.NETWORK,
            target_service=target_service,
            severity=0.8,
            duration=duration,
            parameters={'partition_size': partition_size}
        )
        return await self.inject_fault(fault)
    
    async def inject_service_failure(self, target_service,
                                   duration=10.0):
        """注入服务故障"""
        fault = FaultInjection(
            injection_id=f"service-{uuid.uuid4().hex}",
            fault_type=FaultType.SERVICE_DOWN,
            target_service=target_service,
            severity=0.95,
            duration=duration
        )
        return await self.inject_fault(fault)
    
    async def inject_disk_failure(self, target_service,
                                 disk_usage=0.99,
                                 duration=20.0):
        """注入磁盘故障"""
        fault = FaultInjection(
            injection_id=f"disk-{uuid.uuid4().hex}",
            fault_type=FaultType.DISK,
            target_service=target_service,
            severity=0.85,
            duration=duration,
            parameters={'disk_usage': disk_usage}
        )
        return await self.inject_fault(fault)
    
    async def inject_memory_leak(self, target_service,
                                 leak_rate=0.1,
                                 duration=30.0):
        """注入内存泄漏"""
        fault = FaultInjection(
            injection_id=f"memory-{uuid.uuid4().hex}",
            fault_type=FaultType.MEMORY,
            target_service=target_service,
            severity=0.9,
            duration=duration,
            parameters={'leak_rate': leak_rate}
        )
        return await self.inject_fault(fault)
    
    def stop_injection(self, injection_id):
        """停止故障注入"""
        if injection_id in self.active_injections:
            self.active_injections[injection_id].active = False
            del self.active_injections[injection_id]
            print(f"⏹️ 停止故障: {injection_id}")
    
    def get_active_injections(self):
        """获取当前活跃的故障"""
        return list(self.active_injections.values())
    
    def get_injection_statistics(self):
        """获取故障注入统计"""
        stats = {
            'total_injections': len(self.injection_history),
            'active_injections': len(self.active_injections),
            'by_type': defaultdict(int),
            'detected_issues': len(self.detected_issues)
        }
        
        for injection in self.injection_history:
            stats['by_type'][injection['fault_type']] += 1
        
        return stats


class ChaosExperiment:
    """混沌实验"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.steps: List[Callable] = []
        self.results: List[Dict] = []
        self.hypothesis: str = ""
        self.steady_state_metrics: Dict = {}
        
    def add_step(self, step_func):
        """添加实验步骤"""
        self.steps.append(step_func)
    
    async def run_experiment(self):
        """运行混沌实验"""
        print(f"\n🧪 开始混沌实验: {self.name}")
        print(f"📝 {self.description}")
        
        result = {
            'experiment': self.name,
            'hypothesis': self.hypothesis,
            'start_time': datetime.now(),
            'steps': [],
            'success': True
        }
        
        for i, step in enumerate(self.steps):
            step_result = await step()
            result['steps'].append({
                'step': i + 1,
                'result': step_result
            })
            
            if not step_result.get('success', True):
                result['success'] = False
        
        result['end_time'] = datetime.now()
        result['duration'] = (result['end_time'] - result['start_time']).total_seconds()
        
        self.results.append(result)
        
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"\n{status} 实验完成! 耗时: {result['duration']:.2f}秒")
        
        return result


class ChaosEngine:
    """混沌工程引擎"""
    
    def __init__(self):
        self.fault_injector = FaultInjector()
        self.experiments: List[ChaosExperiment] = []
        self.system_health: Dict[str, Any] = {}
        
    def create_experiment(self, name, description):
        """创建混沌实验"""
        experiment = ChaosExperiment(name, description)
        self.experiments.append(experiment)
        return experiment
    
    async def run_complete_chaos_suite(self):
        """运行完整的混沌测试套件"""
        print("\n" + "="*80)
        print("🌪️ 高级混沌工程测试套件")
        print("="*80)
        
        # 实验1: 服务故障实验
        exp1 = self.create_experiment(
            "服务故障恢复实验",
            "测试系统在核心服务故障时的恢复能力"
        )
        exp1.hypothesis = "系统应该能够在10秒内从服务故障中恢复"
        
        async def exp1_step1():
            print("📊 步骤1: 记录系统稳定状态")
            self.system_health['baseline'] = {'status': 'healthy'}
            return {'success': True, 'message': '稳定状态记录完成'}
        
        async def exp1_step2():
            print("🎯 步骤2: 注入服务故障")
            await self.fault_injector.inject_service_failure("core-api", duration=5.0)
            return {'success': True, 'message': '故障注入完成'}
        
        async def exp1_step3():
            print("⏱️ 步骤3: 观察恢复过程")
            await asyncio.sleep(3.0)
            return {'success': True, 'message': '恢复观察完成'}
        
        exp1.add_step(exp1_step1)
        exp1.add_step(exp1_step2)
        exp1.add_step(exp1_step3)
        
        await exp1.run_experiment()
        
        # 实验2: 网络分区实验
        exp2 = self.create_experiment(
            "网络分区恢复实验",
            "测试系统在网络分区情况下的处理能力"
        )
        exp2.hypothesis = "系统应该能够处理30%的网络分区"
        
        async def exp2_step1():
            print("📊 步骤1: 记录网络状态")
            return {'success': True}
        
        async def exp2_step2():
            print("🎯 步骤2: 注入网络分区")
            await self.fault_injector.inject_network_partition("database-cluster", 0.3, duration=8.0)
            return {'success': True}
        
        exp2.add_step(exp2_step1)
        exp2.add_step(exp2_step2)
        
        await exp2.run_experiment()
        
        # 实验3: 延迟故障实验
        exp3 = self.create_experiment(
            "延迟故障实验",
            "测试系统在高延迟情况下的表现"
        )
        
        async def exp3_step1():
            print("🎯 步骤: 注入延迟故障")
            await self.fault_injector.inject_latency("api-gateway", 0.2, 1.5, duration=5.0)
            return {'success': True}
        
        exp3.add_step(exp3_step1)
        await exp3.run_experiment()
        
        # 实验4: 复合故障实验
        exp4 = self.create_experiment(
            "复合故障实验",
            "测试系统在多个故障同时发生时的表现"
        )
        
        async def exp4_compound():
            print("🎯 步骤: 同时注入多个故障")
            await asyncio.gather(
                self.fault_injector.inject_error("payment-service", 0.3, duration=5.0),
                self.fault_injector.inject_latency("user-service", 0.1, 0.8, duration=5.0)
            )
            return {'success': True}
        
        exp4.add_step(exp4_compound)
        await exp4.run_experiment()
        
        print("\n" + "="*80)
        print("🏆 混沌工程测试套件完成!")
        print("="*80)
        
        stats = self.fault_injector.get_injection_statistics()
        print(f"\n📊 统计:")
        print(f"  总故障数: {stats['total_injections']}")
        print(f"  活跃故障: {stats['active_injections']}")
        print(f"  故障类型统计: {dict(stats['by_type'])}")


async def main():
    """混沌工程演示"""
    print("="*80)
    print("🌪️ Agent永续自进化系统 - 高级混沌工程")
    print("="*80)
    
    engine = ChaosEngine()
    
    # 运行完整的混沌测试套件
    await engine.run_complete_chaos_suite()
    
    print("\n✅ 混沌工程演示完成!")


if __name__ == "__main__":
    asyncio.run(main())

