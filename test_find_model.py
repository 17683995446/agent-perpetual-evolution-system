
"""
硅基流动 API 简单测试 - 尝试不同的模型
"""

import requests
import json

BASE_URL = "https://api.siliconflow.cn/v1"
# 使用环境变量管理敏感配置
import os
API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

if not API_KEY:
    raise EnvironmentError("请设置环境变量 SILICONFLOW_API_KEY")


def get_available_models():
    """获取可用模型列表"""
    url = BASE_URL + "/models"
    headers = {
        "Authorization": "Bearer " + API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("\nAvailable models:")
            
            if "data" in result:
                for model in result["data"]:
                    print(f"  - {model.get('id', '')}")
            
            return result
        else:
            print(f"Failed to get models: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting models: {e}")
        return None

def test_with_model(model_name):
    """测试特定模型"""
    print(f"\nTesting model: {model_name}")
    
    url = BASE_URL + "/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! What can you help with?"}
    ]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 256
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✓ Success!")
            
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                content = choice.get("message", {}).get("content", "")
                
                print(f"\nResponse:")
                print(content)
            
            if "usage" in result:
                usage = result["usage"]
                print(f"\nToken Usage: {usage.get('total_tokens', 0)}")
            
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SiliconFlow API Testing")
    print("=" * 60)
    
    # 先尝试获取可用模型列表
    print("\nStep 1: Getting available models...")
    get_available_models()
    
    # 尝试一些常见的模型
    test_models = [
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "Qwen/Qwen2.5-7B-Instruct",
        "THUDM/glm-4-9b-chat",
        "meta-llama/Llama-3.2-3B-Instruct"
    ]
    
    print("\n" + "=" * 60)
    print("Step 2: Testing models")
    print("=" * 60)
    
    success_count = 0
    for model in test_models:
        if test_with_model(model):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Result: {success_count}/{len(test_models)} models worked!")
    print("=" * 60)

