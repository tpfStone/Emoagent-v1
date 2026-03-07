# 情绪对话系统 - 产品需求文档

## 项目概述

### 系统简介
情绪对话系统是一个集成情绪识别、短期记忆、危机干预和智能对话的心理支持原型产品，旨在为用户提供温暖、专业的情绪支持服务。

### 团队分工
项目团队共5人：
- **模型开发**：2人（负责BERT情绪识别模型训练、调优和LLM集成）
- **后端开发**：2人（负责API开发、数据库设计和系统架构）
- **前端开发**：1人（负责用户界面开发和交互设计）

### 核心功能
1. 匿名访问与会话管理
2. 基于 BERT 的情绪识别（单标签）
3. 短期记忆管理（最近 6 轮对话）
4. 危机关键词检测与干预
5. LLM 智能对话生成
6. 用户自评与指标采集
7. 周记统计报告

### 技术架构总览
- **前端**：React 18 + TypeScript + Vite + Zustand + Ant Design
- **后端**：Python 3.13+ / FastAPI，Handler-Service-DAO 三层架构
- **AI 服务**：BERT 情绪识别 + LLM 对话生成（开发阶段 Mock，后续替换为真实 LLM）
- **存储**：PostgreSQL 16+（持久化）+ Redis 7+（缓存）

> 详细架构设计见 [系统架构文档](docs/ARCHITECTURE.md)，LLM 集成方案见 [LLM 集成开发方案](docs/LLM_STRATEGY.md)。

---

## 业务需求

### 1. 匿名进入与会话管理

**后端接口**：
- 接口：`POST /api/auth/anonymous`
- 功能：为新用户生成匿名 token 和 session_id
- 响应示例：
  ```json
  {
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001"
  }
  ```

**前端行为**：
- 页面加载时自动调用获取 token 接口
- 将 token 和 session_id 存储到状态管理（Zustand）
- 所有后续 API 请求自动携带 token

### 2. 核心聊天链路

**后端接口**：
- 接口：`POST /api/chat/message`
- 请求体：
  ```json
  {
    "session_id": "uuid-session-id",
    "user_message": "user input text",
    "token": "uuid-token-string"
  }
  ```
- 处理流程：
  1. 验证 token
  2. 安全门控（危机识别）：匹配危机关键词
  3. 非危机情况下进行情绪识别（BERT 模型）
  4. 从 Redis 获取短期记忆（最近 6 轮）
  5. 组装 prompt（包含情绪标签和历史上下文）
  6. 调用 LLM 生成回复（超时 10s）
  7. 超时降级：返回预设通用回复
  8. 更新 Redis 记忆并落库
- 响应示例：
  ```json
  {
    "assistant_message": "I understand how you feel. Could you tell me more?",
    "emotion_label": "sadness",
    "is_crisis": false,
    "turn_index": 3
  }
  ```

**前端行为**：
- 聊天窗口：消息列表（用户消息 + AI 回复）+ 输入框 + 发送按钮 + 加载状态
- 情绪标签：展示当前轮次的情绪识别结果，不同情绪使用不同颜色标识
- 危机提示：当 `is_crisis=true` 时，特殊样式展示危机干预话术，高亮显示资源热线信息

> 完整 API 规范见 [API 接口文档](docs/API.md)，前端组件设计见 [前端开发指南](docs/FRONTEND.md)。

### 3. 短期记忆管理

**存储策略**：
- Redis 存储最近 6 轮对话
- Key 格式：`memory:{session_id}`
- TTL：24 小时（自动过期）
- 超过 6 轮时自动截断最早的轮次
- 只存储摘要字段，不存原文

**数据结构**：
```json
[
  {
    "turn": 1,
    "user": "Hello",
    "assistant": "Hi there! How can I help you?",
    "emotion": "joy"
  },
  {
    "turn": 2,
    "user": "I've been feeling very anxious lately",
    "assistant": "Could you tell me more about what's making you anxious?",
    "emotion": "fear"
  }
]
```

**前端展示（可选）**：
- 侧边栏显示对话历史摘要
- 情绪变化趋势图（简单折线图）

### 4. 安全/危机干预

**危机规则匹配**：
- 危机关键词存储在数据库表 `crisis_rules`
- 按优先级（priority 降序）匹配所有启用的规则
- 支持正则表达式匹配

**危机响应流程**：
- 命中危机规则后：
  1. 不调用 BERT 情绪识别
  2. 不调用 LLM
  3. 直接返回数据库中配置的固定话术（资源指引）
  4. 标记 `is_crisis=True` 并落库到 turns 表

**前端展示**：
- 危机消息使用特殊样式（如红色边框、警示图标）
- 热线号码可点击拨打（移动端）或复制

> 危机干预规则详见 [config/crisis_intervention_protocols.md](config/crisis_intervention_protocols.md)。

### 5. 指标采集与落库

每轮对话落库到 `turns` 表，记录：
- 基本信息：`session_id`, `turn_index`, `user_message`, `assistant_message`, `created_at`
- 情绪标签：`emotion_label`（sadness, joy, love, anger, fear, surprise）
- 危机标记：`is_crisis`（boolean）
- 性能指标：`bert_latency_ms`, `llm_latency_ms`

**统计维度（D类指标）**：
- 危机会话数量
- 危机关键词分布
- 情绪分布统计
- 响应时长分析

### 6. 用户自评

**后端接口**：
- 接口：`POST /api/ratings`
- 请求体：
  ```json
  {
    "session_id": "uuid-session-id",
    "rating_type": "before",
    "score": 7,
    "token": "uuid-token-string"
  }
  ```
- `rating_type`：`"before"` 或 `"after"`
- `score`：1-10 分

**前端行为**：
- 会话开始前弹出自评弹窗（before）
- 会话结束时弹出自评弹窗（after）
- 1-10 分的评分按钮或滑块
- 可选的文字说明输入框

### 7. 最小周记接口

**后端接口**：
- 接口：`GET /api/reports/weekly?session_id={session_id}`
- 响应示例：
  ```json
  {
    "session_count": 5,
    "total_turns": 42,
    "avg_turns_per_session": 8.4,
    "emotion_distribution": {
      "joy": 15,
      "fear": 12,
      "sadness": 10,
      "anger": 8,
      "love": 5,
      "surprise": 3
    },
    "crisis_count": 2,
    "rating_before_avg": 4.2,
    "rating_after_avg": 6.8,
    "rating_missing_rate": 0.2
  }
  ```

**前端行为**：
- 卡片展示关键指标
- 情绪分布饼图/柱状图
- 评分前后对比图

---

## 数据库设计

### 表清单

| 表名 | 用途 |
|------|------|
| `sessions` | 管理匿名会话基本信息（session_id, token, 活跃时间） |
| `conversations` | 记录每个会话的对话元信息（轮数统计）**【阶段1仅建表，不编写业务代码；未来用于多对话支持和长期记忆】** |
| `turns` | 存储每轮对话的详细信息和性能指标（核心指标表） |
| `crisis_rules` | 存储危机关键词及对应的干预话术 |
| `user_ratings` | 存储用户的前后自评数据（1-10分） |

> 完整的表结构、索引策略、ORM 模型和迁移指南见 [数据库文档](docs/DATABASE.md)。

---

## API 接口清单

| 路径 | 方法 | 功能 | Handler |
|------|------|------|---------|
| `/api/auth/anonymous` | POST | 获取匿名 token | AuthHandler |
| `/api/chat/message` | POST | 发送消息 | ChatHandler |
| `/api/ratings` | POST | 提交自评 | RatingHandler |
| `/api/reports/weekly` | GET | 获取周报 | ReportHandler |

> 完整的请求/响应规范、错误码和调用示例见 [API 接口文档](docs/API.md)。

---

## 阶段1范围说明

### 明确实现范围
1. ✅ 短期记忆：最近6轮，Redis缓存，TTL=24h
2. ✅ 情绪识别：BERT单标签分类（使用 nateraw/bert-base-uncased-emotion 模型，输出 sadness, joy, love, anger, fear, surprise）
3. ✅ 危机干预：关键词匹配，固定话术，通用地区
4. ✅ 指标采集：D类指标（会话数、轮数、情绪分布、危机统计）
5. ✅ LLM降级：10s超时自动返回预设回复
6. ✅ **LLM 集成**：开发阶段使用 Mock，后续替换为 DeepSeek 等真实 LLM，抽象层支持随时切换
7. ✅ **前端界面**：聊天页面、周报页面

### 暂不实现（后续阶段）
- ❌ 长期记忆与个性化
- ❌ 多标签情绪识别
- ❌ 危机话术地区差异化
- ❌ 复杂的周报可视化（阶段1仅提供基础图表）
- ❌ WebSocket 实时推送（阶段1使用轮询）

---

## 测试与交付标准

### 测试要求
- **DAO 层单元测试**：使用内存数据库（SQLite）测试 CRUD 操作
- **Service 层单元测试**：Mock DAO 和外部服务，测试业务逻辑
- **LLM 服务测试**：Mock API，测试超时、降级逻辑
- **Handler 层集成测试**：使用 FastAPI TestClient 测试完整 API 流程
- **前端测试**：Vitest + React Testing Library
- **覆盖率要求**：总体代码覆盖率 > 80%

> 详细测试策略和示例见 [测试指南](docs/TESTING.md)。

### 交付标准
- **模型团队**：BERT情绪识别模型(准确率>85%)、LLM集成测试通过
- **后端团队**：API接口完整、数据库设计实现、测试覆盖率>80%
- **前端团队**：React应用完成、UI/UX流畅、与后端API完整对接

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [系统架构](docs/ARCHITECTURE.md) | 分层架构、LLM 可替换设计、数据流详解 |
| [LLM 集成开发方案](docs/LLM_STRATEGY.md) | 开发分阶段接入：Mock → DeepSeek → 按需替换 |
| [API 接口文档](docs/API.md) | 完整的 REST API 规范和调用示例 |
| [前端开发指南](docs/FRONTEND.md) | React 组件设计、状态管理、样式系统 |
| [数据库文档](docs/DATABASE.md) | 表结构、索引策略、ORM 模型、迁移指南 |
| [测试指南](docs/TESTING.md) | 测试金字塔、分层测试示例、CI/CD |
| [部署文档](docs/DEPLOYMENT.md) | Docker Compose、Nginx、SSL 配置 |
| [开发指南](docs/DEVELOPMENT.md) | 环境搭建、代码规范、调试技巧 |
| [危机干预协议](config/crisis_intervention_protocols.md) | 危机关键词和固定话术 |
| [LLM 降级响应](config/llm_fallback_responses.md) | LLM 不可用时的静态回复模板 |
| [Prompt 模板](config/prompt_template.md) | LLM 调用时使用的 Prompt 模板 |
