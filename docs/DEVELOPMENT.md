# 开发指南

## 快速开始

### 环境准备

**必需软件**:
- Python 3.13+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+
- Git

**开发工具**:
- Visual Studio Code / PyCharm（代码编辑器）
- Postman / Insomnia（API 测试）
- DBeaver / pgAdmin（数据库管理）
- RedisInsight（Redis 管理）

### 团队分工
- **模型开发**（2人）：BERT模型训练与优化、LLM集成、Prompt工程
- **后端开发**（2人）：API开发、数据库设计、系统架构
- **前端开发**（1人）：React应用开发、UI/UX实现

---

## 后端开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/your-org/emoagent-v1.git
cd emoagent-v1
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 或使用 uv（更快的替代方案）
uv venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt

# 或使用 uv（更快）
uv pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

必填配置：
```env
DATABASE_URL=postgresql://emoagent_user:password@localhost:5432/emoagent_dev
REDIS_URL=redis://localhost:6379/0

# LLM 配置（开发阶段先用 Mock，后续替换为真实 LLM）
# 第一阶段：使用 Mock LLM（推荐开发时使用）
LLM_PROVIDER=mock
# 无需 API Key，快速开始开发

# 第二阶段：切换到 DeepSeek（需要时取消注释）
# LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. 创建数据库

```bash
# 连接 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE DATABASE emoagent_dev;
CREATE USER emoagent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE emoagent_dev TO emoagent_user;
\q
```

### 6. 运行数据库迁移

```bash
# 执行迁移
alembic upgrade head

# 验证表结构
psql -U emoagent_user -d emoagent_dev -c "\dt"
```

### 7. 导入种子数据

数据库迁移完成后，需要导入 `crisis_rules` 表的初始数据（6 类危机关键词和干预话术）：

```bash
psql -U emoagent_user -d emoagent_dev -f scripts/seed_crisis_rules.sql
```

### 8. 下载 BERT 模型

启动后端服务时，`EmotionService` 需要加载 BERT 模型进行情绪分类。如果仅运行单元测试（测试中通过 `AsyncMock` 替代），可跳过此步骤。

本项目使用 `nateraw/bert-base-uncased-emotion` 模型，支持 6 种情绪分类（sadness, joy, love, anger, fear, surprise）。

```bash
# 自动下载到 ./models 目录
python -c "from transformers import AutoModelForSequenceClassification, AutoTokenizer; AutoModelForSequenceClassification.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models'); AutoTokenizer.from_pretrained('nateraw/bert-base-uncased-emotion', cache_dir='./models')"
```

### 9. 启动后端服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

---

## 前端开发环境搭建

### 1. 进入前端目录

```bash
cd frontend
```

### 2. 安装依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm（更快的替代方案）
pnpm install
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

配置内容：
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. 启动前端服务

```bash
npm run dev
# 或
pnpm dev

# 访问前端
open http://localhost:5173
```

---

## 开发工作流

### 分支策略

```
main            # 生产分支（受保护）
  ↑
develop         # 开发分支
  ↑
feature/*       # 功能分支
hotfix/*        # 紧急修复分支
```

### 创建功能分支

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/emotion-badge

# 开发...

# 提交代码
git add .
git commit -m "feat(frontend): add emotion badge component"

# 推送到远程
git push origin feature/emotion-badge
```

### Commit 规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```bash
feat(chat): add emotion badge display
fix(api): handle llm timeout correctly
docs(readme): update installation steps
refactor(dao): simplify turn query logic
test(service): add chat service unit tests
```

---

## 代码规范

### 后端代码规范（Python）

#### PEP 8 + 类型标注

```python
# 好的示例
from typing import Optional, List

async def get_turns_by_session(
    session_id: str,
    limit: Optional[int] = None
) -> List[Turn]:
    """
    根据 session_id 查询 turns
    
    Args:
        session_id: 会话ID
        limit: 限制返回数量
        
    Returns:
        Turn 对象列表
    """
    query = select(Turn).where(Turn.session_id == session_id)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
```

#### 使用 Black 格式化

```bash
# 安装 Black
pip install black

# 格式化代码
black app/ tests/

# 检查格式
black --check app/
```

#### 使用 isort 排序导入

```bash
# 安装 isort
pip install isort

# 排序导入
isort app/ tests/

# 检查排序
isort --check app/
```

#### 使用 mypy 类型检查

```bash
# 安装 mypy
pip install mypy

# 类型检查
mypy app/

# 配置 mypy.ini
[mypy]
python_version = 3.13
strict = True
ignore_missing_imports = True
```

### 前端代码规范（TypeScript）

#### ESLint + Prettier

```json
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier'
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn'
  }
};

// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

#### 格式化代码

```bash
# 格式化
npm run format

# 检查格式
npm run format:check

# Lint 检查
npm run lint

# 自动修复
npm run lint:fix
```

#### TypeScript 严格模式

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

---

## 调试技巧

### 后端调试

#### 使用 pdb 调试器

```python
# 在代码中设置断点
import pdb; pdb.set_trace()

# 调试命令
# n - next
# s - step into
# c - continue
# p <var> - print variable
# q - quit
```

#### VS Code 调试配置

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

#### 日志调试

```python
import logging

logger = logging.getLogger(__name__)

async def process_message(...):
    logger.info(f"Processing message for session: {session_id}")
    logger.debug(f"User message: {user_message}")
    
    try:
        result = await llm_service.generate_response(prompt)
        logger.info(f"LLM response received: {len(result)} chars")
    except Exception as e:
        logger.error(f"LLM error: {e}", exc_info=True)
```

### 前端调试

#### React DevTools

```bash
# 安装浏览器扩展
# Chrome: React Developer Tools
# Firefox: React DevTools
```

#### Zustand DevTools

```typescript
import { devtools } from 'zustand/middleware';

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      // state and actions
    }),
    { name: 'ChatStore' }
  )
);
```

#### 浏览器调试

```javascript
// 打印状态
console.log('Chat store:', useChatStore.getState());

// 断点
debugger;

// 性能分析
console.time('API call');
await chatAPI.sendMessage(...);
console.timeEnd('API call');
```

---

## 测试驱动开发（TDD）

### 后端 TDD 流程

```bash
# 1. 编写测试（先失败）
# tests/test_services/test_chat_service.py

@pytest.mark.asyncio
async def test_process_message_returns_response():
    # Arrange
    chat_service = ChatService(...)
    
    # Act
    response = await chat_service.process_message(
        session_id="test",
        user_message="Hello",
        token="test-token"
    )
    
    # Assert
    assert response.assistant_message is not None
    assert response.emotion_label is not None

# 2. 运行测试（应该失败）
pytest tests/test_services/test_chat_service.py::test_process_message_returns_response -v

# 3. 实现功能（让测试通过）
# app/services/chat_service.py
async def process_message(...):
    # 实现逻辑
    pass

# 4. 运行测试（应该通过）
pytest tests/test_services/test_chat_service.py::test_process_message_returns_response -v

# 5. 重构代码
# 6. 再次运行测试（确保仍然通过）
```

### 前端 TDD 流程

```bash
# 1. 编写测试
# src/components/EmotionBadge.test.tsx

# 2. 运行测试（应该失败）
npm run test -- EmotionBadge.test.tsx

# 3. 实现组件
# src/components/EmotionBadge.tsx

# 4. 运行测试（应该通过）
npm run test -- EmotionBadge.test.tsx

# 5. 重构
```

---

## 性能优化技巧

### 后端优化

#### 数据库查询优化

```python
# 使用索引
query = select(Turn).where(Turn.session_id == session_id)  # session_id 有索引

# 避免 N+1 查询
query = select(Turn).options(joinedload(Turn.session))

# 分页查询
query = select(Turn).limit(20).offset(0)

# 批量插入
db.add_all([turn1, turn2, turn3])
await db.commit()
```

#### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_crisis_rules():
    """缓存危机规则（内存）"""
    return dao.get_all_crisis_rules()

# Redis 缓存
async def get_user_data(session_id: str):
    cache_key = f"user:{session_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    data = await dao.get_user_data(session_id)
    await redis.setex(cache_key, 3600, json.dumps(data))
    return data
```

### 前端优化

#### 代码分割

```typescript
// 路由懒加载
const ChatPage = lazy(() => import('./pages/ChatPage'));
const ReportPage = lazy(() => import('./pages/ReportPage'));

<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<ChatPage />} />
    <Route path="/report" element={<ReportPage />} />
  </Routes>
</Suspense>
```

#### React.memo 优化

```typescript
const EmotionBadge = React.memo<EmotionBadgeProps>(({ emotion }) => {
  return <span>{emotion}</span>;
});
```

#### useMemo / useCallback

```typescript
const sortedMessages = useMemo(() => {
  return messages.sort((a, b) => a.turnIndex - b.turnIndex);
}, [messages]);

const handleSend = useCallback((text: string) => {
  sendMessage(text);
}, [sendMessage]);
```

---

## 常见问题（FAQ）

### Q1: 如何使用情绪标签？

当前使用 `nateraw/bert-base-uncased-emotion` 模型，输出英文标签：

**模型输出标签**:
- sadness (悲伤)
- joy (喜悦)
- love (爱)
- anger (愤怒)
- fear (恐惧)
- surprise (惊讶)

**前端显示（Ant Design Tag）**:
```typescript
import { Tag } from 'antd';

// 情绪 → 颜色映射（用于 Tag color 属性）
const emotionColors: Record<string, string> = {
  joy: '#3b82f6',
  sadness: '#6b7280',
  fear: '#f97316',
  anger: '#ef4444',
  love: '#ec4899',
  surprise: '#8b5cf6',
};

// 情绪 → 中文标签映射
const emotionLabels: Record<string, string> = {
  joy: '喜悦',
  sadness: '悲伤',
  fear: '恐惧',
  anger: '愤怒',
  love: '爱',
  surprise: '惊讶',
};

// 使用示例
<Tag color={emotionColors[emotion]}>{emotionLabels[emotion]}</Tag>
```

### Q2: 如何切换到不同的 LLM？

**开发阶段 LLM 集成方式**：

```bash
# 第一阶段：Mock LLM（推荐开发时使用）
LLM_PROVIDER=mock
# 优点：免费、快速、无需 API Key

# 第二阶段：DeepSeek 免费额度（真实测试）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key-here

# 生产阶段：按需替换为其他 LLM
LLM_PROVIDER=qianwen
QIANWEN_API_KEY=sk-new-key

# 重启服务后自动切换到新的 LLM 实现
```

### Q3: 如何添加新的 API 端点？

```python
# 1. 定义 Pydantic 模型
class NewRequest(BaseModel):
    param1: str
    param2: int

# 2. 创建 Handler
@router.post("/new-endpoint")
async def new_endpoint(request: NewRequest):
    return {"result": "success"}

# 3. 在 main.py 中注册路由
app.include_router(new_router)
```

### Q4: 数据库迁移失败怎么办？

```bash
# 回滚到上一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看历史
alembic history

# 强制重新生成迁移
alembic revision --autogenerate -m "regenerate migration"
```

### Q5: Redis 连接失败？

```bash
# 检查 Redis 状态
redis-cli ping

# 查看 Redis 配置
redis-cli CONFIG GET *

# 重启 Redis
sudo systemctl restart redis

# 检查环境变量
echo $REDIS_URL
```

---

## 开发最佳实践

### 1. 始终编写测试
- 新功能必须有单元测试
- 修复 bug 时先写复现测试
- 保持测试覆盖率 > 80%

### 2. 代码审查（Code Review）
- 每个 PR 需要至少 1 人审查
- 审查清单：
  - [ ] 代码符合规范
  - [ ] 有充足的测试
  - [ ] 文档已更新
  - [ ] 无明显性能问题

### 3. 小步提交
- 每次提交专注一个改动
- 提交信息清晰描述改动内容
- 避免大而全的提交

### 4. 文档优先
- 新功能先写文档
- API 修改同步更新文档
- 复杂逻辑添加注释

### 5. 持续集成（CI）
- 推送代码自动运行测试
- 测试失败不允许合并
- 定期运行覆盖率检查

---

## 开发工具列表

### 后端开发
- **httpie**: 命令行 HTTP 客户端
  ```bash
  http POST localhost:8000/api/auth/anonymous
  ```
- **ipython**: 增强的 Python REPL
- **pytest-watch**: 自动运行测试
  ```bash
  ptw tests/
  ```

### 前端开发
- **React DevTools**: 调试 React 组件
- **Zustand DevTools**: 调试状态管理
- **Lighthouse**: 性能审计

### 通用工具
- **Git GUI**: GitKraken / SourceTree
- **API 文档**: Swagger UI（自动生成）
- **数据库工具**: DBeaver
- **Redis 工具**: RedisInsight

---

## 待补充内容

- [ ] 微服务开发指南
- [ ] Docker 本地开发环境
- [ ] 数据 Mock 策略
- [ ] 本地化（i18n）开发
- [ ] 移动端开发适配
- [ ] 性能基准测试

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-02  
**维护者**: 全体开发团队（2人模型 + 2人后端 + 1人前端）
