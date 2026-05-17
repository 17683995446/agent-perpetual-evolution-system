"""
Test Interface Presentation Layer - 测试接口层（7个单词）

测试命令行接口和Web API接口。
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from datetime import datetime

from fastapi.testclient import TestClient
import pytest_asyncio


@pytest.fixture
def client():
    """创建FastAPI测试客户端"""
    from src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation import (
        app,
    )
    return TestClient(app)


class TestWebAPIPresentation:
    """Web API接口测试"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "2.0.0"

    def test_readiness_check(self, client):
        """测试就绪检查端点"""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "timestamp" in data

    def test_openapi_docs(self, client):
        """测试API文档端点"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_docs(self, client):
        """测试ReDoc文档端点"""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @patch(
        "src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation._system_started",
        False,
    )
    @patch(
        "src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation._system_controller",
        None,
    )
    @patch(
        "src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation._evolution_controller",
        None,
    )
    @patch(
        "src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation._task_service",
        None,
    )
    def test_system_not_started(self, client):
        """测试系统未启动时的API响应"""
        response = client.get("/api/v1/system/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["system_state"] == "stopped"
        assert data["uptime_seconds"] == 0.0

    def test_submit_task_unavailable(self, client):
        """测试系统未启动时提交任务"""
        request_data = {
            "content": {"type": "test", "data": "value"},
            "priority": "medium",
            "timeout_seconds": 300,
        }
        
        response = client.post("/api/v1/tasks/submit", json=request_data)
        
        assert response.status_code == 503  # Service Unavailable

    def test_memory_status_unavailable(self, client):
        """测试系统未启动时查询内存"""
        response = client.get("/api/v1/memory/status")
        
        assert response.status_code == 503

    def test_invalid_json_request(self, client):
        """测试无效JSON请求"""
        response = client.post(
            "/api/v1/tasks/submit",
            content="invalid json",
            headers={"content-type": "application/json"},
        )
        
        assert response.status_code == 422


class TestCLIPresentation:
    """命令行接口测试"""

    def test_cli_import(self):
        """测试CLI模块可以正确导入"""
        try:
            from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
                cli,
            )
            assert cli is not None
        except Exception as e:
            pytest.fail(f"CLI导入失败: {e}")

    def test_cli_commands_exist(self):
        """测试CLI命令存在"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
            cli,
        )
        
        # 检查主要命令组
        command_names = [cmd.name for cmd in cli.commands.values()]
        
        assert "system" in command_names
        assert "tasks" in command_names
        assert "evolution" in command_names
        assert "memory" in command_names

    def test_cli_system_commands(self):
        """测试system命令组"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
            cli,
        )
        
        system_group = cli.commands["system"]
        system_command_names = [cmd.name for cmd in system_group.commands.values()]
        
        assert "start" in system_command_names
        assert "stop" in system_command_names
        assert "status" in system_command_names

    def test_cli_tasks_commands(self):
        """测试tasks命令组"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
            cli,
        )
        
        tasks_group = cli.commands["tasks"]
        tasks_command_names = [cmd.name for cmd in tasks_group.commands.values()]
        
        assert "submit" in tasks_command_names
        assert "list" in tasks_command_names
        assert "status" in tasks_command_names

    def test_cli_evolution_commands(self):
        """测试evolution命令组"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
            cli,
        )
        
        evolution_group = cli.commands["evolution"]
        evolution_command_names = [cmd.name for cmd in evolution_group.commands.values()]
        
        assert "info" in evolution_command_names
        assert "recommend" in evolution_command_names
        assert "optimize" in evolution_command_names

    def test_cli_memory_commands(self):
        """测试memory命令组"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.command_line_interface_presentation import (
            cli,
        )
        
        memory_group = cli.commands["memory"]
        memory_command_names = [cmd.name for cmd in memory_group.commands.values()]
        
        assert "status" in memory_command_names
        assert "cleanup" in memory_command_names


class TestPydanticModels:
    """测试Pydantic数据模型"""

    def test_task_submit_request_model(self):
        """测试任务提交请求模型"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation import (
            TaskSubmitRequest,
        )
        
        request = TaskSubmitRequest(
            content={"type": "test", "data": "value"},
            priority="high",
            timeout_seconds=600,
        )
        
        assert request.content["type"] == "test"
        assert request.priority == "high"
        assert request.timeout_seconds == 600

    def test_task_submit_response_model(self):
        """测试任务提交响应模型"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation import (
            TaskSubmitResponse,
        )
        
        response = TaskSubmitResponse(
            task_id="task-123456",
            status="submitted",
            message="任务提交成功",
        )
        
        assert response.task_id == "task-123456"
        assert response.status == "submitted"
        assert response.message == "任务提交成功"

    def test_system_status_response_model(self):
        """测试系统状态响应模型"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation import (
            SystemStatusResponse,
        )
        
        response = SystemStatusResponse(
            timestamp=datetime.utcnow().isoformat(),
            system_state="running",
            evolution_stage="learning",
            uptime_seconds=1234.5,
            health_status=True,
        )
        
        assert response.system_state == "running"
        assert response.evolution_stage == "learning"
        assert response.uptime_seconds == 1234.5

    def test_memory_status_response_model(self):
        """测试内存状态响应模型"""
        from src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation import (
            MemoryStatusResponse,
        )
        
        response = MemoryStatusResponse(
            total_mb=1024.0,
            used_mb=512.0,
            free_mb=512.0,
            used_percent=50.0,
            temperature={
                "hot_mb": 128.0,
                "warm_mb": 200.0,
                "cold_mb": 100.0,
                "frozen_mb": 84.0,
            },
        )
        
        assert response.total_mb == 1024.0
        assert response.used_mb == 512.0
        assert response.used_percent == 50.0
        assert response.temperature["hot_mb"] == 128.0


class TestAPIErrorHandling:
    """测试API错误处理"""

    def test_404_not_found(self, client):
        """测试404错误"""
        response = client.get("/api/v1/nonexistent/endpoint")
        
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """测试方法不允许"""
        response = client.put("/health")
        
        assert response.status_code == 405
