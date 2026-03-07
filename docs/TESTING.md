# 测试指南

## 测试策略

本项目采用分层测试策略，确保各层独立可测试，整体流程正确无误。

### 团队测试职责
- **模型团队**（2人）：负责BERT模型准确率测试、LLM响应质量评估、情绪分类测试
- **后端团队**（2人）：负责DAO层单元测试、Service层单元测试、Handler层集成测试、API端到端测试
- **前端团队**（1人）：负责组件单元测试、状态管理测试、UI交互测试、E2E测试

### 测试金字塔
```
         E2E Tests (端到端测试)
        /                    \
   Integration Tests (集成测试)
  /                              \
Unit Tests (单元测试 - 覆盖率>80%)
```

---

## 后端测试

### 测试框架
- **Pytest**: 主测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 覆盖率报告
- **httpx**: HTTP 客户端测试

### 测试目录结构
```
tests/
├── conftest.py                # 全局 fixtures
├── test_dao/                  # DAO 层单元测试
│   ├── test_session_dao.py
│   ├── test_turn_dao.py
│   ├── test_crisis_dao.py
│   └── test_rating_dao.py
├── test_services/             # Service 层单元测试
│   ├── test_auth_service.py
│   ├── test_chat_service.py
│   ├── test_emotion_service.py
│   ├── test_memory_service.py
│   ├── test_crisis_service.py
│   ├── test_llm_service.py
│   ├── test_metrics_service.py
│   └── test_report_service.py
└── test_handlers/             # Handler 层集成测试
    ├── test_auth_handler.py
    ├── test_chat_handler.py
    ├── test_rating_handler.py
    └── test_report_handler.py
```

### DAO 层单元测试

**测试重点**: 数据库 CRUD 操作的正确性

**测试示例**:
```python
# tests/test_dao/test_turn_dao.py
import pytest
from app.dao.turn_dao import TurnDAO
from app.models.models import Turn

@pytest.mark.asyncio
async def test_create_turn(db_session):
    """测试创建 turn 记录"""
    dao = TurnDAO(db_session)
    
    turn = await dao.create_turn(
        session_id="test-session-id",
        turn_index=1,
        user_message="Hello",
        assistant_message="Hi there!",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=98,
        llm_latency_ms=3500
    )
    
    assert turn.id is not None
    assert turn.session_id == "test-session-id"
    assert turn.turn_index == 1
    assert turn.emotion_label == "joy"

@pytest.mark.asyncio
async def test_get_turns_by_session(db_session):
    """Test querying turns by session_id"""
    dao = TurnDAO(db_session)
    
    # Create test data
    await dao.create_turn(...)
    await dao.create_turn(...)
    
    # Query
    turns = await dao.get_turns_by_session("test-session-id")
    
    assert len(turns) == 2
```

### Service 层单元测试

**测试重点**: 业务逻辑的正确性，使用 Mock 隔离外部依赖

**测试示例**:
```python
# tests/test_services/test_chat_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.chat_service import ChatService

@pytest.mark.asyncio
async def test_process_message_normal_flow():
    """Test normal chat flow"""
    # Mock 依赖
    mock_auth_service = AsyncMock()
    mock_crisis_service = AsyncMock()
    mock_crisis_service.check_crisis.return_value = CrisisResult(is_crisis=False)
    
    mock_emotion_service = AsyncMock()
    mock_emotion_service.classify_emotion.return_value = "fear"
    
    mock_memory_service = AsyncMock()
    mock_memory_service.get_recent_turns.return_value = []
    
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_response.return_value = "I understand how you feel"
    
    mock_metrics_service = AsyncMock()
    
    # Create ChatService instance
    chat_service = ChatService(
        auth_service=mock_auth_service,
        crisis_service=mock_crisis_service,
        emotion_service=mock_emotion_service,
        memory_service=mock_memory_service,
        llm_service=mock_llm_service,
        metrics_service=mock_metrics_service
    )
    
    # Execute test
    response = await chat_service.process_message(
        session_id="test-session",
        user_message="I am feeling anxious",
        token="test-token"
    )
    
    # Assertions
    assert response.assistant_message == "I understand how you feel"
    assert response.emotion_label == "fear"
    assert response.is_crisis is False
    
    # Verify calls
    mock_emotion_service.classify_emotion.assert_called_once_with("I am feeling anxious")
    mock_llm_service.generate_response.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_crisis_flow():
    """Test crisis intervention flow"""
    mock_crisis_service = AsyncMock()
    mock_crisis_service.check_crisis.return_value = CrisisResult(
        is_crisis=True,
        response="Please call the crisis hotline...",
        matched_keyword="suicide"
    )
    
    chat_service = ChatService(crisis_service=mock_crisis_service, ...)
    
    response = await chat_service.process_message(
        session_id="test-session",
        user_message="I want to end my life",
        token="test-token"
    )
    
    assert response.is_crisis is True
    assert "crisis hotline" in response.assistant_message
```

### Handler 层集成测试

**测试重点**: API 端到端流程的正确性

**测试示例**:
```python
# tests/test_handlers/test_chat_handler.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_send_message_success():
    """Test send message API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 先获取 token
        auth_response = await client.post("/api/auth/anonymous")
        assert auth_response.status_code == 200
        auth_data = auth_response.json()
        
        token = auth_data["token"]
        session_id = auth_data["session_id"]
        
        # 2. 发送消息
        response = await client.post(
            "/api/chat/message",
            json={
                "session_id": session_id,
                "user_message": "Hello",
                "token": token
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "assistant_message" in data
        assert "emotion_label" in data
        assert data["is_crisis"] is False

@pytest.mark.asyncio
async def test_send_message_invalid_token():
    """Test invalid token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/message",
            json={
                "session_id": "fake-session",
                "user_message": "Hello",
                "token": "invalid-token"
            }
        )
        
        assert response.status_code == 401
```

### 测试 Fixtures

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """Create test database session"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_llm_service():
    """Mock LLM service"""
    from unittest.mock import AsyncMock
    mock = AsyncMock()
    mock.generate_response.return_value = "Test reply"
    mock.health_check.return_value = True
    return mock
```

### 运行测试

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_services/test_chat_service.py -v

# Run a specific test function
pytest tests/test_services/test_chat_service.py::test_process_message_normal_flow -v

# Generate coverage report
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### 覆盖率要求

| 层次 | 覆盖率目标 |
|------|-----------|
| DAO 层 | > 90% |
| Service 层 | > 85% |
| Handler 层 | > 80% |
| 整体 | > 80% |

---

## 前端测试

### 测试框架
- **Vitest**: 单元测试框架（Vite 原生支持）
- **React Testing Library**: 组件测试
- **Playwright / Cypress**: E2E 测试（可选）

### 测试目录结构
```
frontend/
├── src/
│   └── components/
│       ├── ChatWindow.tsx
│       └── ChatWindow.test.tsx
└── e2e/
    ├── chat.spec.ts
    └── rating.spec.ts
```

### 组件单元测试

**测试示例（React + Vitest + Ant Design）**:
```typescript
// src/components/chat/EmotionBadge.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EmotionBadge from './EmotionBadge';

describe('EmotionBadge', () => {
  it('renders emotion chinese label correctly', () => {
    render(<EmotionBadge emotion="fear" />);
    expect(screen.getByText('恐惧')).toBeInTheDocument();
  });

  it('returns null when emotion is null', () => {
    const { container } = render(<EmotionBadge emotion={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders as Ant Design Tag component', () => {
    render(<EmotionBadge emotion="joy" />);
    const tag = screen.getByText('喜悦');
    expect(tag.closest('.ant-tag')).not.toBeNull();
  });

  it('renders different labels for different emotions', () => {
    const { rerender } = render(<EmotionBadge emotion="sadness" />);
    expect(screen.getByText('悲伤')).toBeInTheDocument();

    rerender(<EmotionBadge emotion="love" />);
    expect(screen.getByText('爱')).toBeInTheDocument();
  });
});
```

### API 调用测试

```typescript
// src/api/chat.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { chatAPI } from './chat';

vi.mock('axios');

describe('chatAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('sendMessage calls API with correct parameters', async () => {
    const mockResponse = {
      data: {
        assistant_message: 'Hello',
        emotion_label: 'joy',
        is_crisis: false,
        turn_index: 1
      }
    };
    
    (axios.post as any).mockResolvedValue(mockResponse);
    
    const request = {
      session_id: 'test-session',
      user_message: 'Hi',
      token: 'test-token'
    };
    
    const result = await chatAPI.sendMessage(request);
    
    expect(axios.post).toHaveBeenCalledWith('/api/chat/message', request);
    expect(result.assistant_message).toBe('Hello');
  });
  
  it('handles API error correctly', async () => {
    (axios.post as any).mockRejectedValue(new Error('Network error'));
    
    await expect(chatAPI.sendMessage({} as any)).rejects.toThrow('Network error');
  });
});
```

### 状态管理测试

```typescript
// src/stores/chatStore.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useChatStore } from './chatStore';
import { chatAPI } from '../api/chat';

vi.mock('../api/chat');

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({ messages: [], isLoading: false, error: null });
  });
  
  it('sendMessage adds user message and AI response', async () => {
    const mockResponse = {
      assistant_message: 'AI response',
      emotion_label: 'joy',
      is_crisis: false,
      turn_index: 1
    };
    
    (chatAPI.sendMessage as any).mockResolvedValue(mockResponse);
    
    const store = useChatStore.getState();
    await store.sendMessage('Hello');
    
    const messages = useChatStore.getState().messages;
    expect(messages).toHaveLength(2);
    expect(messages[0].role).toBe('user');
    expect(messages[0].content).toBe('Hello');
    expect(messages[1].role).toBe('assistant');
    expect(messages[1].content).toBe('AI response');
  });
});
```

### E2E 测试（Playwright 示例）

```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test('user can complete a chat session', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    await expect(page.locator('.chat-window')).toBeVisible();
    
    await page.fill('input[placeholder="Type a message..."]', 'Hello');
    await page.click('button:has-text("Send")');
    
    await expect(page.locator('.message.assistant').first()).toBeVisible({ timeout: 10000 });
    
    await expect(page.locator('.emotion-badge').first()).toBeVisible();
    
    await page.fill('input[placeholder="Type a message..."]', 'I am feeling anxious');
    await page.click('button:has-text("Send")');
    
    await expect(page.locator('.crisis-alert')).not.toBeVisible();
  });
  
  test('crisis alert appears for crisis keywords', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    await page.fill('input[placeholder="Type a message..."]', 'I want to end my life');
    await page.click('button:has-text("Send")');
    
    await expect(page.locator('.crisis-alert')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.crisis-alert')).toContainText('crisis hotline');
  });
});
```

### 运行前端测试

```bash
# Unit tests
npm run test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage

# E2E tests (backend and frontend must be running)
npm run test:e2e

# E2E tests (UI mode)
npm run test:e2e:ui
```

---

## 性能测试（可选）

### 后端性能测试（Locust）

```python
# locustfile.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Get token"""
        response = self.client.post("/api/auth/anonymous")
        data = response.json()
        self.token = data["token"]
        self.session_id = data["session_id"]
    
    @task(3)
    def send_message(self):
        """Send a chat message"""
        self.client.post("/api/chat/message", json={
            "session_id": self.session_id,
            "user_message": "Hello",
            "token": self.token
        })
    
    @task(1)
    def get_report(self):
        """Get weekly report"""
        self.client.get(f"/api/reports/weekly?session_id={self.session_id}&token={self.token}")
```

运行性能测试：
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
```

---

## 测试最佳实践

### 通用原则
1. **独立性**: 每个测试应独立运行，互不影响
2. **可重复性**: 测试结果应稳定一致
3. **快速执行**: 单元测试应在秒级完成
4. **清晰命名**: 测试函数名应描述测试场景
5. **适当 Mock**: 隔离外部依赖，专注测试目标

### 命名规范
```python
# Good naming
def test_create_turn_with_valid_data()
def test_send_message_when_crisis_detected()
def test_llm_timeout_triggers_fallback()

# Bad naming
def test_turn()
def test_case_1()
def test()
```

### Mock 原则
- Mock 外部 API（DeepSeek、BERT）
- Mock 数据库（DAO 层测试除外）
- Mock 时间（测试时间相关逻辑）
- 不 Mock 被测试的对象

---

## 待补充内容

- [ ] 压力测试方案
- [ ] 安全测试（SQL 注入、XSS）
- [ ] 可访问性测试（a11y）
- [ ] 跨浏览器兼容性测试
- [ ] 移动端测试
- [ ] 数据一致性测试
- [ ] 回归测试策略

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-02  
**维护者**: 全体开发团队（各负责各自模块测试）
