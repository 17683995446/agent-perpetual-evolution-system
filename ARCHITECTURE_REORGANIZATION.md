# Agent Perpetual System - 工程架构重组计划

## 当前问题分析

### 1. 文件系统混乱
- 根目录包含多个演示和测试脚本
- 文件命名不够规范和完整
- 缺少明确的目录职责划分

### 2. 命名不够规范
- 短文件名如 `models.py`, `scheduler.py` 缺乏可读性
- 模块职责不够明确
- 缺乏统一的命名规范

### 3. 架构不够模块化
- 业务逻辑和基础设施混在一起
- 缺乏清晰的层次边界
- 模块间耦合度较高

---

## 目标架构设计

### 新的目录结构

```
agent_perpetual_system/
├── src/                                    # 源代码
│   └── agent_perpetual_system/             # 主应用包
│       ├── __init__.py                     # 包初始化
│       ├── __version__.py                  # 版本信息
│       │
│       ├── core/                           # 核心基础设施层
│       │   ├── __init__.py
│       │   ├── config_manager.py            # 配置管理（使用Pydantic）
│       │   ├── logger_config.py             # 日志配置（使用Structlog）
│       │   ├── database_manager.py          # 数据库管理（SQLAlchemy 2.0）
│       │   ├── database_models.py           # 数据库模型（ORM实体）
│       │   └── exceptions.py                # 自定义异常
│       │
│       ├── modules/                         # 业务功能模块层
│       │   ├── __init__.py
│       │   │
│       │   ├── task_management/             # 任务管理模块
│       │   │   ├── __init__.py
│       │   │   ├── task_service.py          # 任务服务（业务逻辑）
│       │   │   ├── task_repository.py       # 任务仓储（数据访问）
│       │   │   ├── task_executor.py         # 任务执行器
│       │   │   └── task_enums.py            # 任务相关枚举
│       │   │
│       │   └── evolution_system/            # 自主进化系统模块
│       │       ├── __init__.py
│       │       ├── evolution_engine.py      # 进化引擎主逻辑
│       │       ├── memory_manager.py        # 记忆管理器
│       │       ├── strategy_optimizer.py    # 策略优化器
│       │       ├── knowledge_learner.py    # 知识学习器
│       │       └── evolution_enums.py      # 进化阶段枚举
│       │
│       ├── agent/                           # Agent核心调度层
│       │   ├── __init__.py
│       │   ├── agent_scheduler.py           # Agent主调度器
│       │   ├── mode_manager.py              # 模式管理器
│       │   └── checkpoint_manager.py        # 断点管理器
│       │
│       ├── interfaces/                      # 接口层（CLI/API）
│       │   ├── __init__.py
│       │   ├── cli/                         # 命令行接口
│       │   │   ├── __init__.py
│       │   │   ├── cli_main.py              # CLI主入口
│       │   │   ├── cli_commands.py          # CLI命令定义
│       │   │   └── cli_formatters.py        # 输出格式化
│       │   │
│       │   └── api/                         # Web API接口（预留）
│       │       ├── __init__.py
│       │       ├── api_main.py
│       │       └── api_routes.py
│       │
│       └── utils/                           # 工具类
│           ├── __init__.py
│           ├── id_generator.py             # ID生成器
│           └── time_utils.py               # 时间工具
│
├── tests/                                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py                          # pytest配置
│   │
│   ├── unit_tests/                          # 单元测试
│   │   ├── __init__.py
│   │   ├── test_config_manager.py
│   │   ├── test_database_models.py
│   │   ├── test_task_service.py
│   │   ├── test_task_repository.py
│   │   └── test_evolution_engine.py
│   │
│   ├── integration_tests/                   # 集成测试
│   │   ├── __init__.py
│   │   ├── test_task_management_integration.py
│   │   └── test_evolution_system_integration.py
│   │
│   └── e2e_tests/                          # 端到端测试
│       ├── __init__.py
│       └── test_full_system_workflow.py
│
├── scripts/                                  # 脚本工具
│   ├── __init__.py
│   ├── run_demo.py                         # 运行演示
│   ├── run_system.py                       # 运行系统
│   └── system_check.py                     # 系统检查
│
├── docs/                                    # 文档目录
│   ├── __init__.py
│   ├── ARCHITECTURE.md                     # 架构文档
│   ├── API_REFERENCE.md                    # API参考
│   ├── DEVELOPMENT_GUIDE.md                 # 开发指南
│   ├── DEPLOYMENT_GUIDE.md                 # 部署指南
│   └── modules/                            # 模块文档
│       ├── TASK_MANAGEMENT.md
│       ├── EVOLUTION_SYSTEM.md
│       └── AGENT_CORE.md
│
├── configs/                                 # 配置文件目录
│   ├── __init__.py
│   ├── default_config.py                   # 默认配置
│   ├── development.yaml                     # 开发环境配置
│   ├── production.yaml                      # 生产环境配置
│   └── logging.yaml                        # 日志配置
│
├── logs/                                    # 日志输出目录
│   └── .gitkeep                            # 保持目录
│
├── data/                                    # 数据目录
│   ├── __init__.py
│   └── .gitkeep                            # 保持目录
│
├── pyproject.toml                          # 项目配置
├── setup.cfg                               # setup配置
├── README.md                               # 项目说明
├── LICENSE                                 # 许可证
├── CHANGELOG.md                            # 变更日志
├── COMPREHENSIVE_EVALUATION.md             # 综合评估报告
└── ARCHITECTURE_REORGANIZATION.md          # 本文档
```

---

## 命名规范

### 1. 文件命名规范

| 旧名称 | 新名称 | 说明 |
|--------|--------|------|
| `models.py` | `database_models.py` | 数据模型，明确职责 |
| `config.py` | `config_manager.py` | 配置管理 |
| `logging.py` | `logger_config.py` | 日志配置 |
| `database.py` | `database_manager.py` | 数据库管理 |
| `scheduler.py` | `agent_scheduler.py` | 调度器 |
| `task_service.py` | `task_service.py` | 任务服务 |
| `evolution_engine.py` | `evolution_engine.py` | 进化引擎 |
| `main.py` | `cli_main.py` | CLI主入口 |

### 2. 目录命名规范

| 旧名称 | 新名称 | 说明 |
|--------|--------|------|
| `core/` | `core/` | 核心基础设施 |
| `modules/` | `modules/` | 业务模块 |
| - | `task_management/` | 任务管理子模块 |
| - | `evolution_system/` | 进化系统子模块 |
| `agent/` | `agent/` | Agent核心 |
| `cli/` | `interfaces/cli/` | CLI接口 |
| - | `interfaces/api/` | API接口（预留） |
| `tests/` | `tests/` | 测试（细分为unit/integration/e2e） |
| - | `scripts/` | 脚本工具 |
| - | `docs/` | 文档 |
| - | `configs/` | 配置 |

---

## 实施计划

### Phase 1: 创建新目录结构
1. 创建所有必要的目录
2. 创建 `__init__.py` 文件
3. 创建新的模块文件框架

### Phase 2: 重命名和移动代码
1. 移动核心基础设施代码到新位置
2. 重构业务模块
3. 更新模块导入路径

### Phase 3: 更新测试
1. 移动测试文件到新位置
2. 更新测试导入路径
3. 添加新的测试用例

### Phase 4: 更新文档和脚本
1. 移动文档到 `docs/` 目录
2. 整理脚本到 `scripts/` 目录
3. 更新 README

---

## 预期收益

1. **更好的可维护性** - 清晰的模块边界，职责单一
2. **更高的可读性** - 完整的文件名，一目了然
3. **更低的耦合度** - 分层架构，依赖清晰
4. **更易扩展** - 模块化设计，便于添加新功能
5. **更易测试** - 清晰的测试分层结构
