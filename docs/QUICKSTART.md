# 本地部署验证 & Git 推送 —— 新手操作指南

> **前置说明**：i18n 多语言改造已全部完成（代码 + 测试 + 文档），下面的内容是"部署验证 → 推送仓库"的完整操作流程。

---

## 你需要准备的东西


| 工具                     | 用途                        | 是否已有 |
| ---------------------- | ------------------------- | ---- |
| **Docker Desktop**     | 运行 PostgreSQL 和 Redis 数据库 | 需要安装 |
| **Python 3.13**        | 后端运行环境                    | 已安装  |
| **Node.js + npm**      | 前端运行环境                    | 已安装  |
| **Git**                | 版本控制和代码推送                 | 需要确认 |
| **VS Code / Cursor**   | 编辑配置文件                    | 已安装  |
| **浏览器**（Chrome / Edge） | 测试前端页面                    | 已安装  |


---

## 你需要打开几个终端窗口？

整个过程中你需要 **3 个终端窗口**（在 Cursor 底部点击 `+` 新建终端）：

- **终端 1**：运行 Docker 命令、数据库操作、Git 操作
- **终端 2**：运行后端服务（会一直占用这个窗口）
- **终端 3**：运行前端服务（会一直占用这个窗口）

---

## Step 0: 安装并启动 Docker Desktop

### 什么是 Docker？

Docker 是一个"容器"工具，可以帮你一键安装数据库（PostgreSQL、Redis），不需要你手动配置。类似于一个自带环境的虚拟机，但更轻量。

### 操作步骤

1. 打开浏览器，访问 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. 点击 **Download for Windows** 下载安装包
3. 双击安装包，按提示安装（全部选默认即可）
4. 安装完成后会提示重启电脑，**重启**
5. 重启后，Docker Desktop 会自动启动（桌面右下角托盘区出现鲸鱼图标）
6. 等待 Docker Desktop 界面显示 **"Docker Desktop is running"**（可能需要 1-2 分钟）

### 如何验证安装成功？

在 Cursor 底部打开终端（快捷键 `Ctrl + ~`），输入：

```
docker --version
```

如果看到类似 `Docker version 27.x.x` 的输出，说明安装成功。

> **常见问题**：如果提示 "WSL 2 is not installed"，按照弹窗指引安装 WSL 2，然后重启电脑。

---

## Step 1: 复制并编辑环境变量 .env 文件

### 什么是 .env 文件？

`.env` 文件存储数据库密码、API 密钥等配置信息。项目中有一个模板文件 `.env.example`，你需要复制它并填入实际的值。

### 操作步骤

在**终端 1** 中，先进入项目根目录（替换为你自己的实际路径）：

```
cd /d <你的项目路径>\emoagent-v1
```

然后复制模板文件：

```
copy .env.example .env
```

接下来用 Cursor 打开 `.env` 文件进行编辑。你只需要修改以下几项（其余保持默认）：

```ini
# ===== 必须修改的配置 =====

# 数据库密码：把 your_secure_password 改成你自己设的密码（比如 MyPass123!）
# 注意：下面两处的密码必须一致！
DATABASE_URL=postgresql://emoagent_user:MyPass123!@localhost:5432/emoagent
POSTGRES_PASSWORD=MyPass123!

# ===== 建议修改的配置 =====

# 保持 true 以启用 BERT 情绪检测模型（首次调用时自动下载，约 400MB）
# 第一次发送聊天消息时终端会显示 "Loading BERT model..."，下载完成后显示 "BERT model loaded successfully"
ENABLE_EMOTION_DETECTION=true

# ===== 不需要改的配置（保持默认即可） =====
# POSTGRES_USER=emoagent_user        ← 保持默认
# POSTGRES_DB=emoagent               ← 保持默认
# LLM_PROVIDER=mock                  ← 保持 mock，用模拟 AI 回复
# REDIS_PASSWORD=                    ← 留空即可
```

> **重要提醒**：
>
> - `DATABASE_URL` 中的密码和 `POSTGRES_PASSWORD` 必须**完全一致**
> - 密码不要包含 `@`、`#`、`%` 等特殊字符，可能导致连接失败
> - `.env` 文件不要提交到 Git（后面配置 `.gitignore` 时会排除它）

---

## Step 2: 用 Docker 启动 PostgreSQL 和 Redis

### 这一步在做什么？

启动两个数据库容器：

- **PostgreSQL**：存储用户会话、聊天记录、评分等数据
- **Redis**：缓存短期对话记忆，加快响应速度

### 操作步骤

在**终端 1** 中执行：

```
docker-compose up -d postgres redis
```

> **参数解释**：
>
> - `up`：启动服务
> - `-d`：后台运行（detached 模式），不会占用终端
> - `postgres redis`：只启动这两个服务，不启动 backend（我们手动启动后端，方便调试）

第一次执行时 Docker 会下载 PostgreSQL 和 Redis 的镜像（约 200MB），需要等待几分钟。

### 如何验证启动成功？

执行以下命令查看容器状态：

```
docker-compose ps
```

你应该看到类似这样的输出：

```
NAME                STATUS
emoagent-postgres   Up xx seconds (healthy)
emoagent-redis      Up xx seconds (healthy)
```

**关键看**：两个容器的状态都是 `healthy`。如果显示 `starting` 或 `unhealthy`，等 30 秒再执行一次 `docker-compose ps` 检查。

> **如果启动失败**：
>
> - 检查 Docker Desktop 是否正在运行（右下角托盘有鲸鱼图标）
> - 检查 5432 和 6379 端口是否被其他程序占用
> - 尝试 `docker-compose down` 然后重新 `docker-compose up -d postgres redis`

---

## Step 3: 执行数据库迁移和导入种子数据

### 这一步在做什么？

- **数据库迁移**：根据代码中的模型定义，在 PostgreSQL 中创建表（sessions、turns、ratings 等）
- **种子数据**：导入危机干预规则（关键词 + 应急话术），这样系统才能识别危机情况

### 操作步骤

继续在**终端 1** 中执行（确保在项目根目录）：

**第一步：安装 Python 依赖**（如果之前没装过）

```
pip install -r requirements.txt
```

**第二步：执行数据库迁移（建表）**

```
python -m alembic upgrade head
```

成功时你会看到类似输出：

```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, initial schema
```

> **如果报错 "Connection refused"**：说明 `.env` 中的数据库配置和 Docker 容器不匹配，回到 Step 1 检查密码是否一致。

**第三步：导入危机干预规则种子数据**

```
docker exec -i emoagent-postgres psql -U emoagent_user -d emoagent -f /dev/stdin < scripts\seed_crisis_rules.sql
```

> 如果上面的命令报错，可以换一种方式：先把 SQL 内容复制，然后在 Docker 容器里执行：

```
> docker exec -it emoagent-postgres psql -U emoagent_user -d emoagent
> 

```

> 这会打开 PostgreSQL 命令行（显示 `emoagent=#` 提示符），然后粘贴 `scripts\seed_crisis_rules.sql` 文件的内容，按回车执行。输入 `\q` 退出。

---

## Step 4: 启动后端服务

### 操作步骤

在**终端 2**（新开一个终端）中执行：

```
cd /d <你的项目路径>\emoagent-v1
```

> **可选**：如果 BERT 模型下载失败（SSL 报错），可以设置 HuggingFace 镜像源加速下载：
>
> ```
> set HF_ENDPOINT=https://hf-mirror.com
> ```

```
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8200
```

> **参数解释**：
>
> - `app.main:app`：告诉 uvicorn 从 `app/main.py` 文件中找到 `app` 对象
> - `--reload`：代码修改后自动重启（开发模式）
> - `--port 8200`：后端运行在 8200 端口

启动成功时你会看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8200 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
```

> **注意**：这个终端会被后端服务一直占用，不要关闭它。需要执行其他命令请用其他终端。

### 快速验证后端是否正常

打开浏览器，访问：

```
http://localhost:8200/health
```

页面应该显示类似：

```json
{"status":"ok","version":"0.1.0","llm_provider":"mock"}
```

如果看到这个 JSON，说明后端已经正常运行。

---

## Step 5: 启动前端开发服务器

### 操作步骤

在**终端 3**（再新开一个终端）中执行：

```
cd /d <你的项目路径>\emoagent-v1\frontend
```

```
npm run dev
```

启动成功时你会看到：

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://xxx.xxx.xxx.xxx:5173/
```

> **注意**：和后端一样，这个终端也会被占用，不要关闭。

---

## Step 6: 在浏览器中测试后端 API

### 什么是 Swagger UI？

Swagger UI 是 FastAPI 自动生成的 API 测试界面，你可以直接在浏览器中点击按钮来调用 API，不需要写任何代码或命令。

### 操作步骤

1. 打开浏览器，访问：`http://localhost:8200/docs`
2. 你会看到所有 API 接口的列表

**测试认证接口**：

1. 找到 `POST /api/auth/anonymous`，点击展开
2. 点击右边的 **Try it out** 按钮
3. 点击蓝色的 **Execute** 按钮
4. 在下方的 Response body 中，你会看到返回的 `token` 和 `session_id`
5. **复制这两个值**，后面测试聊天接口时需要用到

**测试聊天接口**：

1. 找到 `POST /api/chat/message`，点击展开
2. 点击 **Try it out**
3. 在 Request body 中填入（把 token 和 session_id 替换为你刚才复制的值）：

```json
{
  "session_id": "你复制的session_id",
  "user_message": "Hello, how are you?",
  "token": "你复制的token"
}
```

1. 点击 **Execute**
2. 检查返回结果：
  - `assistant_message`：应该有 AI 的回复内容
  - `is_crisis`：应该是 `false`
  - `emotion_label`：应返回具体情绪标签（如 `joy`、`sadness` 等）

**测试危机检测**：

1. 同样在 `POST /api/chat/message` 中
2. 把 `user_message` 改为 `"I want to end my life"`
3. 点击 **Execute**
4. 检查返回结果：
  - `is_crisis` 应该是 `true`
  - `assistant_message` 应该包含求助热线信息

---

## Step 7: 在浏览器中验证前端完整功能

打开浏览器，访问：`http://localhost:5173`

按以下清单逐项检查，每项通过就在心里打个勾：

### 基础流程

- 页面加载后自动显示聊天界面（不会一直转圈）
- 弹出情绪自评弹窗，标题显示 **"Self-Assessment"**（不是中文）
- 滑块可以拖动（1-10），点击 **Submit** 后弹窗关闭

### 聊天功能

- 在输入框中输入 `Hello`，按 **Enter** 发送
- 输入框的占位文字显示英文 **"Type a message..."**（不是中文）
- 发送后出现 **"Thinking..."** 提示，然后收到 AI 回复
- 输入 `I feel very sad today`，AI 回复内容应与情绪相关
- 消息列表自动滚动到最新消息
- 按 **Shift+Enter** 可以在输入框中换行（不会发送）

### 危机检测

- 输入 `I want to end my life`，发送后出现红色的 **"Safety Alert"** 提示
- 提示中包含求助热线信息

### 周报页面

- 页面顶部有 **"Report"** 按钮（不是中文"周报"）
- 点击后跳转到周报页面，标题显示 **"Weekly Report"**
- 页面显示统计卡片（Total Turns、Crisis Triggers 等，全部英文）
- 点击左上角返回按钮，回到聊天页面

### 404 页面

- 在浏览器地址栏输入 `http://localhost:5173/nonexistent`
- 显示 404 页面，文字为 **"Page not found"**（不是中文）
- 点击 **"Back to Home"** 按钮回到首页

### 验证完成标准

如果以上所有项都通过，说明整体链路正常，可以进入 Step 9 推送代码。

---

## Step 8: 关闭所有服务

测试完成后，按以下顺序关闭服务：

1. 在**终端 3**（前端）中按 `Ctrl + C` 停止前端
2. 在**终端 2**（后端）中按 `Ctrl + C` 停止后端
3. 在**终端 1** 中执行以下命令停止 Docker 容器：

```
docker-compose down
```

> 如果你想**完全清除数据**（删除数据库中所有内容，下次从头开始），执行：

```
> docker-compose down -v
> 

```

> `-v` 参数会删除数据卷（Volume），即数据库文件。不加 `-v` 则数据会保留，下次启动时还在。

---


## 常见问题排查


| 问题                        | 可能原因                   | 解决方法                                                          |
| ------------------------- | ---------------------- | ------------------------------------------------------------- |
| `docker` 命令不存在            | Docker Desktop 未安装或未启动 | 安装 Docker Desktop 并等待它启动完成                                    |
| `docker-compose up` 失败    | Docker Desktop 没有运行    | 打开 Docker Desktop，等待鲸鱼图标出现                                    |
| `alembic upgrade` 报连接错误   | `.env` 中密码和 Docker 不一致 | 检查 `DATABASE_URL` 和 `POSTGRES_PASSWORD` 密码相同                  |
| seed 脚本执行失败               | 表还没创建                  | 先执行 `alembic upgrade head`                                    |
| 后端启动报 ModuleNotFoundError | Python 依赖没装            | 执行 `pip install -r requirements.txt`                          |
| 前端页面空白                    | 后端没启动 或 跨域被拒           | 确认后端在运行；检查 `.env` 中 `CORS_ORIGINS` 包含 `http://localhost:5173` |
| 前端请求 401 错误               | token 过期               | 在浏览器中按 F12 → Application → Local Storage → 删除所有数据 → 刷新页面      |
| BERT 下载 SSL 报错            | 网络访问 HuggingFace 不稳定    | 可尝试 `set HF_ENDPOINT=https://hf-mirror.com` 后重启后端            |
| BERT 加载报错或很慢              | 模型首次下载约 400MB          | 耐心等待；终端显示 "BERT model loaded successfully" 即成功                |
| 发消息后一直 Thinking 无回复       | BERT 首次下载耗时过长           | 等待终端显示模型加载完成；首次加载后后续请求会很快                                    |
