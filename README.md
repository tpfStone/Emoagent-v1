# 情绪对话系统（EmoAgent v1）

[![Backend CI](https://github.com/YOUR_USERNAME/emoagent-v1/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/emoagent-v1/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/YOUR_USERNAME/emoagent-v1/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/emoagent-v1/actions/workflows/frontend-ci.yml)

情绪对话系统是一个集成情绪识别、短期记忆、危机干预和智能对话的心理支持原型产品，旨在为用户提供温暖、专业的情绪支持服务。

## 核心功能

1. **匿名访问与会话管理** — 无需注册，即开即用
2. **BERT 情绪识别** — 基于 `nateraw/bert-base-uncased-emotion` 模型，6 种情绪分类
3. **短期记忆管理** — Redis 缓存最近 6 轮对话，TTL=24h
4. **危机关键词检测与干预** — 命中危机规则时绕过 LLM，直接返回专业资源指引
5. **LLM 智能对话生成** — 开发阶段先用 Mock，后续替换为 DeepSeek 等真实 LLM，10s 超时自动降级
6. **用户自评与指标采集** — 会话前后 1-10 分自评，D 类指标落库
7. **周记统计报告** — 聚合 JSON 接口，前端图表展示

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 前端 | React 18 + TypeScript + Vite + Zustand + Ant Design |
| 后端 | Python 3.13 + FastAPI + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 16+ |
| 缓存 | Redis 7+（短期记忆） |
| AI 模型 | BERT 情绪识别（本地推理）+ LLM 对话生成（可替换） |

## 团队分工

| 角色 | 人数 | 职责 |
|------|------|------|
| 模型开发 | 2 人 | BERT 情绪识别模型训练/调优、LLM 集成、Prompt 工程 |
| 后端开发 | 2 人 | FastAPI 服务、数据库设计、Redis 缓存、系统架构 |
| 前端开发 | 1 人 | React 应用开发、UI/UX 设计、与后端 API 对接 |

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env（默认使用 Mock LLM，无需 API Key）

# 数据库迁移
alembic upgrade head

# 导入危机干预规则种子数据
psql -U emoagent_user -d emoagent -f scripts/seed_crisis_rules.sql

# 启动服务
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问 http://localhost:5173 查看前端界面，API 文档访问 http://localhost:8000/docs 。

### Docker Compose 快速启动

```bash
# 启动所有服务（包括监控）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

访问地址：
- 前端界面：http://localhost:5173
- 后端API：http://localhost:8200
- API文档：http://localhost:8200/docs
- Prometheus：http://localhost:9090
- Grafana：http://localhost:3000（默认登录：admin/admin）

### 多环境配置

项目支持三种运行环境，使用不同的配置文件：

```bash
# 开发环境（使用Mock LLM，详细日志）
cp .env.development .env
docker-compose up -d

# 测试环境（CI/CD使用）
cp .env.testing .env
pytest tests/

# 生产环境（真实LLM，最小日志）
cp .env.production .env
# 修改生产配置中的密码和API Key
docker-compose up -d
```

**环境差异**：

| 配置项 | development | testing | production |
|--------|-------------|---------|------------|
| LLM_PROVIDER | mock | mock | deepseek |
| DEBUG | true | false | false |
| LOG_LEVEL | DEBUG | INFO | WARNING |
| ENABLE_API_DOCS | true | true | false |
| ENABLE_METRICS | true | false | true |

## 项目结构

```
emoagent-v1/
├── app/                    # 后端应用代码（Handler-Service-DAO 三层架构）
│   ├── dao/                # 数据访问层
│   ├── handlers/           # 路由处理层
│   ├── models/             # SQLAlchemy 数据模型
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── services/           # 业务逻辑层
│   └── utils/              # 工具函数
├── frontend/               # 前端 React 应用
├── tests/                  # 后端测试
├── alembic/                # 数据库迁移文件
├── config/                 # 配置文件（危机规则、降级话术、Prompt 模板）
├── scripts/                # 脚本（种子数据等）
│   └── seed_crisis_rules.sql  # crisis_rules 表初始化数据
├── docs/                   # 技术文档中心
│   ├── README.md           # 文档索引
│   ├── QUICKSTART.md       # 快速开始指南
│   ├── ARCHITECTURE.md     # 系统架构
│   ├── LLM_STRATEGY.md     # LLM 集成开发方案
│   ├── API.md              # API 接口文档
│   ├── FRONTEND.md         # 前端开发指南
│   ├── DATABASE.md         # 数据库设计
│   ├── TESTING.md          # 测试指南
│   ├── DEPLOYMENT.md       # 部署文档
│   ├── DEVELOPMENT.md      # 开发指南
│   └── MONITORING.md       # 监控与可观测性
├── monitoring/            # 监控配置
│   ├── prometheus.yml     # Prometheus配置
│   └── grafana/           # Grafana配置和仪表板
├── .github/workflows/     # CI/CD工作流
│   ├── backend-ci.yml     # 后端测试流程
│   └── frontend-ci.yml    # 前端测试流程
├── demand.md               # 产品需求文档
├── CHANGELOG.md            # 更新日志
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── requirements.txt        # Python 依赖
├── alembic.ini             # Alembic 迁移配置
├── Dockerfile              # 后端 Docker 镜像
└── docker-compose.yml      # Docker Compose 编排
```

## 监控系统

系统集成了Prometheus + Grafana监控体系，提供实时的业务指标、性能指标和健康状态监控。

**监控能力**：
- ✅ 业务指标：会话数、消息数、危机触发次数、自评分布
- ✅ 性能指标：BERT推理延迟、API响应时间
- ✅ 情绪分析：实时情绪分布、活跃会话数
- ✅ 系统健康：数据库、Redis、LLM服务状态
- ⏳ LLMOps指标：Token消耗、成本追踪（待真实LLM上线后补充）

**访问地址**：
- Prometheus：http://localhost:9090
- Grafana：http://localhost:3000（admin/admin）
- 指标端点：http://localhost:8200/metrics
- 健康检查：http://localhost:8200/health

详见 [监控文档](docs/MONITORING.md)

## CI/CD

项目使用GitHub Actions实现自动化测试和代码质量检查。

**CI流程**：
- ✅ 后端CI：代码格式检查（black、isort）、类型检查（mypy）、单元测试、覆盖率报告
- ✅ 前端CI：ESLint检查、TypeScript类型检查、单元测试、构建验证

**触发条件**：
- Push到main/develop分支
- 提交Pull Request到main分支

## 文档导航

- **想了解需求** → [需求文档](demand.md)
- **想了解架构** → [系统架构](docs/ARCHITECTURE.md)
- **想调用 API** → [API 文档](docs/API.md)
- **想开始开发** → [开发指南](docs/DEVELOPMENT.md)
- **想部署系统** → [部署文档](docs/DEPLOYMENT.md)
- **想编写测试** → [测试指南](docs/TESTING.md)
- **想了解 LLM 集成方案** → [LLM 集成开发方案](docs/LLM_STRATEGY.md)
- **想配置监控** → [监控文档](docs/MONITORING.md)
- **查看所有文档** → [文档中心](docs/README.md)

## 许可证

本项目采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 协议授权。
