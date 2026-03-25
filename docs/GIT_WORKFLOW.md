# Git 工作流与提交规范

本文档定义了 EmoAgent 项目的 Git 使用规范，包括分支管理、提交规范、CI/CD 集成和协作流程。

---

## 规范范围说明

本文档内容按强制程度分为三类：

### ✅ 强制规范（Mandatory）

以下章节为**团队必须遵守**的规范，所有代码提交和 PR 必须符合这些要求：

- **[分支策略](#分支策略)**
- **[约定式提交规范](#约定式提交规范)**
- **[CHANGELOG 更新规范](#changelog-更新规范)**
- **[Pull Request 规范](#pull-request-规范)**
- **[CI/CD 集成](#cicd-集成)**

### 💡 推荐实践（Recommended）

以下章节为**建议采用**的最佳实践，有助于提升开发效率和代码质量：

- **[工作流程](#工作流程)**
- **[常见场景](#常见场景)**
- **[最佳实践](#最佳实践)**

### 🔧 可选工具（Optional）

以下章节为**非强制性**的辅助工具推荐，开发者可根据个人习惯选择使用：

- **[附录：辅助工具](#附录辅助工具)**

---

## 目录

- [规范范围说明](#规范范围说明)
- [分支策略](#分支策略)
- [约定式提交规范](#约定式提交规范)
- [CHANGELOG 更新规范](#changelog-更新规范)
- [工作流程](#工作流程)
- [Pull Request 规范](#pull-request-规范)
- [CI/CD 集成](#cicd-集成)
- [常见场景](#常见场景)
- [最佳实践](#最佳实践)
- [附录：辅助工具](#附录辅助工具)

---

## 分支策略

项目采用 **Git Flow** 简化版本，包含以下分支类型：

### 主要分支

```
main                # 生产分支（受保护，仅通过 PR 合并）
  ↑
develop            # 开发分支（集成分支，测试通过后合并到 main）
```

#### `main` 分支

- **用途**：生产环境代码，随时可部署
- **保护规则**：
  - 禁止直接推送
  - 必须通过 PR 合并
  - 必须通过 CI 检查
  - 需要至少 1 人审查（团队协作时）
- **合并来源**：仅接受来自 `develop` 或 `hotfix/`* 的合并

#### `develop` 分支

- **用途**：开发集成分支，包含下一版本的所有功能
- **保护规则**：
  - 推荐通过 PR 合并
  - 必须通过 CI 检查
- **合并来源**：接受来自 `feature/`*、`fix/*` 的合并

### 临时分支

#### `feature/*` - 功能分支

```bash
feature/chat-history-export      # 新功能：聊天记录导出
feature/emotion-chart            # 新功能：情绪趋势图表
feature/multi-language-support   # 新功能：多语言支持
```

- **命名规则**：`feature/<功能描述>`（使用小写和连字符）
- **生命周期**：从 `develop` 创建，完成后合并回 `develop` 并删除
- **适用场景**：开发新功能、新特性

#### `fix/`* - Bug 修复分支

```bash
fix/login-token-expiry          # 修复：登录令牌过期问题
fix/emotion-detection-crash     # 修复：情绪检测崩溃
```

- **命名规则**：`fix/<问题描述>`
- **生命周期**：从 `develop` 创建，完成后合并回 `develop` 并删除
- **适用场景**：修复非紧急 bug

#### `hotfix/`* - 紧急修复分支

```bash
hotfix/v0.2.1-security-patch    # 紧急修复：安全漏洞
hotfix/v0.2.1-llm-timeout       # 紧急修复：LLM 超时
```

- **命名规则**：`hotfix/v<版本号>-<问题描述>`
- **生命周期**：从 `main` 创建，完成后同时合并到 `main` 和 `develop`
- **适用场景**：生产环境紧急 bug 修复

---

## 约定式提交规范

项目采用 **[Conventional Commits](https://www.conventionalcommits.org/)** 规范，提升 Git 历史可读性，辅助 CHANGELOG 编写。

### 提交格式

```
<类型>(<范围>): <简短描述>

[可选的详细说明]

[可选的 Footer]
```

#### 基本示例

```bash
feat(chat): 新增聊天记录导出功能
fix(auth): 修复 JWT 过期时间计算错误
docs(readme): 更新部署流程说明
```

#### 详细示例

```bash
feat(emotion): 集成第三代情绪检测模型

- 替换 BERT 模型为 RoBERTa
- 提升情绪识别准确率至 92%
- 优化推理速度至 50ms

Closes #42
```

### 提交类型（Type）


| 类型         | 说明          | 示例                        | 是否触发版本发布 |
| ---------- | ----------- | ------------------------- | -------- |
| `feat`     | 新增功能        | `feat(chat): 新增群聊功能`      | Minor    |
| `fix`      | 修复 Bug      | `fix(auth): 修复登录超时问题`     | Patch    |
| `docs`     | 文档更新        | `docs(api): 更新接口说明`       | 否        |
| `style`    | 代码格式（不影响功能） | `style: 统一代码缩进`           | 否        |
| `refactor` | 重构（不改变功能）   | `refactor(dao): 简化查询逻辑`   | 否        |
| `perf`     | 性能优化        | `perf(db): 优化索引策略`        | Patch    |
| `test`     | 测试相关        | `test(chat): 添加单元测试`      | 否        |
| `chore`    | 构建/工具/依赖    | `chore(deps): 升级 FastAPI` | 否        |
| `ci`       | CI/CD 配置    | `ci(github): 添加自动发版流程`    | 否        |
| `revert`   | 回滚提交        | `revert: 回滚情绪模型更新`        | Patch    |


### 提交范围（Scope）

根据项目模块划分，推荐使用以下范围：

#### 后端范围

```bash
auth          # 认证授权模块
chat          # 聊天服务
emotion       # 情绪分析
crisis        # 危机干预
rating        # 评分反馈
monitoring    # 监控系统
db            # 数据库相关
cache         # 缓存（Redis）
api           # API 层
config        # 配置管理
```

#### 前端范围

```bash
frontend      # 前端通用
ui            # UI 组件
store         # 状态管理（Zustand）
api           # API 调用层
i18n          # 国际化
```

#### 基础设施范围

```bash
docker        # Docker 相关
ci            # CI/CD
deploy        # 部署配置
monitoring    # 监控配置
```

#### 示例

```bash
feat(chat): 新增多轮对话上下文管理
fix(emotion): 修复情绪识别准确率问题
perf(db): 优化聊天记录查询索引
docs(monitoring): 更新 Prometheus 配置说明
chore(docker): 更新基础镜像到 Python 3.13
ci(github): 配置 pre-commit hooks
```

### 特殊标记

#### Breaking Changes（破坏性变更）

```bash
feat(api)!: 重构认证接口

BREAKING CHANGE: /api/auth/login 接口响应格式变更
- 旧格式：{ "token": "xxx" }
- 新格式：{ "accessToken": "xxx", "refreshToken": "yyy" }
```

#### 关联 Issue

```bash
fix(chat): 修复消息重复发送问题

修复了在网络不稳定时消息可能重复发送的问题。

Closes #123
Fixes #124
Resolves #125
```

#### 多个范围

```bash
refactor(auth,chat): 统一异常处理逻辑
```

---

## CHANGELOG 更新规范

项目采用 **[Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)** 格式维护更新日志，记录每个版本的变更内容。

### 更新时机

#### 何时更新 CHANGELOG


| 场景        | 更新时机           | 负责人       |
| --------- | -------------- | --------- |
| 功能分支合并    | PR 合并后立即更新     | PR 作者     |
| Bug 修复合并  | PR 合并后立即更新     | PR 作者     |
| Hotfix 合并 | 合并到 main 后立即更新 | Hotfix 作者 |
| 版本发布      | 发版前统一检查和调整     | 发版负责人     |


#### 更新流程

```bash
# 1. 在功能分支上更新 CHANGELOG.md
git checkout feature/my-feature
# 编辑 CHANGELOG.md，在 [Unreleased] 下添加变更

# 2. 将 CHANGELOG 修改包含在 PR 中
git add CHANGELOG.md
git commit -m "docs(changelog): 记录新功能变更"
git push origin feature/my-feature

# 3. PR 合并后，CHANGELOG 自动合并到 develop/main
```

### 版本号规则

遵循 **[语义化版本 2.0.0](https://semver.org/lang/zh-CN/)**：

```
版本格式：Major.Minor.Patch（主版本号.次版本号.修订号）
```

#### 升级规则


| 变更类型               | 版本升级  | 示例            | 说明          |
| ------------------ | ----- | ------------- | ----------- |
| **破坏性变更**          | Major | 0.2.0 → 1.0.0 | 不兼容的 API 变更 |
| **新增功能** (`feat`)  | Minor | 0.1.0 → 0.2.0 | 向下兼容的功能性新增  |
| **Bug 修复** (`fix`) | Patch | 0.1.0 → 0.1.1 | 向下兼容的问题修复   |
| **性能优化** (`perf`)  | Patch | 0.1.0 → 0.1.2 | 向下兼容的性能提升   |
| 文档/测试/重构           | 不升级   | -             | 不影响用户的内部变更  |


#### 版本号示例

```bash
# 情况 1：新增功能
feat(chat): 新增聊天记录导出功能
→ 版本号：0.1.0 → 0.2.0

# 情况 2：Bug 修复
fix(auth): 修复 JWT 过期时间计算错误
→ 版本号：0.2.0 → 0.2.1

# 情况 3：破坏性变更
feat(api)!: 重构认证接口
BREAKING CHANGE: /api/auth/login 响应格式变更
→ 版本号：0.2.1 → 1.0.0

# 情况 4：仅文档更新
docs(readme): 更新部署说明
→ 版本号：不变（0.2.1）
```

### 分类标准

#### Keep a Changelog 标准分类


| 分类             | 中文  | 英文         | 适用变更          | 对应提交类型               |
| -------------- | --- | ---------- | ------------- | -------------------- |
| **Added**      | 新增  | Added      | 新功能、新特性       | `feat`               |
| **Changed**    | 修改  | Changed    | 现有功能的变更、重构、优化 | `refactor`, `perf`   |
| **Deprecated** | 废弃  | Deprecated | 即将移除的功能（预告）   | `feat` (带说明)         |
| **Removed**    | 移除  | Removed    | 已删除的功能        | `feat!` 或 `refactor` |
| **Fixed**      | 修复  | Fixed      | Bug 修复        | `fix`                |
| **Security**   | 安全  | Security   | 安全漏洞修复        | `fix` (标注安全)         |


#### 提交类型映射表


| 约定式提交类型    | CHANGELOG 分类 | 是否记录   | 示例                   |
| ---------- | ------------ | ------ | -------------------- |
| `feat`     | Added（新增）    | ✅ 是    | `feat(chat): 新增导出功能` |
| `fix`      | Fixed（修复）    | ✅ 是    | `fix(auth): 修复登录超时`  |
| `perf`     | Changed（修改）  | ✅ 是    | `perf(db): 优化查询索引`   |
| `refactor` | Changed（修改）  | ⚠️ 视情况 | 影响用户体验时记录            |
| `docs`     | -            | ❌ 否    | 文档更新不记录              |
| `test`     | -            | ❌ 否    | 测试相关不记录              |
| `chore`    | -            | ❌ 否    | 构建工具不记录              |
| `ci`       | -            | ❌ 否    | CI 配置不记录             |
| `style`    | -            | ❌ 否    | 代码格式不记录              |


### 编写原则

#### 1. 面向用户而非开发者

```markdown
# ❌ 不好的示例（过于技术化）
- 重构 ChatService 的 process_message 方法
- 将 Redis 连接池大小从 10 改为 20

# ✅ 好的示例（用户视角）
- 优化聊天响应速度，平均延迟从 2 秒降至 1 秒
- 提升系统并发处理能力，支持更多同时在线用户
```

#### 2. 分组相关变更

```markdown
### 新增 (Added)

**监控系统**：
- 集成 Prometheus + Grafana 监控体系
- 新增 9 个自定义指标（业务、性能、情绪分析）
- 部署 Grafana 预配置仪表板

**CI/CD 流程**：
- 新增 GitHub Actions 后端 CI 工作流
- 新增 GitHub Actions 前端 CI 工作流
```

#### 3. 突出重要变更

```markdown
### 修改 (Changed)

**⚠️ 重要变更**：
- 后端端口从 8000 改为 8200（需要更新前端配置）
- 认证令牌有效期从 24 小时缩短至 12 小时
```

#### 4. 关联 Issue 和 PR

```markdown
### 修复 (Fixed)

**情绪识别**：
- 修复空输入导致的崩溃问题 ([#156](https://github.com/org/emoagent/issues/156))
- 提升情绪识别准确率至 92% ([#142](https://github.com/org/emoagent/pull/142))
```

### 格式示例

#### 版本头部

```markdown
## [0.2.0] - 2026-03-13

### 新增 (Added)
- 变更内容 1
- 变更内容 2

### 修改 (Changed)
- 变更内容 1

### 修复 (Fixed)
- 变更内容 1

### 废弃 (Deprecated)
- 即将在 v1.0.0 中移除的功能

### 移除 (Removed)
- 已删除的旧功能

### 安全 (Security)
- 修复的安全漏洞
```

#### Unreleased 版本

```markdown
## [Unreleased]

### 新增 (Added)
- 待发布的新功能

### 修复 (Fixed)
- 待发布的 Bug 修复
```

**说明**：

- 开发过程中的变更先记录在 `[Unreleased]` 下
- 发版时将 `[Unreleased]` 改为版本号和日期
- 创建新的 `[Unreleased]` 章节用于下一版本

### 发版检查清单

发布新版本前，发版负责人需完成以下检查：

```markdown
## 发版前 CHANGELOG 检查清单

- [ ] 所有已合并的 PR 变更都已记录
- [ ] 版本号符合语义化版本规则
- [ ] 分类正确（Added/Changed/Fixed 等）
- [ ] 变更描述面向用户而非技术细节
- [ ] 重要变更已标注警告
- [ ] 关联了相关 Issue 和 PR 链接
- [ ] 发布日期正确（YYYY-MM-DD 格式）
- [ ] 已创建新的 [Unreleased] 章节
```

### 工具辅助（可选）

#### 基于 Git 历史生成草稿

```bash
# 查看自上次发版以来的所有提交
git log v0.1.0..HEAD --pretty=format:"%s" --no-merges

# 按类型分组
git log v0.1.0..HEAD --pretty=format:"%s" --no-merges | grep "^feat"
git log v0.1.0..HEAD --pretty=format:"%s" --no-merges | grep "^fix"

# 生成初始草稿（需人工调整）
```

#### 使用 conventional-changelog（可选）

如果团队规模较大，可考虑使用自动化工具生成草稿：

```bash
# 安装（需要 Node.js 环境）
npm install -g conventional-changelog-cli

# 生成草稿（基于约定式提交）
conventional-changelog -p angular -i CHANGELOG.md -s

# 注意：生成的内容需要人工审查和调整
```

### 常见错误

#### ❌ 错误示例

```markdown
# 1. 分类错误
### 新增
- 修复登录 bug  ← 应该在"修复"分类

# 2. 技术细节过多
### 修改
- 将 ChatService.process_message 的返回类型从 dict 改为 ChatResponse

# 3. 遗漏用户影响
### 修复
- 修复数据库索引  ← 缺少对用户的影响说明

# 4. 格式不一致
### Added
- 新增导出功能  ← 混用中英文标题
```

#### ✅ 正确示例

```markdown
### 修复 (Fixed)
- 修复登录页面在输入错误密码 3 次后无响应的问题

### 修改 (Changed)
- 优化聊天响应格式，提升前端渲染性能

### 修复 (Fixed)
- 修复聊天记录查询缓慢问题（从 5 秒优化至 0.5 秒）

### 新增 (Added)
- 新增聊天记录导出功能，支持 JSON 和 TXT 格式
```

---

## 工作流程

### 1. 开发新功能

```bash
# 1. 更新 develop 分支
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/chat-export

# 3. 开发功能（多次提交）
git add app/services/export_service.py
git commit -m "feat(chat): 添加聊天记录导出服务"

git add app/handlers/export_handler.py
git commit -m "feat(chat): 添加导出 API 端点"

git add tests/test_services/test_export_service.py
git commit -m "test(chat): 添加导出服务单元测试"

# 4. 推送到远程
git push -u origin feature/chat-export

# 5. 创建 Pull Request（见下文 PR 规范）

# 6. 合并后删除分支
git checkout develop
git pull origin develop
git branch -d feature/chat-export
git push origin --delete feature/chat-export
```

### 2. 修复 Bug

```bash
# 1. 从 develop 创建修复分支
git checkout develop
git pull origin develop
git checkout -b fix/emotion-crash

# 2. 修复问题并提交
git add app/services/emotion_service.py
git commit -m "fix(emotion): 修复空输入导致的崩溃

添加输入验证，防止空字符串传入 BERT 模型。

Fixes #156"

# 3. 添加测试用例
git add tests/test_services/test_emotion_service.py
git commit -m "test(emotion): 添加空输入测试用例"

# 4. 推送并创建 PR
git push -u origin fix/emotion-crash
```

### 3. 紧急修复生产问题

```bash
# 1. 从 main 创建 hotfix 分支
git checkout main
git pull origin main
git checkout -b hotfix/v0.2.1-llm-timeout

# 2. 修复问题
git add app/services/llm_service.py
git commit -m "fix(chat): 修复 LLM 超时导致服务挂起

增加超时时间至 30s，添加超时重试逻辑。

Fixes #178"

# 3. 推送并创建 PR（目标分支为 main）
git push -u origin hotfix/v0.2.1-llm-timeout

# 4. 合并到 main 后，同步到 develop
git checkout develop
git pull origin develop
git merge hotfix/v0.2.1-llm-timeout
git push origin develop
```

### 4. 同步上游更新

```bash
# 1. 在功能分支开发时，develop 有新提交
git checkout feature/my-feature
git fetch origin

# 2. 变基到最新的 develop（保持线性历史）
git rebase origin/develop

# 3. 如果有冲突，解决后继续
git add <resolved-files>
git rebase --continue

# 4. 强制推送（变基后）
git push --force-with-lease origin feature/my-feature
```

---

## Pull Request 规范

### PR 标题格式

遵循约定式提交格式：

```
feat(chat): 新增聊天记录导出功能
fix(auth): 修复 JWT 过期时间计算错误
docs(deployment): 更新 Docker 部署流程
```

### PR 描述模板

创建 `.github/pull_request_template.md`：

```markdown
## 变更类型
- [ ] 新功能（feat）
- [ ] Bug 修复（fix）
- [ ] 文档更新（docs）
- [ ] 重构（refactor）
- [ ] 性能优化（perf）
- [ ] 测试（test）
- [ ] 构建/工具（chore）

## 变更说明
<!-- 简要描述本次变更的内容和动机 -->

### 主要变更
- 变更 1
- 变更 2

### 影响范围
<!-- 哪些模块受到影响 -->
- [ ] 后端 API
- [ ] 前端界面
- [ ] 数据库结构
- [ ] 配置文件
- [ ] CI/CD

## 测试
<!-- 如何测试本次变更 -->

### 测试步骤
1. 步骤 1
2. 步骤 2

### 测试结果
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 相关 Issue
<!-- 关联的 Issue 编号 -->
Closes #<issue-number>

## 截图/录屏
<!-- 如果涉及 UI 变更，请提供截图或录屏 -->

## 检查清单
- [ ] 代码遵循项目规范（black/isort/eslint）
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有 CI 检查
- [ ] 提交信息符合约定式提交规范
```

### PR 审查流程

#### 提交者职责

1. 确保 CI 全部通过
2. 自我审查代码（Code Self-Review）
3. 补充必要的测试和文档
4. 解决审查意见后及时通知审查者

#### 审查者职责

1. 检查代码质量和规范
2. 验证功能是否符合需求
3. 评估性能和安全性
4. 检查测试覆盖率
5. 审查文档完整性

#### 审查标准

```
Approve - 无问题，可以合并
Comment - 有建议，但不阻塞合并
Request Changes - 有问题，需要修改后重新审查
```

### 合并策略

#### 合并方式

```bash
# 推荐：Squash and Merge（功能分支）
# - 将多个提交压缩为一个
# - 保持 main/develop 历史简洁

# 保留：Merge Commit（hotfix、release）
# - 保留完整提交历史
# - 明确标记合并点

# 禁止：Rebase and Merge（除非有特殊需求）
```

#### GitHub 配置

```
Settings → Branches → Branch protection rules (main):
• Require a pull request before merging
• Require approvals (1)
• Require status checks to pass before merging
  • Backend CI
  • Frontend CI
• Require conversation resolution before merging
• Allow squash merging (推荐)
• Allow merge commits
• Allow rebase merging
```

---

## CI/CD 集成

### 触发 CI 检查

项目配置了自动化 CI 流程，在以下情况触发：

#### 后端 CI（`.github/workflows/backend-ci.yml`）

**触发条件**：

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'app/**'
      - 'tests/**'
      - 'requirements.txt'
      - 'alembic/**'
      - '.github/workflows/backend-ci.yml'
  pull_request:
    branches: [main]
```

**检查项目**：

1. 代码格式检查（black、isort）
2. 类型检查（mypy）
3. 单元测试（pytest）
4. 测试覆盖率报告

**通过标准**：

- 所有格式检查通过
- 类型检查无错误
- 测试覆盖率 ≥ 80%

#### 前端 CI（`.github/workflows/frontend-ci.yml`）

**触发条件**：

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [main]
```

**检查项目**：

1. ESLint 检查
2. TypeScript 类型检查
3. 单元测试（vitest）
4. 构建验证

**通过标准**：

- 无 ESLint 错误（警告允许）
- TypeScript 编译通过
- 所有测试通过

### 跳过 CI 检查

在极少数情况下（如仅修改文档），可以跳过 CI：

```bash
# 在提交信息中添加 [skip ci] 或 [ci skip]
git commit -m "docs: 更新 README [skip ci]"
```

**注意**：跳过 CI 不会绕过 PR 的必填检查。

### CI 失败处理

#### 1. 查看失败原因

```bash
# 访问 GitHub Actions 页面
https://github.com/<your-org>/emoagent-v1/actions

# 点击失败的工作流查看日志
```

#### 2. 本地复现问题

```bash
# 后端格式检查
black --check app/ tests/
isort --check-only app/ tests/
mypy app/ --ignore-missing-imports

# 运行测试
pytest tests/ -v

# 前端检查
cd frontend
npm run lint
npx tsc --noEmit
npm run test
npm run build
```

#### 3. 修复并重新推送

```bash
# 修复代码
black app/ tests/
isort app/ tests/

# 提交修复（使用 fixup 保持提交历史清晰）
git add .
git commit -m "fix(ci): 修复代码格式问题"
git push origin feature/my-feature
```

### 本地预检查

在推送前本地运行 CI 检查，避免触发无效构建：

#### 后端预检查脚本

```bash
#!/bin/bash
# scripts/pre-push-backend.sh

echo "Running backend CI checks locally..."

echo "Checking code format (black)..."
black --check app/ tests/ || exit 1

echo "Checking import sorting (isort)..."
isort --check-only app/ tests/ || exit 1

echo "Running type check (mypy)..."
mypy app/ --ignore-missing-imports || exit 1

echo "Running tests (pytest)..."
pytest tests/ --cov=app --cov-report=term -v || exit 1

echo "All checks passed!"
```

#### 前端预检查脚本

```bash
#!/bin/bash
# scripts/pre-push-frontend.sh

echo "Running frontend CI checks locally..."

cd frontend

echo "Running ESLint..."
npm run lint || exit 1

echo "Running TypeScript check..."
npx tsc --noEmit || exit 1

echo "Running tests..."
npm run test || exit 1

echo "Testing build..."
npm run build || exit 1

echo "All checks passed!"
```

#### 使用方式

```bash
# 推送前运行
bash scripts/pre-push-backend.sh
bash scripts/pre-push-frontend.sh

# 通过后再推送
git push origin feature/my-feature
```

---

## 常见场景

### 场景 1：如何撤销已推送的提交？

```bash
# 方式 1：使用 revert（推荐，安全）
git revert <commit-hash>
git push origin feature/my-feature

# 方式 2：使用 reset（需要强制推送，谨慎使用）
git reset --hard HEAD~1
git push --force-with-lease origin feature/my-feature
```

**注意**：永远不要在 `main` 或 `develop` 上使用 `git push --force`！

### 场景 2：如何修改最后一次提交？

```bash
# 修改提交信息
git commit --amend -m "feat(chat): 新增导出功能（修正拼写错误）"

# 添加遗漏的文件
git add forgotten-file.py
git commit --amend --no-edit

# 推送修改（功能分支可以使用）
git push --force-with-lease origin feature/my-feature
```

### 场景 3：如何合并多个提交？

```bash
# 交互式变基
git rebase -i HEAD~3

# 在编辑器中将后续提交改为 squash 或 fixup
# pick a1b2c3d feat(chat): 添加导出服务
# squash d4e5f6g feat(chat): 修复导出格式
# squash g7h8i9j feat(chat): 优化导出性能

# 保存后推送
git push --force-with-lease origin feature/my-feature
```

### 场景 4：如何解决合并冲突？

```bash
# 1. 更新 develop 分支
git checkout develop
git pull origin develop

# 2. 切换到功能分支并合并
git checkout feature/my-feature
git merge develop

# 3. 解决冲突
# 编辑冲突文件，手动合并
git add <resolved-files>
git commit -m "merge: 解决与 develop 的合并冲突"

# 4. 推送
git push origin feature/my-feature
```

### 场景 5：如何暂存当前工作切换分支？

```bash
# 暂存当前工作
git stash save "WIP: 聊天导出功能开发中"

# 切换分支处理其他任务
git checkout hotfix/urgent-fix
# ... 处理紧急问题 ...

# 回到原分支恢复工作
git checkout feature/chat-export
git stash pop
```

### 场景 6：如何查看某次提交的详细变更？

```bash
# 查看提交日志
git log --oneline --graph --decorate

# 查看具体提交的变更
git show <commit-hash>

# 查看某个文件的历史
git log -p -- app/services/chat_service.py
```

---

## 最佳实践

### DO（推荐做法）

#### 1. 提交粒度适中

```bash
# 好的示例：每个提交专注一个变更
git commit -m "feat(chat): 添加消息导出服务"
git commit -m "test(chat): 添加导出服务单元测试"
git commit -m "docs(api): 更新导出接口文档"

# 坏的示例：一个提交包含多个不相关的变更
git commit -m "feat: 添加导出功能，修复登录 bug，更新文档"
```

#### 2. 提交信息清晰描述

```bash
# 好的示例：清晰说明做了什么和为什么
git commit -m "fix(emotion): 修复空输入导致的崩溃

添加输入验证，防止空字符串传入 BERT 模型。
此问题在生产环境触发了 3 次，影响了用户体验。

Fixes #156"

# 坏的示例：信息模糊
git commit -m "fix bug"
git commit -m "update code"
git commit -m "wip"
```

#### 3. 频繁同步上游

```bash
# 每天同步一次 develop，避免大量冲突
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
```

#### 4. 使用 Git Hooks 自动化检查

创建 `.git/hooks/pre-commit`（可选）：

```bash
#!/bin/bash
# 提交前自动格式化代码

# 后端格式化
if git diff --cached --name-only | grep -q "^app/\|^tests/"; then
    echo "Auto-formatting Python code..."
    black $(git diff --cached --name-only | grep "\.py$")
    isort $(git diff --cached --name-only | grep "\.py$")
    git add $(git diff --cached --name-only | grep "\.py$")
fi

# 前端格式化
if git diff --cached --name-only | grep -q "^frontend/"; then
    echo "Auto-formatting frontend code..."
    cd frontend
    npm run format
    cd ..
fi
```

#### 5. 及时删除已合并的分支

```bash
# 本地删除
git branch -d feature/completed-feature

# 远程删除
git push origin --delete feature/completed-feature

# 批量清理已合并的本地分支
git branch --merged develop | grep -v "\* develop" | xargs -n 1 git branch -d
```

### DON'T（避免做法）

#### 1. 不要直接提交到 main/develop

```bash
# 坏的做法
git checkout main
git add .
git commit -m "feat: 新功能"
git push origin main

# 正确做法：创建功能分支 + PR
git checkout -b feature/new-feature
git add .
git commit -m "feat(chat): 新增功能"
git push origin feature/new-feature
# 然后创建 Pull Request
```

#### 2. 不要使用 `git push --force` 在共享分支

```bash
# 危险！会覆盖其他人的提交
git checkout main
git reset --hard HEAD~5
git push --force origin main

# 正确做法：仅在个人功能分支使用 --force-with-lease
git checkout feature/my-feature
git rebase -i HEAD~3
git push --force-with-lease origin feature/my-feature
```

#### 3. 不要提交敏感信息

```bash
# 永远不要提交这些文件
.env                    # 包含 API Key、数据库密码
credentials.json        # 凭证文件
*.pem / *.key          # 私钥文件
config/secrets.yaml     # 密钥配置

# 确保这些文件在 .gitignore 中
echo ".env" >> .gitignore
echo "*.pem" >> .gitignore
git add .gitignore
git commit -m "chore: 更新 gitignore"
```

#### 4. 不要提交超大文件

```bash
# 避免提交这些文件
models/*.bin           # BERT 模型文件（使用 Git LFS 或外部存储）
*.mp4 / *.mov         # 视频文件
*.zip / *.tar.gz      # 压缩包

# 使用 Git LFS（Large File Storage）
git lfs install
git lfs track "*.bin"
git add .gitattributes
git commit -m "chore: 配置 Git LFS"
```

#### 5. 不要忽略 CI 失败

```bash
# 坏的做法：CI 失败后强行合并
# 这会引入潜在 bug 和技术债务

# 正确做法：修复 CI 失败后再合并
# 1. 本地复现问题
# 2. 修复问题
# 3. 重新推送
# 4. 等待 CI 通过
# 5. 再合并 PR
```

---

## 快速参考

### 常用命令速查

```bash
# 分支管理
git checkout -b feature/my-feature        # 创建并切换到新分支
git branch -d feature/completed           # 删除已合并分支
git push origin --delete feature/old      # 删除远程分支

# 提交管理
git commit -m "feat(chat): 新增功能"      # 约定式提交
git commit --amend --no-edit              # 修改最后一次提交
git revert <commit-hash>                  # 撤销某次提交

# 同步更新
git fetch origin                          # 获取远程更新
git pull origin develop                   # 拉取并合并
git rebase origin/develop                 # 变基到最新 develop

# 暂存工作
git stash save "WIP: 功能开发中"          # 暂存当前工作
git stash pop                             # 恢复暂存的工作
git stash list                            # 查看暂存列表

# 查看历史
git log --oneline --graph                 # 简洁日志
git log --grep="feat"                     # 搜索提交信息
git show <commit-hash>                    # 查看提交详情
```

### 提交类型速查


| 场景     | 类型         | 示例                        |
| ------ | ---------- | ------------------------- |
| 新增功能   | `feat`     | `feat(chat): 新增导出功能`      |
| 修复 Bug | `fix`      | `fix(auth): 修复登录超时`       |
| 文档更新   | `docs`     | `docs(api): 更新接口文档`       |
| 性能优化   | `perf`     | `perf(db): 优化查询索引`        |
| 代码重构   | `refactor` | `refactor(dao): 简化查询逻辑`   |
| 添加测试   | `test`     | `test(chat): 添加单元测试`      |
| 依赖升级   | `chore`    | `chore(deps): 升级 FastAPI` |
| CI 配置  | `ci`       | `ci: 添加自动发版流程`            |


### CI 触发路径


| 变更文件               | 触发 CI       |
| ------------------ | ----------- |
| `app/**/*.py`      | Backend CI  |
| `tests/**/*.py`    | Backend CI  |
| `requirements.txt` | Backend CI  |
| `frontend/**/*`    | Frontend CI |
| `docs/**/*.md`     | 无 CI        |
| `README.md`        | 无 CI        |


---

## 附录：辅助工具

> **注意**：本节内容为非强制性的辅助工具推荐，开发者可根据个人习惯和团队需求选择性使用。

### A. Git 别名配置

在 `~/.gitconfig` 中添加常用别名可以提升命令行效率：

```ini
[alias]
    # 日志美化
    lg = log --graph --oneline --decorate --all
    lga = log --graph --oneline --decorate --all --author
    
    # 快捷命令
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    
    # 约定式提交快捷方式
    feat = "!f() { git commit -m \"feat: $1\"; }; f"
    fix = "!f() { git commit -m \"fix: $1\"; }; f"
    docs = "!f() { git commit -m \"docs: $1\"; }; f"
    
    # 清理已合并分支
    cleanup = "!git branch --merged develop | grep -v '\\* develop' | xargs -n 1 git branch -d"
```

**使用示例**：

```bash
git lg                           # 美化的日志
git feat "新增聊天导出功能"      # 快速创建 feat 提交
git cleanup                      # 清理已合并分支
```

### B. VS Code 扩展推荐

以下扩展可以帮助可视化 Git 操作和自动化约定式提交：

- **Conventional Commits**（`vivaxy.vscode-conventional-commits`）
  - 提供约定式提交格式提示
  - 图形化界面选择类型和范围
- **GitLens**（`eamodio.gitlens`）
  - 可视化 Git 历史
  - 查看每行代码的提交信息
- **Git Graph**（`mhutchie.git-graph`）
  - 图形化分支历史
  - 可视化合并和冲突

### C. Commitizen 工具

适合需要严格约定式提交格式的团队：

```bash
# 全局安装
npm install -g commitizen cz-conventional-changelog

# 配置
echo '{"path": "cz-conventional-changelog"}' > ~/.czrc

# 使用（替代 git commit）
git cz
```

**交互式界面示例**：

```
? Select the type of change that you're committing: (Use arrow keys)
❯ feat:     A new feature
  fix:      A bug fix
  docs:     Documentation only changes
  style:    Changes that do not affect the meaning of the code
  refactor: A code change that neither fixes a bug nor adds a feature
  perf:     A code change that improves performance
  test:     Adding missing tests
```

---

## 相关文档

- [开发指南](DEVELOPMENT.md) - 本地开发环境搭建
- [部署文档](DEPLOYMENT.md) - CI/CD 集成和部署流程
- [测试指南](TESTING.md) - 测试策略和覆盖率要求
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) - CHANGELOG 编写规范
- [Conventional Commits](https://www.conventionalcommits.org/) - 约定式提交规范

---

**文档版本**: v1.1.0  
**创建日期**: 2026-03-13  
**最后更新**: 2026-03-24  
**维护者**: 全体开发团队