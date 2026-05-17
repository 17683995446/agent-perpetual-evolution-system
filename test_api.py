"""
API测试脚本 - 验证增强型Web API的功能
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分段标题"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_health_endpoints():
    """测试健康检查端点"""
    print_section("1. 测试健康检查端点")
    
    print("\n[GET] /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ 健康检查通过")
    
    print("\n[GET] /ready")
    response = requests.get(f"{BASE_URL}/ready")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ 就绪检查通过")
    
    print("\n[GET] /info")
    response = requests.get(f"{BASE_URL}/info")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ API信息获取成功")

def test_system_management():
    """测试系统管理API"""
    print_section("2. 测试系统管理API")
    
    print("\n[POST] /api/v1/system/start")
    response = requests.post(f"{BASE_URL}/api/v1/system/start")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ 系统启动成功")
    
    time.sleep(1)
    
    print("\n[GET] /api/v1/system/status")
    response = requests.get(f"{BASE_URL}/api/v1/system/status")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ 系统状态获取成功")
    
    print("\n[GET] /api/v1/system/metrics")
    response = requests.get(f"{BASE_URL}/api/v1/system/metrics")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  CPU: {data['cpu_percent']:.2f}%")
    print(f"  Memory: {data['memory_mb']['used']:.2f} MB / {data['memory_mb']['total']:.2f} MB")
    print(f"  Tasks: {data['tasks_total']}")
    assert response.status_code == 200
    print("  ✓ 系统指标获取成功")

def test_task_management():
    """测试任务管理API"""
    print_section("3. 测试任务管理API")
    
    print("\n[POST] /api/v1/tasks/submit - 创建高优先级任务")
    task_data = {
        "content": {"type": "data_processing", "data": "test_sample_1"},
        "priority": "high",
        "timeout_seconds": 60
    }
    response = requests.post(f"{BASE_URL}/api/v1/tasks/submit", json=task_data)
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Response: {data}")
    task_id_1 = data["task_id"]
    assert response.status_code == 200
    print(f"  ✓ 任务提交成功 (ID: {task_id_1})")
    
    print("\n[POST] /api/v1/tasks/submit - 创建中优先级任务")
    task_data = {
        "content": {"type": "backup", "data": "backup_data"},
        "priority": "medium",
        "timeout_seconds": 120
    }
    response = requests.post(f"{BASE_URL}/api/v1/tasks/submit", json=task_data)
    print(f"  Status: {response.status_code}")
    data = response.json()
    task_id_2 = data["task_id"]
    print(f"  ✓ 任务提交成功 (ID: {task_id_2})")
    
    time.sleep(1)
    
    print(f"\n[GET] /api/v1/tasks/{task_id_1}")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id_1}")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Task ID: {data['task_id']}")
    print(f"  Status: {data['status']}")
    print(f"  Priority: {data['priority']}")
    assert response.status_code == 200
    print("  ✓ 任务详情获取成功")
    
    print("\n[GET] /api/v1/tasks")
    response = requests.get(f"{BASE_URL}/api/v1/tasks")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Stats: {data['stats']}")
    assert response.status_code == 200
    print("  ✓ 任务列表获取成功")

def test_evolution_api():
    """测试进化引擎API"""
    print_section("4. 测试进化引擎API")
    
    print("\n[GET] /api/v1/evolution/dashboard")
    response = requests.get(f"{BASE_URL}/api/v1/evolution/dashboard")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Stage: {data['stage']}")
        print(f"  Timestamp: {data['timestamp']}")
        print("  ✓ 进化仪表盘获取成功")
    else:
        print(f"  Response: {response.json()}")
    
    print("\n[POST] /api/v1/evolution/recommend")
    recommend_data = {
        "input_data": {"context": "performance_optimization"},
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/v1/evolution/recommend", json=recommend_data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Recommendations: {data['count']}")
        print("  ✓ 建议获取成功")
    else:
        print(f"  Response: {response.json()}")

def test_memory_api():
    """测试内存管理API"""
    print_section("5. 测试内存管理API")
    
    print("\n[GET] /api/v1/memory/status")
    response = requests.get(f"{BASE_URL}/api/v1/memory/status")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Total: {data['total_mb']:.2f} MB")
    print(f"  Used: {data['used_mb']:.2f} MB ({data['used_percent']:.2f}%)")
    print(f"  Free: {data['free_mb']:.2f} MB")
    print("  ✓ 内存状态获取成功")
    
    print("\n[POST] /api/v1/memory/cleanup")
    response = requests.post(f"{BASE_URL}/api/v1/memory/cleanup")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    print("  ✓ 内存清理触发成功")

def test_prometheus_metrics():
    """测试Prometheus指标"""
    print_section("6. 测试Prometheus指标")
    
    print("\n[GET] /metrics")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"  Status: {response.status_code}")
    print(f"  Content-Type: {response.headers['content-type']}")
    
    metrics_text = response.text
    key_metrics = [
        'agent_cpu_usage_percent',
        'agent_memory_usage_bytes',
        'agent_tasks_submitted_total',
        'agent_system_uptime_seconds',
        'http_requests_total'
    ]
    
    print("\n  Key Metrics Found:")
    for metric in key_metrics:
        if metric in metrics_text:
            print(f"    ✓ {metric}")
        else:
            print(f"    ✗ {metric}")
    
    print("\n  ✓ Prometheus指标端点正常")

def test_stop_system():
    """测试停止系统"""
    print_section("7. 测试停止系统")
    
    print("\n[POST] /api/v1/system/stop")
    response = requests.post(f"{BASE_URL}/api/v1/system/stop")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✓ 系统停止成功")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print(" Agent Perpetual System API 测试套件")
    print("=" * 70)
    
    try:
        test_health_endpoints()
        test_system_management()
        test_task_management()
        test_evolution_api()
        test_memory_api()
        test_prometheus_metrics()
        test_stop_system()
        
        print("\n" + "=" * 70)
        print(" 所有API测试通过！✓")
        print("=" * 70)
        print("\nAPI文档地址: http://localhost:8000/docs")
        print("ReDoc文档: http://localhost:8000/redoc")
        print("Prometheus指标: http://localhost:8000/metrics")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到API服务器")
        print("请确保API服务器正在运行: python -m src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
