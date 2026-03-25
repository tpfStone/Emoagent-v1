# 快速开始指南

本指南帮助开发者在15分钟内完成EmoAgent本地环境搭建和运行。

## 前置要求

### 必须安装

- **Docker Desktop** (20.10+) 和 Docker Compose
- **Git** (2.30+)

### 可选安装

如果需要本地开发（不使用Docker），还需要：
- **Python** 3.13+
- **Node.js** 18+
- **PostgreSQL** 16+
- **Redis** 7+

## 快速启动（Docker Compose 推荐）

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/emoagent-v1.git
cd emoagent-v1
```

### 2. 配置环境变量

```bash
# 使用开发环境配置
cp .env.development .env

# 或手动创建（最小配置）
cat > .env << 'EOF'
DATABASE_URL=postgresql://emoagent_user:dev_password@postgres:5432/emoagent
POSTGRES_USER=emoagent_user
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=emoagent
REDIS_URL=redis://redis:6379/0
LLM_PROVIDER=mock
ENV=development
DEBUG=true
LOG_LEVEL=INFO
ENABLE_METRICS=true
CORS_ORIGINS=http://localhost:5173
EOF
```

### 3. 启动所有服务

```bash
# 构建并启动（首次运行约5-10分钟，需下载镜像）
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

**预期输出**：

```
NAME                   STATUS         PORTS
emoagent-backend       Up (healthy)   0.0.0.0:8200->8000/tcp
emoagent-postgres      Up (healthy)   0.0.0.0:5432->5432/tcp
emoagent-redis         Up (healthy)   0.0.0.0:6379->6379/tcp
emoagent-prometheus    Up             0.0.0.0:9090->9090/tcp
emoagent-grafana       Up             0.0.0.0:3000->3000/tcp
```

### 4. 初始化数据库

```bash
# 等待后端服务健康（约30-40秒）
docker-compose logs -f backend | grep "Application startup complete"

# 导入危机干预规则种子数据
docker exec -i emoagent-postgres psql -U emoagent_user -d emoagent < scripts/seed_crisis_rules.sql

# 验证数据导入
docker exec emoagent-postgres psql -U emoagent_user -d emoagent -c "SELECT COUNT(*) FROM crisis_rules;"
```

### 5. 验证服务

```bash
# 健康检查
curl http://localhost:8200/health

# API文档
open http://localhost:8200/docs

# Prometheus指标
curl http://localhost:8200/metrics

# Grafana仪表板
open http://localhost:3000  # 登录：admin/admin
```

### 6. 测试API调用

```bash
# 创建匿名会话
curl -X POST http://localhost:8200/api/auth/anonymous

# 发送测试消息（替换YOUR_SESSION_ID和YOUR_TOKEN）
curl -X POST http://localhost:8200/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "user_message": "I feel sad today",
    "token": "YOUR_TOKEN"
  }'
```

## 本地开发启动（不使用Docker）

### 1. 安装依赖

**后端**：

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

**前端**：

```bash
cd frontend
npm install
```

### 2. 启动数据库服务

```bash
# 仅启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 等待服务就绪
docker-compose logs postgres redis
```

### 3. 数据库迁移

```bash
# 执行Alembic迁移
alembic upgrade head

# 导入种子数据
psql -U emoagent_user -d emoagent -h localhost -f scripts/seed_crisis_rules.sql
```

### 4. 启动后端服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8200

# 访问 http://localhost:8200/docs 查看API文档
```

### 5. 启动前端服务

```bash
cd frontend

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 VITE_API_BASE_URL=http://localhost:8200

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 功能验证

### 基础功能测试

1. **匿名会话创建**：
   - 打开前端界面
   - 应自动创建会话并存储到localStorage

2. **情绪识别对话**：
   - 输入："I feel very sad and lonely"
   - 应返回同理心回复
   - 情绪标签应显示（如果BERT启用）

3. **危机干预触发**：
   - 输入："I want to end my life"
   - 应返回危机干预话术和资源链接
   - 消息顶部应显示红色危机提示

4. **自评功能**：
   - 提交前后自评（1-10分）
   - 数据应保存到数据库

5. **周记报告**：
   - 点击"Weekly Report"查看统计
   - 应显示情绪分布、消息数等

### 监控系统测试

1. **Prometheus**（http://localhost:9090）：
   - 访问 Status → Targets
   - 确认backend目标状态为"UP"
   - 执行查询：`emoagent_sessions_total`

2. **Grafana**（http://localhost:3000）：
   - 登录（admin/admin）
   - 打开 `EmoAgent - System Monitoring` 仪表板
   - 发送几条消息后，观察指标变化

3. **健康检查**：
   - 访问：http://localhost:8200/health
   - 应返回所有组件"up"状态

## 常见问题

### Q1: BERT模型加载失败

**错误信息**：`RuntimeError: BERT model failed to load`

**解决方案**：

```bash
# 方式一：手动下载模型（推荐）
python -c "
from transformers import AutoModelForSequenceClassification, AutoTokenizer
AutoTokenizer.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models')
AutoModelForSequenceClassification.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models')
"

# 方式二：禁用BERT推理（开发调试）
echo "ENABLE_EMOTION_DETECTION=false" >> .env
docker-compose restart backend
```

### Q2: 端口冲突

**错误信息**：`Error starting userland proxy: listen tcp4 0.0.0.0:8200: bind: address already in use`

**解决方案**：

```bash
# 查找占用端口的进程
netstat -ano | findstr :8200  # Windows
lsof -i :8200                 # Linux/macOS

# 修改docker-compose.yml端口映射
# 将 "8200:8000" 改为 "8201:8000"
```

### Q3: PostgreSQL连接失败

**错误信息**：`sqlalchemy.exc.OperationalError: could not connect to server`

**解决方案**：

```bash
# 检查PostgreSQL服务状态
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres

# 重启服务
docker-compose restart postgres

# 等待服务就绪
docker-compose exec postgres pg_isready -U emoagent_user
```

### Q4: 前端无法连接后端

**症状**：前端显示网络错误

**解决方案**：

```bash
# 1. 检查后端服务状态
curl http://localhost:8200/health

# 2. 检查CORS配置（.env文件）
CORS_ORIGINS=http://localhost:5173

# 3. 检查前端环境变量（frontend/.env）
VITE_API_BASE_URL=http://localhost:8200

# 4. 重启服务
docker-compose restart backend
```

### Q5: Grafana无法访问

**症状**：http://localhost:3000 无法打开

**解决方案**：

```bash
# 检查Grafana服务状态
docker-compose ps grafana

# 查看启动日志
docker-compose logs grafana

# 手动启动
docker-compose up -d grafana

# 等待30秒后重试
```

## 停止和清理

### 停止服务

```bash
# 停止所有服务（保留数据）
docker-compose stop

# 停止并删除容器（保留数据卷）
docker-compose down

# 完全清理（删除数据卷）
docker-compose down -v
```

### 清理Docker资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 查看占用空间
docker system df
```

## 下一步

完成快速启动后，建议阅读：

1. **开发新功能** → [开发指南](DEVELOPMENT.md)
2. **了解系统架构** → [系统架构](ARCHITECTURE.md)
3. **编写测试** → [测试指南](TESTING.md)
4. **部署到生产** → [部署文档](DEPLOYMENT.md)
5. **配置监控告警** → [监控文档](MONITORING.md)

## 获取帮助

- **技术文档**：[docs/README.md](README.md)
- **API文档**：http://localhost:8200/docs（服务启动后）
- **问题反馈**：GitHub Issues

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-13  
**维护者**: 全员
