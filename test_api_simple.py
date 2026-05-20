
"""
硅基流动 API 简单测试
"""

import requests
import json

BASE_URL = "https://api.siliconflow.cn/v1"
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")

def test_api():
    """简单测试API"""
    print("=" * 60)
    print("硅基流动 API 测试")
    print("=" * 60)
    url = BASE_URL + "/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    messages = [
        {"role": "system", "content": "你是一个友好的AI助手。"},
        {"role": "user", "content": "你好！请简单介绍一下你自己。"}
    ]
    payload = {
        "model": "Qwen/Qwen3-30B-A3B-Thinking-2507",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }
    print("\n正在发送请求...")
    print(f"API URL: {url}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\n响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 请求成功!")
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                content = choice.get("message", {}).get("content", "")
                print("\n响应内容:")
                print(content)
            if "usage" in result:
                usage = result["usage"]
                print(f"\n📊 Token 使用:")
                print(f"  输入: {usage.get('prompt_tokens', 0)}")
                print(f"  输出: {usage.get('completion_tokens', 0)}")
                print(f"  总计: {usage.get('total_tokens', 0)}")
            return True
        else:
            print(f"\n❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 开始测试\n")
    success = test_api()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败")

