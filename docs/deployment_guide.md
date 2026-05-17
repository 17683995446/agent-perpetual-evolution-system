# Agent Perpetual System - 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [Docker Compose 部署](#docker-compose-部署)
- [Kubernetes 部署](#kubernetes-部署)
- [云平台部署](#云平台部署)
- [生产环境配置](#生产环境配置)

---

## 快速开始

### 前置要求

- Python 3.10+
- Docker (可选)
- Redis (可选，用于生产环境)

### 本地安装

```bash
# 克隆项目
git clone https://github.com/your-org/agent-perpetual.git
cd agent-perpetual

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 启动 API 服务器
python -m uvicorn src.agent_perpetual_system_complete.layer_1_interface_presentation.web_api_interface_presentation:app --host 0.0.0.0 --port 8000

# 启动 CLI
agent-perpetual system status
```

### 验证安装

```bash
# 检查 API 健康状态
curl http://localhost:8000/health

# 使用 CLI
agent-perpetual system status
agent-perpetual tasks list
```

---

## Docker 部署

### 构建镜像

```bash
# 构建生产镜像
docker build -t agent-perpetual:latest .

# 构建多阶段镜像（更小）
docker build --target runtime -t agent-perpetual:runtime .
```

### 运行容器

```bash
# 运行基本容器
docker run -d \
  --name agent-perpetual \
  -p 8000:8000 \
  -p 8001:8001 \
  -e DATABASE_URL=sqlite+aiosqlite:///./data/agent_system.db \
  -v agent-data:/app/data \
  agent-perpetual:latest

# 查看日志
docker logs -f agent-perpetual

# 停止容器
docker stop agent-perpetual
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | sqlite+aiosqlite:///./data/agent_system.db | 数据库连接 |
| `REDIS_URL` | redis://localhost:6379/0 | Redis 连接 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `ENVIRONMENT` | production | 运行环境 |

---

## Docker Compose 部署

### 基本部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 访问服务

- **API**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 自定义配置

创建 `docker-compose.override.yml`:

```yaml
version: '3.9'

services:
  agent-perpetual:
    environment:
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=staging
    ports:
      - "9000:8000"  # 自定义端口
```

### 数据持久化

```bash
# 创建数据卷
docker volume create agent-perpetual-data

# 使用数据卷运行
docker-compose up -d
```

---

## Kubernetes 部署

### 前置要求

- Kubernetes 1.20+
- Helm 3.0+

### 使用 Helm 部署

```bash
# 添加 Helm 仓库
helm repo add agent-perpetual https://charts.agent-perpetual.io
helm repo update

# 搜索 Chart
helm search repo agent-perpetual

# 安装
helm install agent-perpetual agent-perpetual/agent-perpetual \
  --namespace agent-perpetual \
  --create-namespace \
  --values values.yaml
```

### values.yaml 示例

```yaml
replicaCount: 3

image:
  repository: agentperpetual/agent-perpetual
  tag: "2.0.0"
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  apiPort: 8000
  metricsPort: 8001

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: agent-perpetual.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: agent-perpetual-tls
      hosts:
        - agent-perpetual.example.com

prometheus:
  enabled: true
  scrapeInterval: 10s

redis:
  enabled: true
  architecture: replication
```

### kubectl 部署

```bash
# 创建命名空间
kubectl create namespace agent-perpetual

# 部署 ConfigMap
kubectl apply -f k8s/configmap.yaml -n agent-perpetual

# 部署 Service
kubectl apply -f k8s/service.yaml -n agent-perpetual

# 部署 Deployment
kubectl apply -f k8s/deployment.yaml -n agent-perpetual

# 检查状态
kubectl get pods -n agent-perpetual
kubectl get services -n agent-perpetual
```

---

## 云平台部署

### AWS (EKS)

```yaml
# eks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-perpetual
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-perpetual
  template:
    spec:
      containers:
        - name: agent-perpetual
          image: agentperpetual/agent-perpetual:2.0.0
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: agent-perpetual-secrets
                  key: database-url
```

### GCP (GKE)

```bash
# 创建集群
gcloud container clusters create agent-perpetual-cluster \
  --zone us-central1-a \
  --machine-type e2-standard-2

# 获取凭证
gcloud container clusters get-credentials agent-perpetual-cluster

# 部署
kubectl apply -f k8s/
```

### Azure (AKS)

```bash
# 创建资源组
az group create --name agent-perpetual-rg --location eastus

# 创建 AKS 集群
az aks create \
  --resource-group agent-perpetual-rg \
  --name agent-perpetual-aks \
  --node-vm-size Standard_DS2_v2

# 获取凭证
az aks get-credentials --resource-group agent-perpetual-rg --name agent-perpetual-aks

# 部署
kubectl apply -f k8s/
```

---

## 生产环境配置

### 数据库配置

#### PostgreSQL

```bash
# 使用 PostgreSQL
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/agent_perpetual
```

#### MySQL

```bash
# 使用 MySQL
export DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/agent_perpetual
```

### Redis 配置

```yaml
# docker-compose.prod.yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  volumes:
    - redis-data:/data
```

### 安全配置

```bash
# 设置密钥
export SECRET_KEY=your-super-secret-key-here
export REDIS_PASSWORD=your-redis-password

# 配置 CORS
export CORS_ORIGINS=https://your-domain.com
```

### 日志配置

```yaml
# 日志配置
logging:
  version: 1
  formatters:
    json:
      class: pythonjsonlogger.jsonlogger.JsonFormatter
  handlers:
    console:
      class: logging.StreamHandler
      formatter: json
  root:
    level: INFO
    handlers: [console]
```

### 监控配置

```yaml
# Prometheus 配置
prometheus:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 10s
```

### 备份策略

```bash
#!/bin/bash
# backup.sh

# 数据库备份
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
gzip backup_*.sql

# 上传到 S3
aws s3 cp backup_*.sql.gz s3://your-bucket/backups/

# 清理本地备份
find . -name "backup_*.sql.gz" -mtime +7 -delete
```

---

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看日志
docker logs agent-perpetual

# 检查配置
docker exec agent-perpetual env | grep -E "(DATABASE|REDIS)"
```

#### 2. 数据库连接失败

```bash
# 检查数据库容器
docker-compose ps postgres

# 测试连接
docker exec agent-perpetual python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
asyncio.run(create_async_engine(os.getenv('DATABASE_URL')).connect())
"
```

#### 3. 内存不足

```bash
# 增加内存限制
docker-compose down
docker-compose -f docker-compose.prod.yaml up -d
```

---

## 升级指南

### 版本升级

```bash
# 1. 拉取新镜像
docker pull agentperpetual/agent-perpetual:2.1.0

# 2. 备份数据
./scripts/backup.sh

# 3. 更新服务
docker-compose down
docker-compose up -d

# 4. 验证
curl http://localhost:8000/health
```

---

## 支持

- 📧 邮箱: support@agent-perpetual.io
- 💬 Slack: https://agent-perpetual.slack.com
- 📖 文档: https://docs.agent-perpetual.io
- 🐛 问题: https://github.com/agent-perpetual/agent-perpetual/issues
