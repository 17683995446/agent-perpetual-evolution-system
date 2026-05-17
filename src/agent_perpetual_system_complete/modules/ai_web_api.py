
"""
AI进化引擎 Web API 端点集成
添加硅基流动API支持的AI进化引擎端点
"""

import asyncio
import psutil
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


# 配置
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

MODEL = "Qwen/Qwen2.5-7B-Instruct"
URL = "https://api.siliconflow.cn/v1/chat/completions"


# ==================== 数据模型 ====================

class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    context: str
    max_tokens: Optional[int] = 1024


class AIOptimizationRequest(BaseModel):
    """AI优化请求"""
    metrics: Dict[str, Any]
    focus_area: Optional[str] = "performance"


class PerformanceDataRequest(BaseModel):
    """性能数据请求"""
    cpu_percent: float
    memory_percent: float
    task_count: int
    success_rate: float


# ==================== AI分析函数 ====================

def call_siliconflow_api(messages, max_tokens=1024) -> Optional[str]:
    """调用硅基流动API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"API Error: {response.text}"
            
    except Exception as e:
        return f"Request Error: {str(e)}"


async def analyze_performance(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """分析性能数据"""
    system_prompt = """You are an expert performance analyst for AI agent systems.
Analyze performance metrics and provide:
1. Key findings (2-3 points)
2. Potential bottlenecks
3. Quick optimization wins

Be concise and use Chinese if appropriate."""

    user_message = f"""Analyze these performance metrics:
- CPU: {metrics.get('cpu_percent', 0):.1f}%
- Memory: {metrics.get('memory_percent', 0):.1f}%
- Tasks: {metrics.get('task_count', 0)} total
- Success Rate: {metrics.get('success_rate', 0)*100:.1f}%

Provide structured analysis."""

    analysis = call_siliconflow_api([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    return {
        "analysis": analysis,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }


async def generate_optimization_suggestions(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """生成优化建议"""
    system_prompt = """You are an optimization expert for AI agent systems.
Generate specific, actionable optimization suggestions.
Return as JSON array with: title, description, priority (critical/high/medium/low), expected_improvement.
Return ONLY JSON array."""

    user_message = f"""Generate optimization suggestions for:
- CPU: {metrics.get('cpu_percent', 0):.1f}%
- Memory: {metrics.get('memory_percent', 0):.1f}%
- Success Rate: {metrics.get('success_rate', 0)*100:.1f}%

Return JSON array."""

    suggestions_text = call_siliconflow_api([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ], max_tokens=2048)

    # 尝试解析JSON
    suggestions = []
    if suggestions_text:
        try:
            import json
            start = suggestions_text.find("[")
            end = suggestions_text.rfind("]")
            if start != -1 and end != -1:
                suggestions = json.loads(suggestions_text[start:end+1])
        except Exception:
            suggestions = [{"title": "Default", "description": suggestions_text, "priority": "medium"}]

    return {
        "suggestions": suggestions,
        "count": len(suggestions),
        "timestamp": datetime.now().isoformat()
    }


async def chat_with_ai(message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """与AI聊天"""
    if system_prompt is None:
        system_prompt = "You are a helpful AI assistant for an agent system."

    response = call_siliconflow_api([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ])

    return {
        "response": response,
        "timestamp": datetime.now().isoformat()
    }


# ==================== API端点示例 ====================

async def get_ai_dashboard() -> Dict[str, Any]:
    """获取AI驱动的仪表盘数据"""
    # 收集当前系统指标
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
    }

    # 并行获取分析和优化建议
    analysis_task = analyze_performance(metrics)
    suggestions_task = generate_optimization_suggestions(metrics)

    analysis, suggestions = await asyncio.gather(analysis_task, suggestions_task)

    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "analysis": analysis,
        "suggestions": suggestions,
        "system_health": calculate_health(metrics)
    }


def calculate_health(metrics: Dict[str, float]) -> str:
    """计算系统健康状态"""
    score = 100
    
    cpu = metrics.get("cpu_percent", 0)
    if cpu > 90: score -= 30
    elif cpu > 80: score -= 15
    
    memory = metrics.get("memory_percent", 0)
    if memory > 90: score -= 30
    elif memory > 85: score -= 15
    
    if score >= 80: return "healthy"
    elif score >= 60: return "warning"
    return "critical"


# ==================== 主测试 ====================

async def main():
    """测试API端点"""
    print("=" * 70)
    print("AI进化引擎 Web API 端点测试")
    print("=" * 70)

    # 测试1: 获取AI仪表盘
    print("\n1. 获取AI仪表盘...")
    dashboard = await get_ai_dashboard()
    
    print(f"   时间戳: {dashboard['timestamp']}")
    print(f"   系统健康: {dashboard['system_health']}")
    print(f"   CPU: {dashboard['metrics']['cpu_percent']:.1f}%")
    print(f"   内存: {dashboard['metrics']['memory_percent']:.1f}%")
    
    print(f"\n   AI分析:")
    print(f"   {dashboard['analysis']['analysis'][:150]}...")
    
    print(f"\n   优化建议 ({dashboard['suggestions']['count']}条):")
    for i, sug in enumerate(dashboard['suggestions']['suggestions'][:2], 1):
        print(f"   {i}. {sug.get('title', 'N/A')}")

    # 测试2: 聊天
    print("\n2. 测试AI聊天...")
    chat_result = await chat_with_ai("Hello! What can you do?")
    print(f"   AI回复: {chat_result['response'][:100]}...")

    print("\n" + "=" * 70)
    print("API端点测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

