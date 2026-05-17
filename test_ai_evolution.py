"""
AI进化引擎测试 - 完整测试硅基流动免费模型
"""

import requests
import json
import time
from datetime import datetime


class AIEvolutionTester:
    """AI进化引擎测试器"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 可用的免费模型列表
        self.free_models = [
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "THUDM/glm-4-9b-chat",
            "deepseek-ai/DeepSeek-V2.5"
        ]
        
        self.test_results = []
    
    def test_model(self, model_name, test_message="你好，请简单介绍一下自己。"):
        """测试单个模型"""
        print(f"\n🤖 测试模型: {model_name}")
        print(f"   消息: {test_message}")
        
        start_time = time.time()
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个友好的AI助手。"},
                {"role": "user", "content": test_message}
            ],
            "temperature": 0.7,
            "max_tokens": 512
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                print(f"   ✅ 成功!")
                print(f"   ⏱️ 响应时间: {duration:.2f}秒")
                print(f"   📊 Token: 输入{usage.get('prompt_tokens', 0)} → 输出{usage.get('completion_tokens', 0)}")
                
                return {
                    "model": model_name,
                    "success": True,
                    "response": content[:100] + "...",
                    "duration": duration,
                    "usage": usage
                }
            else:
                print(f"   ❌ 失败: 状态码 {response.status_code}")
                return {
                    "model": model_name,
                    "success": False,
                    "error": response.text[:200],
                    "duration": duration
                }
                
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            return {
                "model": model_name,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def run_full_test(self):
        """运行完整测试"""
        print("=" * 70)
        print("🧬 Agent永续自进化系统 - AI进化引擎测试")
        print("=" * 70)
        print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📡 API地址: {self.base_url}")
        print(f"🔑 API密钥: {self.api_key[:15]}...")
        
        print(f"\n📋 将测试 {len(self.free_models)} 个免费模型:")
        for model in self.free_models:
            print(f"   - {model}")
        
        print("\n" + "=" * 70)
        print("🚀 开始测试...")
        print("=" * 70)
        
        success_count = 0
        fail_count = 0
        
        for i, model in enumerate(self.free_models, 1):
            print(f"\n[{i}/{len(self.free_models)}]")
            result = self.test_model(model)
            self.test_results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                fail_count += 1
        
        # 打印总结
        self.print_summary(success_count, fail_count)
        
        return self.test_results
    
    def print_summary(self, success_count, fail_count):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        
        print(f"\n✅ 成功: {success_count}/{len(self.free_models)} 个模型")
        print(f"❌ 失败: {fail_count}/{len(self.free_models)} 个模型")
        
        if success_count > 0:
            successful_models = [r for r in self.test_results if r["success"]]
            
            print(f"\n🏆 可用模型排名 (按响应时间):")
            successful_models.sort(key=lambda x: x["duration"])
            
            for i, result in enumerate(successful_models, 1):
                print(f"   {i}. {result['model']}")
                print(f"      响应时间: {result['duration']:.2f}秒")
                print(f"      输出Token: {result['usage'].get('completion_tokens', 0)}")
        
        print("\n" + "=" * 70)
        if success_count == len(self.free_models):
            print("🎉 所有模型测试成功！LLM服务完全正常！")
        elif success_count > 0:
            print(f"⚠️  部分模型可用 ({success_count}/{len(self.free_models)})")
        else:
            print("❌ 所有模型测试失败，请检查API密钥和网络连接")
        print("=" * 70)
    
    def test_task_optimization(self):
        """测试任务优化功能"""
        print("\n" + "=" * 70)
        print("📝 测试AI任务优化功能")
        print("=" * 70)
        
        task = """
任务：开发一个简单的待办事项管理系统

需求：
1. 添加待办事项
2. 查看待办事项列表
3. 标记完成
4. 删除待办事项
5. 数据持久化存储
        """.strip()
        
        prompt = f"""你是一个专业的任务优化顾问。请分析以下任务，给出优化建议：

{task}

请以JSON格式输出，包含：
- 任务分解建议
- 技术栈推荐
- 潜在风险
- 优化建议
"""
        
        payload = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": [
                {"role": "system", "content": "你是一个专业的任务优化顾问。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        print(f"\n🚀 发送任务优化请求...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print(f"\n✅ 任务优化成功!")
                print(f"⏱️ 耗时: {duration:.2f}秒")
                print(f"\n📋 AI优化建议:")
                print("-" * 70)
                print(content)
                print("-" * 70)
                
                return True
            else:
                print(f"❌ 任务优化失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            return False


def main():
    """主函数"""
    import simple_config
    
    config = simple_config.get_config()
    
    if not config.is_valid():
        print("❌ 请先配置API密钥!")
        config.help()
        return
    
    print("\n" + "=" * 70)
    print("🧬 Agent永续自进化系统 - AI进化引擎完整测试")
    print("=" * 70)
    
    tester = AIEvolutionTester(config.get_api_key())
    
    # 1. 测试所有免费模型
    tester.run_full_test()
    
    # 2. 测试任务优化功能
    tester.test_task_optimization()
    
    print("\n🎉 AI进化引擎测试完成！")


if __name__ == "__main__":
    main()

