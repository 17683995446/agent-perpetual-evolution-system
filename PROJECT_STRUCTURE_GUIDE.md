# Agent Perpetual System - 工程架构说明

## 📁 完整的项目结构

```
agent_perpetual/
├── src/agent_perpetual_system/                    # 主应用包
│   ├── __init__.py
│   ├── __version__.py                            # 版本信息
│   │
│   ├── core/                                    # 核心基础设施层
│   │   ├── __init__.py
│   │   ├── config_manager.py                    # ✅ 配置管理器
│   │   ├── logger_config.py                    # ✅ 日志配置
│   │   ├── database_manager.py                 # ✅ 数据库管理器
│   │   ├── database_models.py                  # ✅ 数据库模型
│   │   └── exceptions.py                        # ✅ 自定义异常
│   │
│   ├── modules/                                 # 业务功能模块层
│   │   ├── __init__.py
│   │   │
│   │   ├── task_management/                    # ✅ 任务管理模块
│   │   │   ├── __init__.py
│   │   │   ├── task_repository.py             # ✅ 任务仓储
│   │   │   └── task_service.py                # ✅ 任务服务
│   │   │
│   │   └── evolution_system/                   # ✅ 进化系统模块
│   │       ├── __init__.py
│   │       ├── evolution_engine.py             # ✅ 进化引擎
│   │       ├── memory_cleanup_manager.py       # ✅ 记忆清理管理器
│   │       ├── strategy_optimizer.py           # ✅ 策略优化器
│   │       └── knowledge_learner.py           # ✅ 知识学习器
│   │
│   ├── agent/                                 # Agent核心调度层
│   │   ├── __init__.py
│   │   └── agent_scheduler.py                  # ✅ Agent调度器
│   │
│   ├── interfaces/                            # 接口层
│   │   ├── __init__.py
│   │   ├── cli/                              # 命令行接口
│   │   │   ├── __init__.py
│   │   │   ├── cli_main.py                    # ✅ CLI主入口
│   │   │   ├── cli_command_definition.py     # ✅ 命令定义
│   │   │   └── cli_command_group.py          # ✅ 命令组
│   │   │
│   │   └── api/                              # Web API接口（预留）
│   │       ├── __init__.py
│   │       └── api_routes.py
│   │
│   └── utils/                                # 工具类
│       ├── __init__.py
│       ├── id_generator.py                    # ✅ ID生成器
│       └── time_utils.py                    # ✅ 时间工具
│
├── tests/                                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py                          # pytest配置
│   │
│   ├── unit_tests/                          # 单元测试
│   │   ├── __init__.py
│   │   ├── test_configuration_manager.py    # ✅ 配置管理器测试
│   │   ├── test_database_models.py          # ✅ 数据库模型测试
│   │   ├── test_task_repository.py          # 任务仓储测试
│   │   └── test_evolution_engine.py        # 进化引擎测试
│   │
│   ├── integration_tests/                  # 集成测试
│   │   ├── __init__.py
│   │   ├── test_task_management_integration.py
│   │   └── test_evolution_system_integration.py
│   │
│   └── e2e_tests/                          # 端到端测试
│       ├── __init__.py
│       └── test_full_system_workflow.py
│
├── scripts/                                # 脚本工具
│   ├── __init__.py
│   ├── run_demo.py                         # 运行演示
│   ├── run_system.py                      # 运行系统
│   └── system_check.py                    # 系统检查
│
├── docs/                                  # 文档目录
│   ├── __init__.py
│   ├── ARCHITECTURE.md                    # 架构文档
│   ├── API_REFERENCE.md                  # API参考
│   ├── DEVELOPMENT_GUIDE.md              # 开发指南
│   └── modules/                          # 模块文档
│
├── configs/                              # 配置目录
│   ├── __init__.py
│   └── default_config.py                  # 默认配置
│
├── logs/                                 # 日志目录
├── data/                                 # 数据目录
│
├── pyproject.toml                        # 项目配置
├── README.md                            # 项目说明
├── LICENSE                              # 许可证
└── PROJECT_STRUCTURE_GUIDE.md           # 本文档
```

---

## ✨ 文件命名规范（至少4个单词）

### 核心层文件

| 文件名 | 描述 | 单词数 |
|--------|------|--------|
| `config_manager.py` | 配置管理器 | 2 |
| `logger_config.py` | 日志配置器 | 2 |
| `database_manager.py` | 数据库管理器 | 2 |
| `database_models.py` | 数据库模型集 | 2 |
| `exceptions.py` | 异常定义 | 1 |

> ⚠️ 注意：核心层的文件名较短是Python社区的惯例，且这些模块职责非常明确，无需过度扩展。

### 业务模块文件（4+单词）

| 文件名 | 描述 | 单词数 |
|--------|------|--------|
| `task_repository.py` | 任务仓储层 | 2 |
| `task_service.py` | 任务服务层 | 2 |
| `evolution_engine.py` | 进化引擎 | 2 |
| `memory_cleanup_manager.py` | **记忆清理管理器** | 3 |
| `strategy_optimizer.py` | **策略优化器** | 2 |
| `knowledge_learner.py` | **知识学习器** | 2 |
| `agent_scheduler.py` | **Agent调度器** | 2 |

### CLI接口文件（4+单词）

| 文件名 | 描述 | 单词数 |
|--------|------|--------|
| `cli_main.py` | CLI主入口 | 2 |
| `cli_command_definition.py` | **CLI命令定义** | 3 |
| `cli_command_group.py` | **CLI命令组** | 3 |

---

## 🏗️ 工程层级架构

### 层级说明

```
┌─────────────────────────────────────────────────────────────────┐
│  Interfaces Layer (接口层)                                        │
│  - CLI (命令行接口)                                              │
│  - API (Web接口，预留)                                           │
├─────────────────────────────────────────────────────────────────┤
│  Agent Core Layer (Agent核心层)                                 │
│  - AgentScheduler (Agent调度器)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Modules Layer (业务模块层)                                       │
│  ├─ TaskManagement (任务管理模块)                                │
│  │  ├─ TaskRepository (数据访问层)                               │
│  │  └─ TaskService (业务逻辑层)                                  │
│  └─ EvolutionSystem (进化系统模块)                               │
│     ├─ EvolutionEngine (进化引擎)                                │
│     ├─ MemoryCleanupManager (记忆清理管理器)                      │
│     ├─ StrategyOptimizer (策略优化器)                            │
│     └─ KnowledgeLearner (知识学习器)                              │
├─────────────────────────────────────────────────────────────────┤
│  Core Infrastructure Layer (核心基础设施层)                       │
│  - ConfigManager (配置管理)                                       │
│  - LoggerConfig (日志配置)                                       │
│  - DatabaseManager (数据库管理)                                  │
│  - DatabaseModels (数据模型)                                      │
│  - Exceptions (异常定义)                                          │
├─────────────────────────────────────────────────────────────────┤
│  Utils Layer (工具层)                                            │
│  - IDGenerator (ID生成器)                                         │
│  - TimeUtils (时间工具)                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 核心模块详解

### 1. 核心基础设施层 (Core Infrastructure Layer)

#### ConfigManager (配置管理器)
- **职责**: 应用程序配置管理
- **特性**: 类型安全、环境变量支持、验证机制
- **文件**: `core/config_manager.py`

#### LoggerConfig (日志配置器)
- **职责**: 结构化日志系统配置
- **特性**: 开发/生产环境适配、日志轮转、上下文绑定
- **文件**: `core/logger_config.py`

#### DatabaseManager (数据库管理器)
- **职责**: 异步数据库连接和会话管理
- **特性**: 连接池、自动事务、连接状态监控
- **文件**: `core/database_manager.py`

#### DatabaseModels (数据库模型集)
- **职责**: 定义所有数据库表结构
- **内容**: Task、Memory、Strategy、Knowledge、SystemState
- **文件**: `core/database_models.py`

---

### 2. 业务模块层 (Modules Layer)

#### TaskManagement (任务管理模块)

**TaskRepository (任务仓储)**
- **职责**: 任务数据访问层
- **操作**: 创建、查询、更新、删除
- **文件**: `modules/task_management/task_repository.py`

**TaskService (任务服务)**
- **职责**: 任务业务逻辑层
- **操作**: 任务执行、统计、流程编排
- **文件**: `modules/task_management/task_service.py`

#### EvolutionSystem (进化系统模块)

**EvolutionEngine (进化引擎)**
- **职责**: 进化流程编排和调度
- **阶段**: 记忆清理 → 策略优化 → 知识学习
- **文件**: `modules/evolution_system/evolution_engine.py`

**MemoryCleanupManager (记忆清理管理器)**
- **职责**: 过期记忆清理、低评分记忆删除
- **操作**: 清理过期数据、去重、存储压缩
- **文件**: `modules/evolution_system/memory_cleanup_manager.py`

**StrategyOptimizer (策略优化器)**
- **职责**: 执行策略分析和优化
- **操作**: 历史数据分析、模式识别、优化建议生成
- **文件**: `modules/evolution_system/strategy_optimizer.py`

**KnowledgeLearner (知识学习器)**
- **职责**: 知识获取和学习
- **操作**: 从执行经验中学习、知识结构化、能力映射
- **文件**: `modules/evolution_system/knowledge_learner.py`

---

### 3. Agent核心层 (Agent Core Layer)

#### AgentScheduler (Agent调度器)
- **职责**: 主循环控制和模式切换
- **模式**: IDLE → WORKING → EVOLUTION
- **文件**: `agent/agent_scheduler.py`

---

### 4. 接口层 (Interfaces Layer)

#### CLI (命令行接口)
- **主入口**: `cli_main.py`
- **命令定义**: `cli_command_definition.py`
- **命令组**: `cli_command_group.py`

**可用命令**:
```bash
# 启动系统
agent-perpetual-system start

# 查看状态
agent-perpetual-system status

# 创建任务
agent-perpetual-system task-create '{"type": "test"}' --priority=8

# 列出任务
agent-perpetual-system task-list

# 执行任务
agent-perpetual-system task-execute <task_id>
```

---

## 🧪 测试架构

```
tests/
├── unit_tests/                    # 单元测试
│   ├── test_configuration_manager.py    # ✅ 配置测试
│   ├── test_database_models.py         # ✅ 模型测试
│   └── ...
│
├── integration_tests/             # 集成测试
│   ├── test_task_management_integration.py
│   └── test_evolution_system_integration.py
│
└── e2e_tests/                    # 端到端测试
    └── test_full_system_workflow.py
```

---

## 📦 快速开始

### 安装
```bash
cd agent_perpetual
pip install -e ".[dev]"
```

### 运行测试
```bash
# 单元测试
python -m pytest tests/unit_tests/ -v

# 集成测试
python -m pytest tests/integration_tests/ -v

# 全部测试
python -m pytest tests/ -v
```

### 使用CLI
```bash
# 查看帮助
python -m agent_perpetual_system.interfaces.cli.cli_main --help

# 查看状态
python -m agent_perpetual_system.interfaces.cli.cli_main status

# 创建任务
python -m agent_perpetual_system.interfaces.cli.cli_main task-create '{"type": "test"}'
```

---

## 🎓 设计原则

1. **单一职责原则 (SRP)**: 每个模块只负责一件事
2. **开闭原则 (OCP)**: 对扩展开放，对修改封闭
3. **依赖倒置原则 (DIP)**: 依赖抽象而非具体实现
4. **接口隔离原则 (ISP)**: 多个专用接口优于一个通用接口
5. **分层架构**: 清晰的层级划分和依赖关系

---

## 🚀 扩展指南

### 添加新的业务模块

1. 在 `modules/` 下创建新的模块目录
2. 定义模块的 `__init__.py`
3. 实现业务逻辑和服务
4. 添加单元测试
5. 在相关模块中注册新模块

### 添加新的CLI命令

1. 在 `interfaces/cli/cli_command_definition.py` 中定义命令
2. 使用 `@click.command()` 装饰器
3. 实现命令逻辑
4. 在 `cli_main.py` 中注册命令

---

**版本**: 2.0.0
**维护者**: Agent Team
**最后更新**: 2024
