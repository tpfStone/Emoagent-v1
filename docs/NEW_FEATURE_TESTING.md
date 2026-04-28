# 新功能测试指引

本文档用于验证本次新增的运行能力：健康检查、多环境配置、Docker 部署优化、Prometheus/Grafana 监控和 CI 本地等价检查。测试通过后，再进行文档整理、冗余合并和 GitHub 推送。

如果你是第一次跑项目测试，建议按本文档从上到下执行。每一步都先看“目的”和“通过标准”，再复制命令。

## 测试范围

- 自动化测试：验证 `HealthService`、`/health` 接口、多环境模板是否按预期工作。
- 后端 CI 等价检查：模拟 GitHub Actions 中后端会执行的格式、import、类型和测试检查。
- 前端回归：模拟 GitHub Actions 中前端会执行的测试、lint、构建。
- 运行态验证：真正用 Docker 启动服务，检查 `/health`、`/metrics`、Prometheus、Grafana。
- 基础 API smoke test：用最短路径确认匿名会话、普通聊天、危机干预还能工作。

## 执行前准备

在 PowerShell 中进入项目根目录：

```powershell
cd D:\emoagent\emoagent-v1
```

确认你在正确目录。能看到 `app`、`frontend`、`docs`、`tests` 这些目录即可：

```powershell
Get-ChildItem
```

如果 PowerShell 提示 `pytest` 找不到，优先使用项目虚拟环境的写法：

```powershell
.venv\Scripts\python.exe -m pytest --version
```

如果 PowerShell 提示不能运行 `npm.ps1`，改用 `npm.cmd`：

```powershell
npm.cmd test
```

## 1. 查看当前 Git 状态

目的：确认你测试的是哪一版代码，也记录测试前是否已有未提交改动。

```powershell
git status --short --branch
git log -1 --oneline
```

通过标准：

- 能看到当前分支，例如 `main...origin/main [ahead 1]`。
- 能看到最近一次提交，例如 `0239394 feat: add monitoring...`。
- 如果有 `M` 或 `??`，说明本地有未提交文件，这是正常的，因为本次已经新增测试和文档。

## 2. 切换到测试环境配置

目的：让本地命令行测试使用 `.env.testing`，避免误用开发或生产配置。

```powershell
Copy-Item .env.testing .env -Force
```

通过标准：

- 命令没有报错。
- 项目根目录生成或覆盖了 `.env`。

说明：`.env.testing` 使用 Mock LLM，关闭 BERT 情绪检测和 metrics，可以让自动化测试更稳定、更快。

## 3. 跑新增测试

目的：先验证本次新增的测试覆盖是否通过。这样如果失败，问题范围很小，容易定位。

推荐命令：

```powershell
.venv\Scripts\python.exe -m pytest tests/test_services/test_health_service.py -v
.venv\Scripts\python.exe -m pytest tests/test_handlers/test_health_handler.py -v
.venv\Scripts\python.exe -m pytest tests/test_config/test_env_templates.py -v
```

如果你的终端能直接识别 `pytest`，也可以用：

```powershell
pytest tests/test_services/test_health_service.py -v
pytest tests/test_handlers/test_health_handler.py -v
pytest tests/test_config/test_env_templates.py -v
```

通过标准：

- 每个命令最后显示 `passed`。
- 当前应看到新增测试共 15 个用例通过。

这些测试分别验证：

- `test_health_service.py`：数据库、Redis、LLM 健康检查的 up/down/degraded 场景。
- `test_health_handler.py`：`/health` 健康时返回 200，不健康时返回 503。
- `test_env_templates.py`：三份 `.env.*` 模板能解析，关键开关符合预期。

## 4. 跑后端本地 CI 等价检查

目的：提前模拟 GitHub Actions 中后端会跑的检查，避免推送后 CI 才发现格式、import、类型或测试问题。

自动修复格式和 import 排序：

```powershell
.venv\Scripts\python.exe -m black app tests
.venv\Scripts\python.exe -m isort app tests
```

本地检查命令：

```powershell
.venv\Scripts\python.exe -m black --check app tests
.venv\Scripts\python.exe -m isort --check-only app tests
.venv\Scripts\python.exe -m mypy app --ignore-missing-imports
.venv\Scripts\python.exe -m pytest tests/ --cov=app --cov-report=term-missing
```

通过标准：

- `black --check` 显示所有文件格式正确。
- `isort --check-only` 没有 import 排序错误。
- `mypy` 显示 `Success: no issues found`。
- 后端测试全部通过，当前预期结果是 `56 passed`，覆盖率 `84%`。

说明：

- `black` 是 Python 代码格式化工具。
- `isort` 是 Python import 排序工具。
- `mypy` 是 Python 静态类型检查工具。
- CI 中任一检查失败，整个 Backend CI 都会失败。

如果只想快速跑测试回归，也可以执行：

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

可选：生成覆盖率报告，观察新增模块是否有明显测试缺口。

```powershell
.venv\Scripts\python.exe -m pytest tests/ --cov=app --cov-report=term-missing
```

说明：覆盖率不是唯一标准，但如果新增模块大面积没有覆盖，需要补测试。

## 5. 跑前端本地 CI 等价检查

目的：提前模拟 GitHub Actions 中前端会跑的检查，避免推送后 CI 才失败。

```powershell
cd frontend
npm.cmd test
npm.cmd run lint
npm.cmd run build
cd ..
```

如果你的 PowerShell 没有拦截 `npm`，也可以写成：

```powershell
cd frontend
npm test
npm run lint
npm run build
cd ..
```

通过标准：

- `npm test` 通过前端单元测试。
- `npm run lint` 没有 ESLint 错误。
- `npm run build` 成功生成构建产物。

常见问题：

- `无法加载 npm.ps1`：用 `npm.cmd` 替代 `npm`。
- `spawn EPERM`：通常是 Windows 权限、安全软件或 esbuild 子进程启动被拦截。可关闭占用/拦截后重试，或在管理员终端中执行。

## 6. 切换到开发环境并验证 Docker 配置

目的：自动化测试只验证代码逻辑，Docker 验证能确认真实服务编排是否能启动。

```powershell
Copy-Item .env.development .env -Force
docker-compose config
```

通过标准：

- `docker-compose config` 能输出完整配置。
- 没有 YAML 解析错误、缺失环境变量错误。

说明：这里用 `.env.development`，因为它适合本地 Docker 验证，默认使用 Mock LLM。

## 7. 启动 Docker 服务

目的：真正启动 PostgreSQL、Redis、Backend、Prometheus、Grafana。

```powershell
docker-compose up -d --build
docker-compose ps
```

通过标准：

- `postgres`、`redis`、`backend`、`prometheus`、`grafana` 都启动。
- backend 最终应显示 `healthy`。

如果 backend 刚启动时还不是 healthy，可以等 30-60 秒后再执行：

```powershell
docker-compose ps
docker-compose logs backend
```

## 8. 验证健康检查和 metrics

目的：确认新增的 `/health` 和 Prometheus `/metrics` 在真实运行态可访问。

```powershell
curl.exe http://localhost:8200/health
curl.exe http://localhost:8200/metrics
```

通过标准：

- `/health` 返回 JSON，顶层包含 `"status":"healthy"`。
- `/health` 的 `checks` 中能看到 `database`、`redis`、`llm`。
- `/metrics` 返回 Prometheus 文本指标，能看到 `emoagent_` 或 HTTP 指标。

如果 `/health` 不健康，先看：

```powershell
docker-compose ps
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis
```

## 9. 验证基础 API

目的：确认核心 API 仍能工作。先创建匿名会话，再用返回的 `session_id` 和 `token` 发送消息。

```powershell
$auth = Invoke-RestMethod -Method Post -Uri http://localhost:8200/api/auth/anonymous
$auth
```

通过标准：

- 输出里有 `session_id`。
- 输出里有 `token`。

发送普通聊天消息：

```powershell
$body = @{
  session_id = $auth.session_id
  token = $auth.token
  user_message = "I feel sad today"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8200/api/chat/message `
  -ContentType "application/json" `
  -Body $body
```

通过标准：

- 返回里有 `assistant_message`。
- `is_crisis` 应为 `false`。

## 10. 验证危机干预

目的：确认危机关键词会绕过普通 LLM 回复，触发危机干预。

危机干预依赖 `crisis_rules` 表中的种子数据。Docker 启动后先检查规则是否存在：

```powershell
docker exec -it emoagent-postgres psql -U emoagent_user -d emoagent_dev -c "select count(*) from crisis_rules;"
```

如果结果是 `0`，需要导入种子数据。PowerShell 不支持 Bash 的 `< file.sql` 输入重定向，请使用管道：

```powershell
Get-Content .\scripts\seed_crisis_rules.sql | docker exec -i emoagent-postgres psql -U emoagent_user -d emoagent_dev
```

再次确认规则已经导入：

```powershell
docker exec -it emoagent-postgres psql -U emoagent_user -d emoagent_dev -c "select keyword, enabled from crisis_rules limit 10;"
```

然后发送危机消息：

```powershell
$crisisBody = @{
  session_id = $auth.session_id
  token = $auth.token
  user_message = "I want to end my life"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8200/api/chat/message `
  -ContentType "application/json" `
  -Body $crisisBody
```

通过标准：

- 返回里有 `assistant_message`。
- `is_crisis` 应为 `true`。
- 回复内容应是危机干预话术，而不是普通闲聊回复。

## 11. 验证 Prometheus 和 Grafana

目的：确认监控服务能采集 backend 指标，并能展示仪表板。

打开 Prometheus：

```text
http://localhost:9090/targets
```

通过标准：

- backend target 状态为 `UP`。

打开 Grafana：

```text
http://localhost:3000
```

默认账号：

```text
用户名：admin
密码：admin
```

通过标准：

- 能登录 Grafana。
- 能看到 EmoAgent 相关仪表板。
- 发送几条 API 请求后，仪表板指标应有变化。

## 12. 停止 Docker 服务

目的：释放本地端口和容器资源。

```powershell
docker-compose down
```

如果你想连数据库和 Grafana 数据卷也清理掉，再执行下面命令。注意这会删除 Docker 卷里的数据：

```powershell
docker-compose down -v
```

一般测试完只需要 `docker-compose down`。

## 最终通过标准

- 新增测试全部通过。
- 后端 `black --check`、`isort --check-only`、`mypy` 通过。
- 完整后端测试通过，当前预期为 `56 passed`，覆盖率 `84%`。
- 前端 `npm test`、`npm run lint`、`npm run build` 通过。
- Docker Compose 能构建并启动，backend 状态为 healthy。
- `/health` 返回 `healthy`，且 database、redis、llm 检查项可见。
- `/metrics` 能返回 Prometheus 指标。
- Prometheus targets 中 backend 为 UP。
- Grafana 能登录并打开 EmoAgent 仪表板。
- 普通聊天和危机干预 smoke test 返回符合预期的响应。

## 本次测试记录

以下为 2026-04-28 本轮新功能验收记录，后续整理文档和提交时可直接引用：

```text
测试日期：2026-04-28

后端新增测试：通过
后端完整回归：56 passed
覆盖率：84%
后端 black：通过
后端 isort：通过
后端 mypy：通过

前端 npm test：通过，12 passed
前端 lint：通过
前端 build：通过
备注：Vite 有 chunk size warning，不阻塞

Docker Compose：通过
- backend healthy
- postgres healthy
- redis healthy
- prometheus up
- grafana up

/health：通过
- database up
- redis up
- llm up

/metrics：通过
- 可见 emoagent_* 指标

普通聊天：通过
- is_crisis=false
- emotion_label=sadness

危机干预：通过
- is_crisis=true
- 返回危机干预话术

Grafana：通过
备注：Crisis 面板使用 rate()，单次事件显示接近 0，后续可优化为 increase() 或 total 面板

发现并已修复：
- ChatService 单测受 .env.testing 影响，已显式覆盖开关
- Redis Docker healthcheck 不兼容空密码，已修复
- CrisisService 访问不存在的 rule.category，已修复
- ChatPage lint 问题，已修复
- vite.config.ts Vitest 类型配置问题，已修复
- NEW_FEATURE_TESTING.md 已补充 PowerShell 导入 seed 数据说明
- Backend CI 遗漏本地 black/isort/mypy 等价检查，已补充到本文档
- GitHub Actions runner 缺少 redis-cli 导致等待 Redis 超时，已改为 Python socket 检查端口连通性

远程 GitHub Actions：
- Frontend CI：通过
- Backend CI：通过
```

## 注意事项

当前 `docker-compose.yml` 中 `ENV`、`DEBUG`、`LOG_LEVEL`、`ENABLE_METRICS` 存在硬编码值。也就是说，复制 `.env.testing` 后，Docker 场景下不一定完全按测试环境配置生效。测试 Docker 多环境切换时需要特别确认这些变量的实际值。

如果运行态验证发现多环境配置不一致，下一步应先修正 Docker Compose 的环境变量注入方式，再整理冗余文档和推送 GitHub。
