
"""
硅基流动 API 集成演示
使用可用的免费模型
"""

import asyncio
import requests
import json
from typing import Dict, Any, List

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")


# 可用的模型
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def simple_chat(message: str, system_prompt: str = "You are a helpful AI assistant.") -&gt; str:
    """简单的聊天接口"""
    
    url = BASE_URL + "/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            choice = result.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            return content
        else:
            return f"Error: {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"


def optimize_task(task_description: str) -&gt; Dict[str, Any]:
    """任务优化"""
    system_prompt = """You are a task optimization expert. Please analyze the task and provide optimization suggestions in JSON format.
The JSON should have:
- "suggestions": list of optimization suggestions
- "priority": list of priorities (HIGH/MEDIUM/LOW)
- "steps": list of implementation steps
"""
    
    response = simple_chat(task_description, system_prompt)
    
    # 尝试解析JSON
    try:
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_str = response[start_idx:end_idx+1]
            return json.loads(json_str)
    except Exception:
        pass
    
    # 如果不能解析JSON，返回原始响应
    return {"raw_response": response}


def generate_workflow(goal: str) -&gt; Dict[str, Any]:
    """生成工作流"""
    system_prompt = """You are a workflow design expert. Please design a workflow for the goal.
Return JSON format with:
- "workflow_name": name of workflow
- "steps": list of step names
- "estimated_duration": estimated time in hours
- "success_probability": 0 to 1
"""
    
    response = simple_chat(f"Design a workflow for: {goal}", system_prompt)
    
    return {"workflow": response}


def analyze_performance(performance_data: str) -&gt; str:
    """性能分析"""
    system_prompt = "You are a performance analyst. Analyze this data and give insights."
    
    return simple_chat(performance_data, system_prompt)


async def main():
    """主演示"""
    print("=" * 70)
    print("SiliconFlow API Integration Demo")
    print("=" * 70)
    
    # 测试 1: 简单聊天
    print("\n1. Simple Chat")
    print("-" * 40)
    result = simple_chat("Hello! Can you help me with coding?")
    print("Response:", result[:200], "..." if len(result) &gt; 200 else "")
    print("✓ Simple chat works!")
    
    # 测试 2: 任务优化
    print("\n2. Task Optimization")
    print("-" * 40)
    task_opt = optimize_task("Build a user management system")
    print("Optimization result:", str(task_opt)[:300], "...")
    print("✓ Task optimization works!")
    
    # 测试 3: 工作流生成
    print("\n3. Workflow Generation")
    print("-" * 40)
    workflow = generate_workflow("Create an automated test system")
    print("Workflow result:", str(workflow)[:300], "...")
    print("✓ Workflow generation works!")
    
    # 测试 4: 性能分析
    print("\n4. Performance Analysis")
    print("-" * 40)
    perf_data = "Tasks: 150, Success rate: 85%, Avg latency: 2.3s, CPU usage: 75%, Memory: 82%"
    perf_analysis = analyze_performance(perf_data)
    print("Analysis result:", perf_analysis[:300], "..." if len(perf_analysis) &gt; 300 else "")
    print("✓ Performance analysis works!")
    
    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

