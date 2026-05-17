# Agent Perpetual System - 最佳实践指南

## 📋 目录

- [架构最佳实践](#架构最佳实践)
- [性能优化](#性能优化)
- [安全加固](#安全加固)
- [监控和日志](#监控和日志)
- [错误处理](#错误处理)
- [配置管理](#配置管理)

---

## 架构最佳实践

### 1. 遵循分层架构

```
┌─────────────────────────────────────────┐
│         Layer 1: Interface              │ ← 只处理用户交互
├─────────────────────────────────────────┤
│         Layer 2: Orchestration          │ ← 协调和编排
├─────────────────────────────────────────┤
│         Layer 3: Business Service        │ ← 业务逻辑
├─────────────────────────────────────────┤
│         Layer 4: Domain Model           │ ← 领域实体
├─────────────────────────────────────────┤
│         Layer 5: Data Access            │ ← 数据访问
├─────────────────────────────────────────┤
│         Layer 6: Infrastructure          │ ← 基础设施
├─────────────────────────────────────────┤
│         Layer 7: Foundation Utility     │ ← 基础工具
└─────────────────────────────────────────┘
```

**规则**：
- ✅ 每层只依赖下一层
- ✅ 禁止跨层直接调用
- ✅ 使用依赖注入
- ✅ 接口抽象依赖

### 2. 文件命名规范

**重要**：所有业务模块必须使用 **≥4个单词** 的文件名。

```python
# ✅ 正确示例
task_execution_orchestrator.py       # 4个单词
system_orchestration_controller.py   # 4个单词
configuration_settings_abstraction.py # 5个单词
memory_cleanup_service_provider.py   # 5个单词

# ❌ 错误示例
orchestrator.py                      # 1个单词
task_service.py                      # 2个单词
service.py                           # 1个单词
```

### 3. 使用异步编程

```python
# ✅ 正确：使用 async/await
async def execute_task(task_id: str):
    result = await task_repository.get_task(task_id)
    return result

# ❌ 错误：混合使用
def execute_task(task_id: str):
    result = asyncio.run(task_repository.get_task(task_id))  # 不要这样
```

---

## 性能优化

### 1. 数据库优化

```python
# ✅ 使用批量操作
async def batch_insert_tasks(tasks: List[Task]):
    async with async_session.begin():
        session.add_all(tasks)

# ✅ 使用索引
class Task(Base):
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_priority_created', 'priority', 'created_at'),
    )

# ✅ 使用分页
async def get_tasks_paginated(page: int, page_size: int):
    offset = (page - 1) * page_size
    return await session.execute(
        select(Task).offset(offset).limit(page_size)
    )
```

### 2. 内存优化

```python
# ✅ 使用流式处理
async def process_large_file(filepath: str):
    async with aiofiles.open(filepath, 'rb') as f:
        while chunk := await f.read(1024 * 1024):  # 1MB chunks
            await process_chunk(chunk)

# ✅ 及时清理
async def cleanup_data():
    await memory_cleanup_service.force_cleanup()
```

### 3. 并发优化

```python
# ✅ 使用信号量限制并发
semaphore = asyncio.Semaphore(max_concurrent)

async def bounded_execution(task):
    async with semaphore:
        return await task.execute()

# ✅ 使用 asyncio.gather 并行执行
results = await asyncio.gather(
    *[execute_task(t) for t in tasks],
    return_exceptions=True
)
```

---

## 安全加固

### 1. 输入验证

```python
from pydantic import BaseModel, Field, validator

class TaskSubmitRequest(BaseModel):
    content: Dict[str, Any] = Field(..., description="任务内容")
    priority: str = Field(..., regex="^(low|medium|high|highest)$")
    timeout_seconds: int = Field(300, ge=1, le=86400)
    
    @validator('content')
    def validate_content(cls, v):
        if not v:
            raise ValueError("内容不能为空")
        return v
```

### 2. 敏感信息处理

```python
# ✅ 使用环境变量
import os
API_KEY = os.getenv('API_KEY', '')

# ✅ 使用密钥管理服务
from cryptography.fernet import Fernet
cipher = Fernet(ENCRYPTION_KEY)

# ❌ 禁止硬编码
# API_KEY = "sk-1234567890abcdef"  # 禁止！
```

### 3. SQL 注入防护

```python
# ✅ 使用参数化查询
async def get_task_by_id(task_id: str):
    result = await session.execute(
        select(Task).where(Task.task_identifier == task_id)  # 参数化
    )

# ❌ 禁止字符串拼接
# query = f"SELECT * FROM tasks WHERE id = '{task_id}'"  # 禁止！
```

---

## 监控和日志

### 1. 结构化日志

```python
from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)

logger = get_structured_logger(__name__)

# ✅ 正确：结构化日志
logger.info(
    "task_submitted",
    task_id=task_id,
    priority=priority,
    user_id=user_id,
    request_id=request_id,
)

# ❌ 错误：字符串拼接
# logger.info(f"Task {task_id} submitted by {user_id}")  # 禁止！
```

### 2. 日志级别使用

```python
# DEBUG: 开发调试
logger.debug("processing_data", data=data)

# INFO: 正常运行信息
logger.info("task_completed", task_id=task_id)

# WARNING: 警告信息
logger.warning("high_memory_usage", usage_percent=85.0)

# ERROR: 错误信息
logger.error("task_failed", task_id=task_id, error=str(e))

# CRITICAL: 严重错误
logger.critical("system_unavailable", reason="database_connection_failed")
```

### 3. 性能指标收集

```python
from src.agent_perpetual_system_complete.layer_3_business_service.prometheus_metrics_collector import (
    PrometheusMetricsCollector,
)

metrics = PrometheusMetricsCollector()

# 记录请求
metrics.increment_http_request("GET", "/api/tasks", 200)

# 记录任务时长
metrics.observe_task_duration("success", duration_seconds=1.5)

# 记录错误
metrics.increment_error_count(error_type="validation_error")
```

---

## 错误处理

### 1. 使用自定义异常

```python
class AgentPerpetualError(Exception):
    """基础异常类"""
    pass

class TaskNotFoundError(AgentPerpetualError):
    """任务未找到"""
    pass

class TaskExecutionTimeoutError(AgentPerpetualError):
    """任务执行超时"""
    pass

class ValidationError(AgentPerpetualError):
    """验证错误"""
    pass
```

### 2. 统一的错误处理

```python
from fastapi import HTTPException

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "task_not_found",
            "message": str(exc),
            "task_id": exc.task_id,
        }
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": str(exc),
            "details": exc.details,
        }
    )
```

### 3. 使用重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def execute_with_retry(task_id: str):
    try:
        return await execute_task(task_id)
    except TransientError:
        raise  # tenacity 会自动重试
```

---

## 配置管理

### 1. 使用 Pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/agent_system.db"
    
    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"
    
    # 应用配置
    app_name: str = "Agent Perpetual System"
    log_level: str = "INFO"
    
    # 任务配置
    max_concurrent_tasks: int = 10
    default_timeout_seconds: int = 300
    
    # 安全配置
    secret_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 2. 环境特定配置

```python
# .env.development
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite+aiosqlite:///./dev.db

# .env.production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@prod-db:5432/agent_perpetual

# .env.testing
LOG_LEVEL=ERROR
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

### 3. 运行时配置更新

```python
# 动态更新配置（不重启服务）
async def update_config(key: str, value: Any):
    # 验证新值
    validated_value = validate_config_value(key, value)
    
    # 更新配置
    settings.__dict__[key] = validated_value
    
    # 通知相关组件
    await config_change_notifier.notify(key, validated_value)
```

---

## 部署最佳实践

### 1. Docker 优化

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install --user -e ".[dev]"

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
USER 1001
```

### 2. 健康检查

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. 资源限制

```yaml
resources:
  limits:
    cpus: '2.0'
    memory: 2Gi
  requests:
    cpus: '1.0'
    memory: 1Gi
```

---

## 测试最佳实践

### 1. 测试隔离

```python
@pytest_asyncio.fixture
async def clean_database():
    """每个测试前清理数据库"""
    await db.drop_all()
    await db.create_all()
    yield
    await db.drop_all()

@pytest.mark.asyncio
async def test_task_creation(clean_database):
    """测试任务创建"""
    task = await create_task(...)
    assert task.id is not None
```

### 2. Mock 外部依赖

```python
@pytest.fixture
def mock_external_api(mocker):
    """Mock 外部 API 调用"""
    return mocker.patch(
        'src.agent_perpetual_system_complete.services.external_api.call',
        return_value={"status": "success"}
    )

@pytest.mark.asyncio
async def test_with_mocked_api(mock_external_api):
    result = await service.process()
    assert result["status"] == "success"
```

### 3. 参数化测试

```python
@pytest.mark.parametrize("priority,expected_status", [
    ("low", TaskStatus.PENDING),
    ("medium", TaskStatus.PENDING),
    ("high", TaskStatus.READY),
    ("highest", TaskStatus.READY),
])
@pytest.mark.asyncio
async def test_task_priority(priority, expected_status):
    task = await create_task(priority=priority)
    assert task.status == expected_status
```

---

## 持续集成最佳实践

### 1. 自动化测试

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest layer_8_testing_verification/ \
      --cov=src/agent_perpetual_system_complete \
      --cov-fail-under=80 \
      --timeout=300
```

### 2. 代码质量检查

```yaml
- name: Code quality
  run: |
    ruff check .
    black --check .
    mypy src/agent_perpetual_system_complete
```

### 3. 安全扫描

```yaml
- name: Security scan
  run: |
    bandit -r src/
    safety check
```

---

## 总结

遵循这些最佳实践可以：

✅ **提高代码质量** - 统一的架构和命名规范  
✅ **提升性能** - 优化数据库、内存、并发  
✅ **增强安全** - 输入验证、敏感信息保护  
✅ **便于监控** - 结构化日志、指标收集  
✅ **简化调试** - 统一的错误处理  
✅ **加速开发** - 测试隔离、Mock 外部依赖  
✅ **保障质量** - 自动化 CI/CD 流水线

---

**最后更新**：2024-01-15
