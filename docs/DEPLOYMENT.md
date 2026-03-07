# 部署文档

## 环境要求

### 后端环境
- **操作系统**: Linux (Ubuntu 20.04+) / macOS / Windows
- **Python**: 3.13+
- **数据库**: PostgreSQL 16+
- **缓存**: Redis 7+
- **内存**: 最低 4GB（生产环境 8GB+）
- **磁盘**: 最低 20GB（用于 BERT 模型和日志）

### 前端环境
- **Node.js**: 18+
- **包管理器**: npm / pnpm / yarn

### 网络要求
- 外网访问（调用 DeepSeek API）
- HTTPS 证书（生产环境）

### 部署职责分工
**模型团队（2人）**：
- BERT模型文件准备和部署
- LLM API密钥配置和测试
- 模型推理性能优化

**后端团队（2人）**：
- 服务器环境搭建
- 数据库和Redis配置
- API服务部署和监控
- 日志系统配置

**前端团队（1人）**：
- 前端项目构建
- 静态资源部署
- Nginx配置和优化
- CDN配置

---

## 后端配置

### 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```env
# ========== 数据库配置 ==========
DATABASE_URL=postgresql://emoagent_user:your_secure_password@localhost:5432/emoagent
POSTGRES_USER=emoagent_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=emoagent

# ========== Redis 配置 ==========
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# ========== LLM 配置 ==========
# 第一阶段：Mock LLM（开发测试，推荐初期使用）
# LLM_PROVIDER=mock

# 第二阶段：DeepSeek 免费额度（真实测试）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 生产阶段：按需替换为其他 LLM
QIANWEN_API_KEY=
WENXIN_API_KEY=

# ========== 应用配置 ==========
ENV=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here

# ========== CORS 配置 ==========
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ========== BERT 模型配置 ==========
BERT_MODEL_PATH=./models/bert-emotion
BERT_MODEL_NAME=nateraw/bert-base-uncased-emotion

# ========== 服务器配置 ==========
HOST=0.0.0.0
PORT=8000
WORKERS=4

# ========== 监控配置（可选） ==========
SENTRY_DSN=
```

### 配置说明

| 配置项 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | - | ✅ |
| `REDIS_URL` | Redis 连接字符串 | redis://localhost:6379/0 | ✅ |
| `LLM_PROVIDER` | LLM 提供商（mock/deepseek/qianwen/wenxin） | mock | ✅ |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥（第二阶段需要） | - | ❌ |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔） | * | ✅ |
| `WORKERS` | Uvicorn 工作进程数 | 4 | ❌ |
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | INFO | ❌ |

---

## 前端配置

### 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```env
# ========== API 配置 ==========
VITE_API_BASE_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com/ws

# ========== 功能开关 ==========
VITE_ENABLE_DEV_TOOLS=false
VITE_ENABLE_ANALYTICS=true

# ========== 第三方服务（可选） ==========
VITE_SENTRY_DSN=
VITE_GA_TRACKING_ID=
```

---

## Docker 部署

### Docker Compose 配置

Docker Compose是本项目的标准部署方式，简化了多服务编排和配置管理。

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    container_name: emoagent-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  
  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: emoagent-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped
  
  # 后端 API
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: emoagent-backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      LLM_PROVIDER: ${LLM_PROVIDER}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      DEEPSEEK_BASE_URL: ${DEEPSEEK_BASE_URL}
      DEEPSEEK_MODEL: ${DEEPSEEK_MODEL}
      CORS_ORIGINS: ${CORS_ORIGINS}
      ENV: production
      DEBUG: false
      LOG_LEVEL: INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
  
  # 前端应用（Nginx）
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: emoagent-frontend
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: emoagent-network
```

### 后端 Dockerfile

```dockerfile
# Dockerfile（项目根目录）
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY ./app ./app
COPY ./config ./config
COPY ./alembic ./alembic
COPY ./alembic.ini .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 前端 Dockerfile

```dockerfile
# frontend/Dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 启动 Docker Compose

```bash
# 1. 确保 .env 文件已配置
cp .env.example .env
# 编辑 .env 文件

# 2. 构建并启动所有服务
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f backend

# 5. 停止服务
docker-compose down

# 6. 完全清理（包括数据卷）
docker-compose down -v
```

---

## 手动部署

### 后端部署

#### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2. 数据库迁移

```bash
# 初始化 Alembic（如果还没有）
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial tables"

# 执行迁移
alembic upgrade head
```

#### 3. 导入种子数据

```bash
psql -U emoagent_user -d emoagent -f scripts/seed_crisis_rules.sql
```

#### 4. 下载 BERT 模型

本项目使用 `nateraw/bert-base-uncased-emotion` 模型（6 种情绪分类）。

```bash
# 方式一：使用 transformers 自动下载
python -c "from transformers import AutoModelForSequenceClassification, AutoTokenizer; AutoModelForSequenceClassification.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models'); AutoTokenizer.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models')"

# 方式二：手动下载后放置到 models/ 目录
```

#### 5. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（单进程）
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 生产模式（多进程）
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署

#### 1. 安装依赖

```bash
cd frontend
npm install
```

#### 2. 构建生产版本

```bash
# 确保 .env 文件配置正确
npm run build

# 构建产物在 dist/ 目录
```

#### 3. 部署到 Nginx

```bash
# 复制构建产物到 Nginx 目录
sudo cp -r dist/* /var/www/html/

# 配置 Nginx
sudo nano /etc/nginx/sites-available/emoagent

# Nginx 配置内容（见上面的 nginx.conf）

# 启用配置
sudo ln -s /etc/nginx/sites-available/emoagent /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 生产环境优化

### 后端优化

#### 1. 使用 Gunicorn + Uvicorn Workers

```bash
# 安装 gunicorn
pip install gunicorn

# 启动（4 个 worker）
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

#### 2. Systemd 服务

创建 `/etc/systemd/system/emoagent.service`：

```ini
[Unit]
Description=Emotion Chat System Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/emoagent
Environment="PATH=/var/www/emoagent/.venv/bin"
EnvironmentFile=/var/www/emoagent/.env
ExecStart=/var/www/emoagent/.venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable emoagent
sudo systemctl start emoagent
sudo systemctl status emoagent
```

### 前端优化

#### 1. 生产构建优化

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'axios', 'zustand'],
          charts: ['recharts'],
        },
      },
    },
  },
});
```

#### 2. CDN 加速

使用 CDN 托管静态资源：

```html
<!-- index.html -->
<link rel="dns-prefetch" href="https://cdn.example.com">
<link rel="preconnect" href="https://cdn.example.com">
```

---

## 监控和日志

### 日志配置

```python
# app/utils/logger.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

### Prometheus 指标（可选）

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 添加 Prometheus 指标
Instrumentator().instrument(app).expose(app)
```

### Sentry 错误追踪（可选）

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENV", "production"),
)
```

---

## 数据库备份

### PostgreSQL 备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/var/backups/emoagent
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME=emoagent
DB_USER=emoagent_user

mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U $DB_USER -F c $DB_NAME > $BACKUP_DIR/emoagent_$DATE.backup

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete

echo "Backup completed: emoagent_$DATE.backup"
```

设置定时任务：

```bash
# crontab -e
0 2 * * * /path/to/backup.sh
```

### 恢复数据库

```bash
pg_restore -U emoagent_user -d emoagent -c /path/to/backup.backup
```

---

## SSL/HTTPS 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### Nginx HTTPS 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... 其他配置
}
```

---

## 常见问题

### Q1: BERT 模型加载失败
**解决方案**：
```bash
# 检查模型文件是否完整
ls -lh models/bert-emotion/

# 手动下载模型
python -c "from transformers import AutoModelForSequenceClassification, AutoTokenizer; AutoModelForSequenceClassification.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models'); AutoTokenizer.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models')"
```

### Q2: DeepSeek API 超时
**解决方案**：
- 检查网络连接
- 增加超时时间（环境变量 `LLM_TIMEOUT`）
- 启用降级策略

### Q3: PostgreSQL 连接失败
**解决方案**：
```bash
# 检查 PostgreSQL 服务状态
sudo systemctl status postgresql

# 检查连接字符串
psql -U emoagent_user -d emoagent -h localhost
```

### Q4: CORS 错误
**解决方案**：
- 确认 `.env` 中 `CORS_ORIGINS` 配置正确
- 检查前端请求的 Origin 是否在允许列表中

---

## 待补充内容

- [ ] Kubernetes 部署方案
- [ ] CI/CD 流程配置（GitHub Actions / GitLab CI）
- [ ] 负载均衡配置（Nginx / Traefik）
- [ ] 蓝绿部署策略
- [ ] 灰度发布方案
- [ ] 监控告警配置（Grafana + AlertManager）
- [ ] 日志聚合方案（ELK Stack）
- [ ] 数据库主从复制

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-04  
**维护者**: 后端团队（部署主导）+ 模型团队（模型部署）+ 前端团队（前端部署）
