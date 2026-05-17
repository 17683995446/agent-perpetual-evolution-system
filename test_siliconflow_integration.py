
"""
测试硅基流动API集成
验证API调用、任务优化、进化引擎等功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent_perpetual_system_complete.modules.siliconflow_integration import (
    SiliconFlowService,
    SiliconFlowConfig,
    SiliconFlowModel,
)
from src.agent_perpetual_system_complete.modules.config_manager import ConfigManager


async def test_simple_chat():
    """测试简单聊天"""
    print("\n" + "=" * 60)
    print("测试 1: 简单聊天")
    print("=" * 60)
    
    config_manager = ConfigManager()
    api_key = config_manager.get_siliconflow_api_key()
    
    if not api_key:
        print("❌ 未配置API密钥")
        return False
    
    print(f"✅ 使用API密钥: {api_key[:20]}...")
    
    service = SiliconFlowService(api_key)
    await service.initialize()
    
    try:
        response = await service.simple_chat(
            "你好！请简单介绍一下你自己。",
            system_prompt="你是一个友好的AI助手"
        )
        
        print(f"\n✅ 响应:\n{response}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_task_optimization():
    """测试任务优化"""
    print("\n" + "=" * 60)
    print("测试 2: 任务优化")
    print("=" * 60)
    
    config_manager = ConfigManager()
    api_key = config_manager.get_siliconflow_api_key()
    
    service = SiliconFlowService(api_key)
    await service.initialize()
    
    try:
        task_description = """
开发一个用户管理系统，包含以下功能：
- 用户注册和登录
- 用户信息管理
- 权限控制
- 数据统计
        """.strip()
        
        result = await service.task_optimizer.optimize_task_execution(
            task_description,
            execution_history=[]
        )
        
        print(f"\n✅ 优化结果:\n{result}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_workflow_generation():
    """测试工作流生成"""
    print("\n" + "=" * 60)
    print("测试 3: 工作流生成")
    print("=" * 60)
    
    config_manager = ConfigManager()
    api_key = config_manager.get_siliconflow_api_key()
    
    service = SiliconFlowService(api_key)
    await service.initialize()
    
    try:
        result = await service.task_optimizer.generate_workflow(
            goal="构建一个自动化测试系统",
            constraints=[
                "必须在1周内完成",
                "预算有限",
                "需要支持多种测试类型"
            ]
        )
        
        print(f"\n✅ 工作流生成结果:\n{result}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_performance_analysis():
    """测试性能分析"""
    print("\n" + "=" * 60)
    print("测试 4: 性能分析")
    print("=" * 60)
    
    config_manager = ConfigManager()
    api_key = config_manager.get_siliconflow_api_key()
    
    service = SiliconFlowService(api_key)
    await service.initialize()
    
    try:
        performance_data = {
            "tasks_executed": 150,
            "success_rate": 0.85,
            "average_latency": 2.3,
            "cpu_usage": 0.75,
            "memory_usage": 0.82,
            "error_types": {
                "timeout": 12,
                "resource_exhausted": 8,
                "invalid_input": 5
            },
            "peak_hours": ["09:00", "14:00", "18:00"]
        }
        
        result = await service.evolution_engine.analyze_performance(performance_data)
        
        print(f"\n✅ 性能分析结果:\n{result}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def test_evolution_suggestions():
    """测试进化建议"""
    print("\n" + "=" * 60)
    print("测试 5: 进化建议")
    print("=" * 60)
    
    config_manager = ConfigManager()
    api_key = config_manager.get_siliconflow_api_key()
    
    service = SiliconFlowService(api_key)
    await service.initialize()
    
    try:
        current_state = {
            "system_status": "RUNNING",
            "active_agents": 3,
            "task_queue_size": 42,
            "resource_utilization": {
                "cpu": 0.68,
                "memory": 0.72,
                "disk": 0.45
            },
            "recent_trends": {
                "task_volume": "increasing",
                "error_rate": "stable",
                "response_time": "improving"
            }
        }
        
        suggestions = await service.evolution_engine.get_evolution_suggestions(
            current_state=current_state,
            historical_data=[]
        )
        
        print(f"\n✅ 进化建议数: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n建议 {i}:")
            print(suggestion)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("硅基流动 API 集成测试")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 简单聊天
    results.append(("简单聊天", await test_simple_chat()))
    
    # 测试 2: 任务优化
    results.append(("任务优化", await test_task_optimization()))
    
    # 测试 3: 工作流生成
    results.append(("工作流生成", await test_workflow_generation()))
    
    # 测试 4: 性能分析
    results.append(("性能分析", await test_performance_analysis()))
    
    # 测试 5: 进化建议
    results.append(("进化建议", await test_evolution_suggestions()))
    
    # 打印结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\n总计: {total_passed}/{len(results)} 测试通过")
    
    return total_passed == len(results)


if __name__ == "__main__":
    try:
        # 首先检查是否安装了openai库
        import openai
    except ImportError:
        print("安装 openai 库...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai&gt;=1.0"])
    
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

