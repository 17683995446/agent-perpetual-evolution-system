
"""
硅基流动 API 简单测试
"""

import requests
import json

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")


def test_api():
    """简单测试API"""
    print("=" * 60)
    print("SiliconFlow API Test")
    print("=" * 60)
    
    url = BASE_URL + "/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }
    
    messages = [
        {"role": "system", "content": "You are a friendly AI assistant."},
        {"role": "user", "content": "Hello! Please introduce yourself briefly."}
    ]
    
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    print("\nSending request...")
    print(f"API URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\nSUCCESS!")
            
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                content = choice.get("message", {}).get("content", "")
                
                print("\nResponse:")
                print(content)
            
            if "usage" in result:
                usage = result["usage"]
                print(f"\nToken Usage:")
                print(f"  Input: {usage.get('prompt_tokens', 0)}")
                print(f"  Output: {usage.get('completion_tokens', 0)}")
                print(f"  Total: {usage.get('total_tokens', 0)}")
            
            return True
        else:
            print(f"\nFAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    print("\nStarting test...\n")
    
    success = test_api()
    
    if success:
        print("\nTest PASSED!")
    else:
        print("\nTest FAILED")

