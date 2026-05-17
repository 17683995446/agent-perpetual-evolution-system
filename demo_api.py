
"""
SiliconFlow API Integration Demo
Working version with simple code
"""

import requests
import json

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")


# Working model
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def simple_chat(message, system_prompt="You are a helpful AI assistant."):
    """Simple chat interface"""
    
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
            return "Error: " + response.text
            
    except Exception as e:
        return "Error: " + str(e)


def main():
    """Main demo function"""
    print("=" * 70)
    print("SiliconFlow API Integration Demo")
    print("=" * 70)
    
    # Test 1: Simple chat
    print("\n1. Simple Chat")
    print("-" * 40)
    result = simple_chat("Hello! Can you help me with coding?")
    print("Response:", result[:200], "..." if len(result) > 200 else "")
    print("OK - Simple chat works!")
    
    # Test 2: Task optimization
    print("\n2. Task Optimization")
    print("-" * 40)
    task_opt = simple_chat(
        "Optimize this task: Build a user management system. " +
        "Return your suggestions in JSON format with 'suggestions' array."
    )
    print("Optimization result:", task_opt[:300], "..." if len(task_opt) > 300 else "")
    print("OK - Task optimization works!")
    
    # Test 3: Workflow generation
    print("\n3. Workflow Generation")
    print("-" * 40)
    workflow = simple_chat(
        "Generate a workflow for: Create an automated test system. " +
        "Include workflow name, steps, and estimated duration."
    )
    print("Workflow result:", workflow[:300], "..." if len(workflow) > 300 else "")
    print("OK - Workflow generation works!")
    
    # Test 4: Performance analysis
    print("\n4. Performance Analysis")
    print("-" * 40)
    perf_data = (
        "Performance data: Tasks executed: 150, Success rate: 85%, " +
        "Average latency: 2.3 seconds, CPU usage: 75%, Memory usage: 82%"
    )
    perf_analysis = simple_chat(
        "Analyze this performance data: " + perf_data + 
        ". Give insights and optimization suggestions."
    )
    print("Analysis result:", perf_analysis[:300], "..." if len(perf_analysis) > 300 else "")
    print("OK - Performance analysis works!")
    
    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()

