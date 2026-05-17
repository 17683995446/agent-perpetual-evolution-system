# Agent Perpetual System - 开发者指南

## 📋 目录

- [项目结构](#项目结构)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [模块开发](#模块开发)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [贡献指南](#贡献指南)

---

## 项目结构

```
agent-perpetual/
├── src/
│   └── agent_perpetual_system_complete/
│       └── layer_1_interface_presentation/      # 接口层 (5个单词)
│           ├── command_line_interface_presentation.py
│           └── web_api_interface_presentation.py
│
│       └── layer_2_orchestration_coordination/  # 编排层 (4个单词)
│           ├── task_execution_orchestrator.py
│           └── system_orchestration_controller.py
│
│       └── layer_3_business_service/            # 业务服务层 (3个单词)
│           ├── task_management_service_provider.py
│           ├── memory_cleanup_service_provider.py
│           ├── strategy_optimization_service_provider.py
│           ├── knowledge_learning_service_provider.py
│           ├── evolution_engine_controller.py
│           ├── prometheus_metrics_collector.py
│           └── performance_monitor_service.py
│
│       └── layer_4_domain_model/                # 领域模型层 (2个单词)
│           └── task_domain_entity_definition.py
│
│       └── layer_5_data_access/                # 数据访问层 (2个单词)
│           └── task_data_repository_accessor.py
│
│       └── layer_6_infrastructure_abstraction/   # 基础设施层 (3个单词)
│           ├── configuration_settings_abstraction.py
│           └── structured_logging_abstraction.py
│
│       └── layer_7_foundation_utility/          # 基础工具层 (2个单词)
│           ├── unique_identifier_generator.py
│           ├── date_time_utility_helper.py
│           ├── string_manipulation_utility.py
│           ├── collection_operation_utility.py
│           └── json_serialization_deserialization.py
│
├── layer_8_testing_verification/                # 测试验证层
│   ├── unit_testing_verification/
│   ├── integration_testing_verification/
│   └── end_to_end_testing_verification/
│
├── config/                                      # 配置文件
├── docs/                                        # 文档
├── .github/workflows/                          # CI/CD
└── docker-compose.yaml                          # Docker 配置
```

---

## 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/your-org/agent-perpetual.git
cd agent-perpetual
```

### 2. 创建虚拟环境

```bash
# 使用 pyenv (推荐)
pyenv install 3.11.6
pyenv virtualenv 3.11.6 agent-perpetual
pyenv local agent-perpetual

# 或者使用 venv
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装项目（开发模式）
pip install -e ".[dev]"

# 或者只安装运行时依赖
pip install -e .
```

### 4. 设置 Pre-commit Hooks

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 git hooks
pre-commit install

# 手动运行
pre-commit run --all-files
```

### 5. 运行测试

```bash
# 运行所有测试
pytest -v

# 运行带覆盖率
pytest --cov=src/agent_perpetual_system_complete --cov-report=html

# 运行特定测试
pytest layer_8_testing_verification/unit_testing_verification/test_task_execution_orchestrator_test.py -v
```

---

## 代码规范

### 文件命名规范

**重要**：所有业务模块文件必须使用 **≥4个单词** 的文件名。

✅ 正确示例：
```python
# 5个单词
task_execution_orchestrator.py
configuration_settings_abstraction.py

# 4个单词
system_orchestration_controller.py
structured_logging_abstraction.py

# 6个单词
memory_cleanup_service_provider.py
strategy_optimization_service_provider.py
```

❌ 错误示例：
```python
# 只有1-3个单词
orchestrator.py
task_service.py
```

### 导入规范

```python
# 标准库
import asyncio
import json
from typing import Dict, Any, Optional

# 第三方库
from fastapi import FastAPI
from pydantic import BaseModel

# 项目内部（使用相对导入）
from ..layer_3_business_service.task_management_service_provider import (
    TaskManagementServiceProvider,
)
```

### 类和函数命名

```python
# 类名：PascalCase
class TaskExecutionOrchestrator:
class SystemOrchestrationController:

# 函数名：snake_case
async def submit_task_with_dependencies():
def get_execution_statistics():

# 常量：SCREAMING_SNAKE_CASE
MAX_CONCURRENT_TASKS = 100
DEFAULT_TIMEOUT_SECONDS = 300
```

### 文档字符串

```python
class TaskExecutionOrchestrator:
    """
    任务执行编排器（TaskExecutionOrchestrator）
    
    核心职责：
    1. 管理任务的并发执行
    2. 解析和处理任务依赖关系
    3. 基于优先级调度任务
    4. 强制执行超时控制
    5. 收集和报告执行统计
    
    Attributes:
        config: 执行配置
        service_provider: 任务管理服务提供者
    """
    
    async def initialize(self) -> None:
        """
        初始化编排器
        
        执行必要的初始化操作，包括：
        - 创建信号量
        - 设置运行状态
        - 记录启动时间
        
        Returns:
            None
        """
        pass
```

---

## 模块开发

### 1. 创建新的业务服务

```python
# src/agent_perpetual_system_complete/layer_3_business_service/
# my_custom_service_provider.py  (3个单词，需要改！)

# ✅ 正确：使用4个以上单词
# my_custom_service_provider.py (4个单词)
# my_custom_business_service_provider.py (5个单词)

from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)


@dataclass
class MyServiceConfiguration:
    """我的服务配置"""
    service_name: str
    enable_feature_x: bool = True
    timeout_seconds: int = 60


class MyCustomServiceProvider:
    """
    我的自定义服务提供者（MyCustomServiceProvider）
    
    核心职责：
    1. 提供自定义服务功能
    2. 管理服务生命周期
    3. 处理服务异常
    """
    
    def __init__(self, config: Optional[MyServiceConfiguration] = None):
        self.logger = get_structured_logger(__name__)
        self.config = config or MyServiceConfiguration(service_name="default")
        
    async def initialize(self) -> None:
        """初始化服务"""
        self.logger.info(
            "initializing_my_custom_service",
            service_name=self.config.service_name,
        )
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据"""
        self.logger.info("processing_data", data=data)
        return {"status": "success", "data": data}
```

### 2. 创建新的领域实体

```python
# src/agent_perpetual_system_complete/layer_4_domain_model/
# my_custom_entity_definition.py

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class MyCustomDomainEntity(Base):
    """我的自定义领域实体（MyCustomDomainEntity）"""
    
    __tablename__ = "my_custom_entities"
    
    entity_id = Column(String(36), primary_key=True)
    entity_name = Column(String(255), nullable=False)
    entity_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<MyCustomDomainEntity(id={self.entity_id}, name={self.entity_name})>"
```

### 3. 添加 API 端点

```python
# 在 web_api_interface_presentation.py 中添加

class MyCustomRequest(BaseModel):
    """我的自定义请求"""
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class MyCustomResponse(BaseModel):
    """我的自定义响应"""
    status: str
    result: Dict[str, Any]
    timestamp: str


@app.post("/api/v1/my-custom/endpoint", response_model=MyCustomResponse, tags=["自定义"])
async def my_custom_endpoint(request: MyCustomRequest):
    """
    我的自定义端点
    
    详细的端点描述...
    
    Args:
        request: 请求数据
        
    Returns:
        响应数据
    """
    logger.info("processing_custom_request", data=request.data)
    
    return MyCustomResponse(
        status="success",
        result={"processed": request.data},
        timestamp=datetime.utcnow().isoformat(),
    )
```

---

## 测试指南

### 1. 单元测试结构

```python
# layer_8_testing_verification/unit_testing_verification/
# test_my_custom_service_test.py

import pytest
import pytest_asyncio
from typing import Dict, Any

from src.agent_perpetual_system_complete.layer_3_business_service.my_custom_service_provider import (
    MyCustomServiceProvider,
    MyServiceConfiguration,
)


class TestMyCustomServiceProvider:
    """我的自定义服务提供者测试"""
    
    @pytest_asyncio.fixture
    async def service(self):
        """测试夹具：服务实例"""
        config = MyServiceConfiguration(service_name="test")
        service = MyCustomServiceProvider(config)
        await service.initialize()
        yield service
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        assert service.config.service_name == "test"
    
    @pytest.mark.asyncio
    async def test_process_method(self, service):
        """测试处理方法"""
        test_data = {"key": "value"}
        result = await service.process(test_data)
        
        assert result["status"] == "success"
        assert result["data"] == test_data
```

### 2. 运行测试

```bash
# 运行所有单元测试
pytest layer_8_testing_verification/unit_testing_verification/ -v

# 运行带覆盖率
pytest layer_8_testing_verification/unit_testing_verification/ \
    --cov=src/agent_perpetual_system_complete \
    --cov-report=html \
    --cov-report=term-missing

# 运行特定测试类
pytest layer_8_testing_verification/unit_testing_verification/test_my_custom_service_test.py::TestMyCustomServiceProvider -v

# 运行特定测试方法
pytest layer_8_testing_verification/unit_testing_verification/test_my_custom_service_test.py::TestMyCustomServiceProvider::test_service_initialization -v
```

### 3. 测试覆盖率目标

| 模块类型 | 最低覆盖率 |
|---------|-----------|
| 业务服务层 | 90% |
| 数据访问层 | 85% |
| 接口层 | 80% |
| 工具层 | 90% |

---

## 调试技巧

### 1. 使用结构化日志

```python
from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)

logger = get_structured_logger(__name__)

# 结构化日志
logger.info(
    "task_submitted",
    task_id="task-123",
    priority="high",
    dependencies=["task-001", "task-002"],
)

# 调试模式
logger.debug(
    "processing_data",
    data_size=len(data),
    processing_time_ms=elapsed_ms,
)
```

### 2. 使用 pdb 调试

```python
import pdb

async def my_async_function():
    result = await some_async_operation()
    pdb.set_trace()  # 设置断点
    return result
```

### 3. 使用 pytest 调试

```bash
# 进入 pdb
pytest test_file.py --pdb

# 在第一个失败时停止
pytest test_file.py -x

# 显示局部变量
pytest test_file.py --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

---

## 贡献指南

### 1. Fork 和 Clone

```bash
# Fork 项目
git clone https://github.com/your-username/agent-perpetual.git
cd agent-perpetual
```

### 2. 创建分支

```bash
# 功能分支
git checkout -b feature/my-new-feature

# 修复分支
git checkout -b fix/issue-description

# 文档分支
git checkout -b docs/improve-documentation
```

### 3. 提交代码

```bash
# 暂存文件
git add .

# 提交（遵循 Conventional Commits）
git commit -m "feat(layer_3): 添加新的服务提供者

添加了一个新的服务提供者模块，用于处理特定业务场景。

- 实现服务初始化逻辑
- 添加服务处理方法
- 包含完整的单元测试

BREAKING CHANGE: 无"
```

### 4. 推送和创建 Pull Request

```bash
# 推送分支
git push origin feature/my-new-feature

# 创建 Pull Request
gh pr create \
  --title "feat: 添加新的服务提供者" \
  --body "## 描述
添加了一个新的服务提供者模块...

## 类型
- [ ] 功能
- [ ] 修复
- [ ] 文档

## 检查清单
- [ ] 代码遵循命名规范
- [ ] 添加了单元测试
- [ ] 所有测试通过
- [ ] 更新了文档"
```

### 5. 代码审查

所有 Pull Request 必须：
- ✅ 遵循代码规范
- ✅ 通过所有 CI 检查
- ✅ 包含测试覆盖
- ✅ 更新相关文档
- ✅ 至少一个审查者批准

---

## 支持

- 📧 邮箱: dev@agent-perpetual.io
- 💬 Slack: #dev-support
- 🐛 问题: GitHub Issues
