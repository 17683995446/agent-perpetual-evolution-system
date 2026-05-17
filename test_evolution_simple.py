
"""
AI进化引擎 - 简化测试版本
"""

import asyncio
import time
import psutil
import requests
import json

# 配置
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

MODEL = "Qwen/Qwen2.5-7B-Instruct"
URL = "https://api.siliconflow.cn/v1/chat/completions"


def call_api(messages):
    """调用API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    response = requests.post(URL, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        return f"Error: {response.text}"


def get_metrics():
    """获取系统指标"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
    }


def analyze_with_ai(metrics):
    """AI分析"""
    messages = [
        {"role": "system", "content": "You are a performance analyst. Analyze metrics and give suggestions in Chinese."},
        {"role": "user", "content": f"分析这些指标: CPU={metrics['cpu_percent']:.1f}%, 内存={metrics['memory_percent']:.1f}%"}
    ]
    
    return call_api(messages)


async def main():
    """主函数"""
    print("=" * 70)
    print("AI进化引擎测试")
    print("=" * 70)
    
    # 1. 获取系统指标
    print("\n1. 获取系统指标...")
    metrics = get_metrics()
    print(f"   CPU: {metrics['cpu_percent']:.1f}%")
    print(f"   内存: {metrics['memory_percent']:.1f}%")
    print(f"   磁盘: {metrics['disk_percent']:.1f}%")
    
    # 2. AI分析
    print("\n2. AI分析...")
    analysis = analyze_with_ai(metrics)
    print(f"   分析结果: {analysis[:200]}...")
    
    print("\n3. 性能监控...")
    
    for i in range(3):
        metrics = get_metrics()
        print(f"   [{i+1}] CPU: {metrics['cpu_percent']:.1f}%, 内存: {metrics['memory_percent']:.1f}%")
        await asyncio.sleep(2)
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

