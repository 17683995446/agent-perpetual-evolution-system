"""
LLM服务测试 - 检查硅基流动API是否正常
使用超简单配置系统！
"""

import sys
import requests

try:
    import simple_config
    CONFIG_AVAILABLE = True
except:
    CONFIG_AVAILABLE = False
    print("⚠️  配置系统不可用，请直接设置API密钥")


def test_api_connection(api_key, test_message="你好，请简单介绍一下自己。"):
    """
    测试硅基流动API连接
    
    Args:
        api_key: API密钥
        test_message: 测试消息
    
    Returns:
        测试结果字典
    """
    base_url = "https://api.siliconflow.cn/v1"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 测试模型 - 使用最常用的Qwen模型
    test_model = "Qwen/Qwen2.5-7B-Instruct"
    
    payload = {
        "model": test_model,
        "messages": [
            {"role": "system", "content": "你是一个友好的AI助手。"},
            {"role": "user", "content": test_message}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    print(f"\n🚀 开始测试LLM服务...")
    print(f"📡 API地址: {base_url}")
    print(f"🤖 使用模型: {test_model}")
    
    try:
        print(f"\n⏳ 正在发送请求...")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            choice = result.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            usage = result.get("usage", {})
            
            print(f"\n✅ 连接成功！")
            print(f"\n📝 AI回复:")
            print(content)
            
            print(f"\n📊 Token使用情况:")
            print(f"   输入: {usage.get('prompt_tokens', 0)} tokens")
            print(f"   输出: {usage.get('completion_tokens', 0)} tokens")
            print(f"   总计: {usage.get('total_tokens', 0)} tokens")
            
            return {
                "success": True,
                "status": response.status_code,
                "response": content,
                "usage": usage
            }
        else:
            print(f"\n❌ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return {
                "success": False,
                "status": response.status_code,
                "error": response.text
            }
            
    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时，请检查网络连接")
        return {
            "success": False,
            "error": "请求超时"
        }
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败，请检查网络连接")
        return {
            "success": False,
            "error": "连接失败"
        }
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def quick_status_check():
    """快速状态检查"""
    print("=" * 70)
    print("🔍 Agent永续自进化系统 - LLM服务状态检查")
    print("=" * 70)
    
    api_key = None
    
    # 尝试使用简化配置系统
    if CONFIG_AVAILABLE:
        print("\n📦 检查简化配置系统...")
        try:
            config = simple_config.get_config()
            if config.is_valid():
                api_key = config.get_api_key()
                print(f"✅ 找到配置！API密钥: {api_key[:10]}...")
        except Exception as e:
            print(f"⚠️  简化配置系统读取失败: {e}")
    
    # 如果配置系统没有，尝试直接问用户
    if not api_key:
        print("\n💡 提示：您可以通过以下方式配置：")
        print("   1. 运行: python quick_setup.py")
        print("   2. 或者设置环境变量: export SILICONFLOW_API_KEY=sk-...")
        print("   3. 或者直接在此处输入")
        
        try:
            api_key = input("\n🔑 请输入API密钥 (直接回车跳过): ").strip()
        except:
            print("\n⏭️  跳过手动输入")
    
    if not api_key:
        print("\n❌ 没有配置API密钥，无法测试LLM服务")
        print("\n📝 请按以下步骤配置：")
        print("   1. 运行: python quick_setup.py")
        print("   2. 或者设置环境变量")
        return False
    
    # 进行实际测试
    print(f"\n" + "=" * 70)
    print("🧪 开始测试...")
    print("=" * 70)
    
    result = test_api_connection(api_key)
    
    print(f"\n" + "=" * 70)
    if result.get("success"):
        print("🎉 LLM服务状态: 正常！")
    else:
        print("⚠️  LLM服务状态: 存在问题")
    print("=" * 70)
    
    return result.get("success", False)


if __name__ == "__main__":
    quick_status_check()
