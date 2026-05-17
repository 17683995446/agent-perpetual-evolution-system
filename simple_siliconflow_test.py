
"""
硅基流动 API 简单测试
无需额外依赖
使用 requests 库直接调用 API
"""

import asyncio
import requests
import json
from typing import Dict, Any, Optional, List

BASE_URL = "https://api.siliconflow.cn/v1"

# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")



class SimpleSiliconFlowClient:
    """
    简单的硅基流动 API 客户端
    使用 requests 库直接调用 REST API
    """
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.default_model = "Qwen/Qwen3-30B-A3B-Thinking-2507"
    
    def chat_completion_sync(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -&gt; Dict[str, Any]:
        """
        同步版本的聊天补全
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -&gt; Dict[str, Any]:
        """
        异步版本的聊天补全
        """
        import httpx
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            return {"error": str(e)}


def quick_test():
    """快速测试"""
    print("\n" + "=" * 60)
    print("硅基流动 API 快速测试")
    print("=" * 60)
    
    client = SimpleSiliconFlowClient()
    
    # 简单的聊天
    messages = [
        {"role": "system", "content": "你是一个友好的AI助手。"},
        {"role": "user", "content": "你好！请简单介绍一下你自己。"}
    ]
    
    print("\n发送消息...")
    result = client.chat_completion_sync(messages)
    
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        return False
    else:
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        
        print("\n✅ 响应:")
        print(content)
        
        usage = result.get("usage", {})
        print(f"\n📊 Token 使用: {usage}")
        
        return True


def test_task_optimization():
    """测试任务优化"""
    print("\n" + "=" * 60)
    print("任务优化测试")
    print("=" * 60)
    
    client = SimpleSiliconFlowClient()
    
    task_description = """
我需要开发一个用户管理系统，包含：
1. 用户注册和登录
2. 用户信息管理
3. 权限控制
4. 数据统计和分析
5. 系统监控
    """.strip()
    
    messages = [
        {"role": "system", "content": "你是一个专业的任务优化顾问。请分析任务并给出优化建议。以JSON格式输出结果。"},
        {"role": "user", "content": task_description}
    ]
    
    result = client.chat_completion_sync(messages, max_tokens=2048)
    
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        return False
    else:
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        
        print("\n✅ 优化建议:")
        print(content)
        
        return True


if __name__ == "__main__":
    print("\n🚀 开始硅基流动API集成测试\n")
    
    # 测试 1: 快速测试
    try:
        quick_test()
    except Exception as e:
        print(f"快速测试失败: {e}")
    
    # 测试 2: 任务优化
    try:
        test_task_optimization()
    except Exception as e:
        print(f"任务优化测试失败: {e}")
    
    print("\n✅ 测试完成！")

