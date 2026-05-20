
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
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

class SimpleSiliconFlowClient:
    """简单的硅基流动 API 客户端"""
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.default_model = "Qwen/Qwen3-30B-A3B-Thinking-2507"

    def chat_completion_sync(self, messages, model=None, temperature=0.7, max_tokens=1024):
        """同步聊天补全"""
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

    async def chat_completion_async(self, messages, model=None, temperature=0.7, max_tokens=1024):
        """异步聊天补全"""
        import aiohttp
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload, timeout=30) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """主函数"""
    print("=" * 60)
    print("Simple SiliconFlow API Test")
    print("=" * 60)
    client = SimpleSiliconFlowClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! What can you do?"}
    ]
    print("\nTesting sync chat completion...")
    result = client.chat_completion_sync(messages)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Success!")
        print(result.get("choices", [{}])[0].get("message", {}).get("content", ""))
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    main()

