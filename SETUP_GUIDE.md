# Agent永续自进化系统 - 超简单配置指南

## 🚀 一句话总结

**只需要1个参数就能运行！**

---

## 📊 新旧配置对比

### 旧配置方式 (太复杂！)

| 配置项 | 是否必需 | 说明 |
|--------|---------|------|
| SILICONFLOW_API_KEY | ✅ 是 | API密钥 |
| OPENAI_API_KEY | ❌ 否 | 其他API |
| ANTHROPIC_API_KEY | ❌ 否 | 其他API |
| DB_HOST | ✅ 是 | 数据库地址 |
| DB_PORT | ✅ 是 | 数据库端口 |
| DB_USERNAME | ✅ 是 | 数据库用户名 |
| DB_PASSWORD | ✅ 是 | 数据库密码 |
| DB_NAME | ✅ 是 | 数据库名称 |
| LOG_LEVEL | ❌ 否 | 日志级别 |
| LOG_FORMAT | ❌ 否 | 日志格式 |
| LOG_DIR | ❌ 否 | 日志目录 |

**共需要 5+ 个必需配置项！** 太复杂了！

---

### 新配置方式 (极简单！)

| 配置项 | 是否必需 | 说明 |
|--------|---------|------|
| SILICONFLOW_API_KEY | ✅ 是 | **唯一**需要的配置 |
| **其他所有** | ❌ 否 | 都有默认值！ |

**只需要1个配置项！** 超简单！

---

## 📝 3种快速配置方式

### 方式1: 一键配置 (推荐！)

```bash
python quick_setup.py
```

按提示输入API密钥，30秒搞定！

---

### 方式2: 配置文件 (简单)

```bash
# 复制模板
cp config.example.json config.json

# 编辑配置
nano config.json
```

填入你的API密钥：
```json
{
  "siliconflow_api_key": "sk-你的密钥"
}
```

就这么简单！

---

### 方式3: 环境变量 (快速)

```bash
# 临时设置
export SILICONFLOW_API_KEY=sk-你的密钥

# 永久设置 (Linux/Mac)
echo 'export SILICONFLOW_API_KEY=sk-你的密钥' >> ~/.bashrc
source ~/.bashrc

# Windows
setx SILICONFLOW_API_KEY sk-你的密钥
```

---

## 📁 配置文件说明

### config.json (最简版)

```json
{
  "siliconflow_api_key": "sk-你的密钥"
}
```

就这么简单！不需要其他配置！

---

### config.json (完整版，可选)

```json
{
  "siliconflow_api_key": "sk-你的密钥",
  
  "optional_settings": {
    "api_base_url": "https://api.siliconflow.cn/v1",
    "api_model": "Qwen/Qwen2.5-7B-Instruct",
    "api_timeout": 60,
    
    "cache_enabled": true,
    "cache_dir": "./cache",
    "cache_ttl": 3600,
    
    "log_level": "INFO",
    "log_file": "./logs/agent.log",
    
    "max_workers": 4,
    "batch_size": 10
  }
}
```

**注意：optional_settings 全部可选，不需要的话直接删掉！**

---

## 🔧 在代码中使用

### 超简单！3行代码搞定！

```python
import simple_config

# 获取配置
config = simple_config.get_config()

# 使用API密钥
api_key = config.get_api_key()

# 检查配置
if config.is_valid():
    print("✅ 配置就绪！")
else:
    print("❌ 需要配置")
    config.help()
```

---

### 或者更简单！1行代码！

```python
import simple_config

api_key = simple_config.get_api_key()
```

---

## 🎯 快速测试配置

```bash
# 测试配置是否正常
python simple_usage_example.py

# 查看配置状态
python simple_usage_example.py status

# 快速配置
python simple_usage_example.py setup
```

---

## 📊 配置优先级

系统会按以下优先级查找配置：

1. **环境变量** (最高优先级)
2. **当前目录的 config.json**
3. **当前目录的 agent_config.json**
4. **当前目录的 settings.json**
5. **用户主目录的 ~/.agent_config.json**

---

## 🤔 常见问题

### Q: 需要数据库吗？
**不需要！** 默认使用内存缓存，不用配置数据库。

### Q: 需要设置其他参数吗？
**不需要！** 所有参数都有默认值，直接使用就行。

### Q: 可以混用多种配置方式吗？
**可以！** 比如既有环境变量，又有配置文件。环境变量优先级更高。

### Q: 配置存在哪里？
- 配置文件: `./config.json` (可以移到项目根目录)
- 或用户主目录: `~/.agent_config.json`
- 或环境变量

### Q: 如何查看当前配置状态？
```bash
python simple_usage_example.py
```

或：
```bash
python quick_setup.py --status
```

---

## 🎉 总结

| 对比项 | 旧版本 | 新版本 |
|--------|--------|--------|
| 必需配置项 | 5+个 | **1个** |
| 配置文件 | 复杂的dataclass | 简单的JSON |
| 学习成本 | 高 | 极低 |
| 上手时间 | 10分钟 | **30秒** |

---

## 📌 下一步

1. **配置API密钥** (3种方式选1)
2. **运行示例** `python simple_usage_example.py`
3. **开始使用**！

---

**有任何问题？运行 `python simple_usage_example.py` 查看帮助！** 🎉

