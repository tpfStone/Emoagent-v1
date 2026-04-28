# 文档中心

欢迎来到情绪对话系统的文档中心。本目录包含项目的完整技术文档，涵盖从架构设计到部署运维的全流程。

## 文档导航

### 技术文档

#### [快速开始指南](QUICKSTART.md)
面向首次运行项目的最短路径：
- Docker Compose 快速启动
- 本地开发启动
- 服务健康检查
- 基础功能验证
- 常见启动问题排查

**适合**：首次接手项目的开发者、测试人员

---

#### [系统架构文档](ARCHITECTURE.md)
全栈架构设计详解：
- 整体架构概览（前后端分离）
- 团队分工（2人模型 + 2人后端 + 1人前端）
- 后端分层架构（Handler-Service-DAO）
- 前端组件化设计
- **LLM 可替换架构**（抽象层 + 依赖注入）
- 数据流详解（Sequence Diagram）
- 安全设计、性能优化、可扩展性
- 技术决策记录（ADR）

**适合**：架构师、技术负责人、全栈开发者

---

#### [LLM 集成开发方案](LLM_STRATEGY.md)
说明开发过程中 LLM 集成部分经历的三个阶段：
- 开发阶段：使用 Mock LLM，免费且无外部依赖
- 测试阶段：替换为 DeepSeek 等真实 LLM，验证端到端效果
- 生产阶段：按需评估切换（通义千问、文心一言等）
- 切换操作指南、成本控制、故障降级策略

**适合**：模型团队（2人）、架构师

---

#### [API 接口文档](API.md)
详细的 REST API 接口规范：
- 认证接口（获取匿名 token）
- 聊天接口（发送消息、情绪识别）
- 自评接口（提交评分）
- 周记接口（获取统计报告）
- 错误码说明
- 调用示例（curl、JavaScript、Python）

**适合**：前端开发者、API 集成人员

---

#### [前端开发指南](FRONTEND.md)
前端架构、组件设计和开发规范：
- 技术选型（React + TypeScript + Vite）
- 项目结构设计
- API 调用封装（TypeScript）
- 状态管理（Zustand）
- 核心组件设计（ChatWindow、EmotionBadge、RatingModal）
- 样式系统（情绪颜色定义）
- **国际化方案（i18n）**：集中式 locale 文件、类型安全、语言扩展指南
- 测试策略

**适合**：前端开发者（1人）

---

#### [部署文档](DEPLOYMENT.md)
生产环境部署指南：
- **多环境配置管理**（development/testing/production）
- 环境要求（Python、Node.js、PostgreSQL、Redis）
- 后端配置（环境变量、数据库迁移）
- 前端配置（构建优化）
- **Docker Compose 部署**（推荐方式）
- 手动部署流程
- Nginx 配置、SSL/HTTPS 配置
- 监控系统部署、CI/CD集成
- 数据库备份与恢复

**适合**：DevOps 工程师、运维人员

---

#### [监控与可观测性文档](MONITORING.md)
Prometheus + Grafana监控体系：
- 监控架构和技术选型
- 指标体系（业务、性能、情绪、健康）
- Grafana仪表板使用
- 告警配置（可选）
- 常用PromQL查询
- LLMOps监控扩展方案（真实LLM上线后）
- 故障排查和最佳实践

**适合**：后端开发者（2人）、运维人员

---

#### [测试指南](TESTING.md)
完整的测试策略和实践：
- 测试金字塔（单元测试、集成测试、E2E 测试）
- 后端测试（Pytest、Mock、Fixtures）
- 前端测试（Vitest、React Testing Library、Playwright）
- 覆盖率要求（>80%）
- 性能测试（Locust）
- CI/CD 集成（GitHub Actions）

**适合**：QA 工程师、开发者

---

#### [数据库文档](DATABASE.md)
数据库设计和管理：
- 表结构设计（5张表详细说明）
- ER 图（Mermaid 可视化）
- 索引策略
- 数据迁移（Alembic）
- 数据字典、性能优化
- 备份与恢复、安全建议

**适合**：后端开发者（2人）、DBA

---

#### [开发指南](DEVELOPMENT.md)
本地开发环境搭建和开发规范：
- 快速开始（后端 + 前端）
- 环境准备（软件安装、配置）
- 开发工作流（Git 分支策略、Commit 规范）
- 代码规范（Python PEP 8、TypeScript ESLint）
- 调试技巧（pdb、DevTools）
- 测试驱动开发（TDD）
- 性能优化技巧、常见问题（FAQ）

**适合**：全体开发者

---

### 协作、验证与实施文档

#### [Git 工作流与提交规范](GIT_WORKFLOW.md)
团队协作和提交规范：
- 分支策略
- Conventional Commits
- CHANGELOG 更新规范
- Pull Request 规范
- CI/CD 集成
- 发布和回滚流程

**适合**：所有提交代码或文档的成员

---

#### [新功能测试指引](NEW_FEATURE_TESTING.md)
本次新增运行能力的验收记录和测试流程：
- HealthService 和 `/health` 自动化测试
- 多环境模板验证
- 前后端本地 CI 等价检查
- Docker Compose 运行态验证
- Prometheus/Grafana 验证
- 本轮测试记录和已修复问题

**适合**：推送 GitHub 前的验收测试、后续回归参考

---

#### [实施总结](IMPLEMENTATION_SUMMARY.md)
监控、CI/CD、多环境配置和 Docker 优化的正式实施总结：
- 完成任务清单
- 文件变更清单
- 功能验证清单
- 风险和后续优化

**适合**：了解 v0.2.0 变更背景和验收状态

---

### 调研与规划文档

#### [调研文档目录](research/README.md)
尚未进入实现阶段的新功能调研和方案对比：
- [并发控制研究方案](research/并发控制研究方案.md)

**适合**：新功能上线前的技术选型和方案评审

---

#### [规划文档目录](planning/README.md)
项目后续路线图、优先级和阶段性任务：
- [下一步决策](planning/下一步决策.md)

**适合**：排期、优先级讨论和后续任务跟踪

---

### 脚本文件

以下文件位于 `scripts/` 目录：

| 文件 | 说明 |
|------|------|
| [crisis_rules 种子数据](../scripts/seed_crisis_rules.sql) | crisis_rules 表初始化数据（6 类危机场景的关键词和干预话术） |

### 配置文件

以下文件位于 `config/` 目录，是系统运行时使用的配置/模板数据：

| 文件 | 说明 |
|------|------|
| [危机干预协议](../config/crisis_intervention_protocols.md) | 6 类危机场景的触发关键词和固定话术 |
| [LLM 降级响应](../config/llm_fallback_responses.md) | LLM 不可用时按情绪分类的静态回复模板 |
| [Prompt 模板](../config/prompt_template.md) | 调用 LLM 生成回复时使用的系统提示词 |

---

## 快速链接

- **开始开发** → [开发指南](DEVELOPMENT.md)
- **快速启动** → [快速开始指南](QUICKSTART.md)
- **调用 API** → [API 文档](API.md)
- **了解架构** → [系统架构](ARCHITECTURE.md)
- **了解 LLM 集成方案** → [LLM 集成开发方案](LLM_STRATEGY.md)
- **部署系统** → [部署文档](DEPLOYMENT.md)
- **配置监控** → [监控文档](MONITORING.md)
- **编写测试** → [测试指南](TESTING.md)
- **验收新功能** → [新功能测试指引](NEW_FEATURE_TESTING.md)
- **查看 Git 规范** → [Git 工作流](GIT_WORKFLOW.md)
- **查看实施总结** → [实施总结](IMPLEMENTATION_SUMMARY.md)
- **查看后续规划** → [下一步决策](planning/下一步决策.md)
- **查看调研方案** → [调研文档](research/README.md)
- **设计数据库** → [数据库文档](DATABASE.md)
- **开发前端** → [前端指南](FRONTEND.md)

---

## 文档状态

| 文档 | 状态 | 最后更新 |
|------|------|---------|
| ARCHITECTURE.md | ✅ 完成 | 2026-03-02 |
| LLM_STRATEGY.md | ✅ 完成 | 2026-03-04 |
| API.md | ✅ 完成 | 2026-03-02 |
| FRONTEND.md | ✅ 完成（Ant Design + i18n） | 2026-03-06 |
| DEPLOYMENT.md | ✅ 完成（多环境+CI/CD） | 2026-03-13 |
| MONITORING.md | ✅ 完成 | 2026-03-13 |
| TESTING.md | ✅ 完成 | 2026-03-02 |
| DATABASE.md | ✅ 完成 | 2026-03-02 |
| DEVELOPMENT.md | ✅ 完成 | 2026-03-04 |
| QUICKSTART.md | ✅ 完成 | 2026-03-13 |
| GIT_WORKFLOW.md | ✅ 完成 | 2026-03-25 |
| IMPLEMENTATION_SUMMARY.md | ✅ 完成 | 2026-04-28 |
| NEW_FEATURE_TESTING.md | ✅ 完成 | 2026-04-28 |
| research/ | 📌 调研中 | 2026-04-28 |
| planning/ | 📌 持续更新 | 2026-04-28 |

---

## 相关资源

### 项目文档
- [项目 README](../README.md) - 项目简介和快速开始
- [需求文档](../demand.md) - 产品需求和业务规则

### 外部资源
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)

---

**文档版本**: v0.2.1  
**发布日期**: 2026-04-28  
**更新说明**: 新增调研、规划目录，补充新功能测试指引和文档索引
