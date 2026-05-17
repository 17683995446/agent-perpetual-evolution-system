# Agent Perpetual System - API 参考文档

## 📚 文档概览

- [系统管理 API](#系统管理-api)
- [任务管理 API](#任务管理-api)
- [进化引擎 API](#进化引擎-api)
- [内存管理 API](#内存管理-api)
- [健康检查 API](#健康检查-api)

---

## 基础信息

**Base URL**: `http://localhost:8000`

**API Version**: v1

**Content-Type**: `application/json`

---

## 系统管理 API

### 启动系统

启动 Agent Perpetual System。

**端点**: `POST /api/v1/system/start`

**请求体**: 无

**响应示例**:
```json
{
  "task_id": "system-started",
  "status": "success",
  "message": "系统启动成功"
}
```

**cURL 示例**:
```bash
curl -X POST http://localhost:8000/api/v1/system/start
```

---

### 停止系统

停止 Agent Perpetual System。

**端点**: `POST /api/v1/system/stop`

**请求体**: 无

**响应示例**:
```json
{
  "task_id": "system-stopped",
  "status": "success",
  "message": "系统停止成功"
}
```

---

### 获取系统状态

获取当前系统状态。

**端点**: `GET /api/v1/system/status`

**响应示例**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "system_state": "running",
  "evolution_stage": "learning",
  "uptime_seconds": 3600.5,
  "health_status": true
}
```

**cURL 示例**:
```bash
curl http://localhost:8000/api/v1/system/status
```

---

## 任务管理 API

### 提交任务

提交新的任务到系统。

**端点**: `POST /api/v1/tasks/submit`

**请求体**:
```json
{
  "content": {
    "type": "analysis",
    "data": "sample_data"
  },
  "priority": "high",
  "timeout_seconds": 300,
  "execution_context": {
    "source": "api"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | object | ✅ | 任务内容 |
| `priority` | string | ❌ | 优先级 (low/medium/high/highest)，默认 medium |
| `timeout_seconds` | integer | ❌ | 超时时间（秒），默认 300 |
| `execution_context` | object | ❌ | 执行上下文 |

**响应示例**:
```json
{
  "task_id": "task-20240115-103000-abc123",
  "status": "submitted",
  "message": "任务提交成功"
}
```

**cURL 示例**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "content": {"type": "analysis", "data": "sample"},
    "priority": "high"
  }'
```

---

### 获取任务信息

根据任务ID获取任务详情。

**端点**: `GET /api/v1/tasks/{task_id}`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务标识符 |

**响应示例**:
```json
{
  "task_id": "task-20240115-103000-abc123",
  "content": {
    "type": "analysis",
    "data": "sample_data"
  },
  "status": "completed",
  "priority": "high",
  "created_at": "2024-01-15T10:30:00",
  "started_at": "2024-01-15T10:30:05",
  "completed_at": "2024-01-15T10:30:15",
  "result": {
    "success": true,
    "output": "analysis_complete"
  },
  "error_message": null
}
```

---

### 列出任务

获取任务列表和统计信息。

**端点**: `GET /api/v1/tasks`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status_filter` | string | ❌ | 按状态过滤 |
| `limit` | integer | ❌ | 返回数量，默认 20 |

**响应示例**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "stats": {
    "total_tasks": 150,
    "pending_tasks": 5,
    "running_tasks": 2,
    "completed_tasks": 140,
    "failed_tasks": 3
  },
  "limit": 20,
  "status_filter": null
}
```

---

## 进化引擎 API

### 获取进化仪表盘

获取进化引擎的完整仪表盘数据。

**端点**: `GET /api/v1/evolution/dashboard`

**响应示例**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "stage": "learning",
  "memory": {
    "used_percent": 45.5,
    "total_bytes": 1073741824,
    "used_bytes": 488642048,
    "optimized_bytes": 67108864,
    "temperature_breakdown": {
      "hot": 134217728,
      "warm": 209715200,
      "cold": 104857600,
      "frozen": 29360128
    }
  },
  "patterns": {
    "total": 42,
    "success": 30,
    "failure": 5,
    "optimization": 7,
    "avg_confidence": 0.78
  },
  "evolution": {
    "iterations_completed": 150,
    "total_optimizations": 25,
    "uptime_seconds": 7200.5,
    "avg_performance_improvement": 8.5
  }
}
```

---

### 获取智能建议

基于输入数据获取优化建议。

**端点**: `POST /api/v1/evolution/recommend`

**请求体**:
```json
{
  "input_data": {
    "task_type": "analysis",
    "data_size": "large"
  },
  "top_k": 5
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `input_data` | object | ✅ | 输入数据 |
| `top_k` | integer | ❌ | 返回建议数量，默认 5 |

**响应示例**:
```json
{
  "recommendations": [
    {
      "pattern_id": "pattern-abc123",
      "pattern_type": "best_practice",
      "recommendation_text": "使用类似配置会获得更好的性能",
      "confidence": 0.85,
      "applicable_features": ["task_type", "data_size"]
    }
  ]
}
```

---

### 强制优化

触发立即优化。

**端点**: `POST /api/v1/evolution/optimize`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `strategy_name` | string | ❌ | 策略名称，不指定则优化所有 |

**响应示例**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "strategy_name": "task_optimization",
  "result": "optimization_triggered"
}
```

---

## 内存管理 API

### 获取内存状态

获取当前内存使用状态。

**端点**: `GET /api/v1/memory/status`

**响应示例**:
```json
{
  "total_mb": 1024.0,
  "used_mb": 456.5,
  "free_mb": 567.5,
  "used_percent": 44.5,
  "temperature": {
    "hot_mb": 128.0,
    "warm_mb": 200.0,
    "cold_mb": 100.0,
    "frozen_mb": 28.5
  }
}
```

---

### 强制内存清理

触发立即内存清理。

**端点**: `POST /api/v1/memory/cleanup`

**响应示例**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "result": {
    "policy": "aggressive",
    "timestamp": "2024-01-15T10:30:00",
    "entries_removed": 15,
    "bytes_freed": 33554432
  }
}
```

---

## 健康检查 API

### 健康检查

获取系统健康状态。

**端点**: `GET /health`

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "2.0.0"
}
```

---

### 就绪检查

检查系统是否就绪。

**端点**: `GET /ready`

**响应示例**:
```json
{
  "ready": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## WebSocket API

### 仪表盘实时更新

获取实时仪表盘数据流。

**端点**: `WS /api/v1/ws/dashboard`

**使用示例**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Dashboard update:', data);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

---

## 错误响应

### 错误格式

所有 API 错误遵循统一格式：

```json
{
  "detail": "错误详细描述"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 错误的请求 |
| 404 | 资源未找到 |
| 422 | 请求验证失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 速率限制

暂无速率限制，但请合理使用 API。

---

## 版本信息

**当前版本**: 2.0.0

**API 版本**: v1

**最后更新**: 2024-01-15
