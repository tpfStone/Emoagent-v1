# API 接口文档

## 概述

本文档详细描述情绪对话系统的 RESTful API 接口规范，包括请求参数、响应格式、错误码说明和调用示例。

**Base URL**: `http://localhost:8000`（开发环境）

**API 版本**: v0.1.0

**认证方式**: Token-based（匿名 token）

## 认证接口

### POST /api/auth/anonymous

获取匿名访问令牌，用于后续 API 调用。

**请求参数**: 无

**响应示例**:
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**响应字段说明**:
- `token` (string): 匿名访问令牌，需在后续请求中携带
- `session_id` (string): 会话唯一标识符

**错误响应**:
```json
{
  "error": "Internal Server Error",
  "detail": "Detailed error message"
}
```

**调用示例**:

```bash
# curl
curl -X POST http://localhost:8000/api/auth/anonymous
```

```javascript
// JavaScript (Fetch API)
const response = await fetch('http://localhost:8000/api/auth/anonymous', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
console.log(data.token, data.session_id);
```

```python
# Python (requests)
import requests

response = requests.post('http://localhost:8000/api/auth/anonymous')
data = response.json()
print(data['token'], data['session_id'])
```

---

## 聊天接口

### POST /api/chat/message

发送用户消息，获取 AI 回复及情绪识别结果。

**请求头**:
- `Content-Type`: application/json
- `Authorization`: Bearer {token}（可选，也可在请求体中传递）

**请求体**:
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_message": "I've been feeling very anxious lately",
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**请求字段说明**:
- `session_id` (string, 必填): 会话ID，来自认证接口
- `user_message` (string, 必填): 用户输入的文本消息
- `token` (string, 必填): 认证令牌

**响应示例**:
```json
{
  "assistant_message": "I understand how you feel. Could you tell me more about what's making you anxious?",
  "emotion_label": "fear",
  "is_crisis": false,
  "turn_index": 3
}
```

**响应字段说明**:
- `assistant_message` (string): AI 生成的回复内容
- `emotion_label` (string): 识别出的情绪标签（sadness, joy, love, anger, fear, surprise）
- `is_crisis` (boolean): 是否触发危机干预
- `turn_index` (integer): 当前对话轮次序号

**特殊情况 - 危机干预**:
```json
{
  "assistant_message": "I notice you may be going through a difficult moment. If you need professional help, please reach out to the following resources:\n- Crisis Hotline: 988 (US/Canada)\n- 24/7 Crisis Text Line: Text HOME to 741741",
  "emotion_label": null,
  "is_crisis": true,
  "turn_index": 5
}
```

**错误响应**:
- **401 Unauthorized**: Token 无效或过期
- **400 Bad Request**: 请求参数错误
- **500 Internal Server Error**: 服务器内部错误

**调用示例**:

```bash
# curl
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "user_message": "I have been feeling very anxious lately",
    "token": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

```javascript
// JavaScript (Axios)
const response = await axios.post('http://localhost:8000/api/chat/message', {
  session_id: '660e8400-e29b-41d4-a716-446655440001',
  user_message: 'I have been feeling very anxious lately',
  token: '550e8400-e29b-41d4-a716-446655440000'
});
console.log(response.data);
```

```typescript
// TypeScript (完整类型定义)
interface ChatRequest {
  session_id: string;
  user_message: string;
  token: string;
}

interface ChatResponse {
  assistant_message: string;
  emotion_label: string | null;
  is_crisis: boolean;
  turn_index: number;
}

const request: ChatRequest = {
  session_id: sessionId,
  user_message: userInput,
  token: authToken
};

const response = await apiClient.post<ChatResponse>('/api/chat/message', request);
```

---

## 自评接口

### POST /api/ratings

提交用户情绪自评分数（会话前后对比）。

**请求体**:
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "rating_type": "before",
  "score": 3,
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**请求字段说明**:
- `session_id` (string, 必填): 会话ID
- `rating_type` (string, 必填): 评分类型，枚举值：`"before"` 或 `"after"`
- `score` (integer, 必填): 评分，范围 1-10
- `token` (string, 必填): 认证令牌

**响应示例**:
```json
{
  "id": 123,
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "rating_type": "before",
  "score": 3,
  "created_at": "2026-03-01T15:30:00Z"
}
```

**响应字段说明**:
- `id` (integer): 自评记录ID
- `session_id` (string): 会话ID
- `rating_type` (string): 评分类型
- `score` (integer): 评分
- `created_at` (string): 创建时间（ISO 8601 格式）

**调用示例**:

```javascript
// 会话开始前评分
await axios.post('/api/ratings', {
  session_id: sessionId,
  rating_type: 'before',
  score: 3,
  token: authToken
});

// 会话结束后评分
await axios.post('/api/ratings', {
  session_id: sessionId,
  rating_type: 'after',
  score: 7,
  token: authToken
});
```

---

## 周记接口

### GET /api/reports/weekly

获取用户的周统计报告（聚合数据）。

**请求参数** (Query String):
- `session_id` (string, 必填): 会话ID
- `token` (string, 可选): 也可通过 Authorization header 传递

**完整URL示例**:
```
GET /api/reports/weekly?session_id=660e8400-e29b-41d4-a716-446655440001&token=550e8400-e29b-41d4-a716-446655440000
```

**响应示例**:
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "time_range": {
    "start": "2026-02-23T00:00:00Z",
    "end": "2026-03-01T23:59:59Z"
  },
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
  "rating_missing_rate": 0.2,
  "bert_avg_latency_ms": 98,
  "llm_avg_latency_ms": 3520
}
```

**响应字段说明**:
- `session_id` (string): 会话ID
- `time_range` (object): 统计时间范围
- `session_count` (integer): 会话总数
- `total_turns` (integer): 对话总轮数
- `avg_turns_per_session` (float): 平均每会话轮数
- `emotion_distribution` (object): 情绪分布统计
- `crisis_count` (integer): 触发危机干预的次数
- `rating_before_avg` (float): 会话前平均评分
- `rating_after_avg` (float): 会话后平均评分
- `rating_missing_rate` (float): 自评缺失率
- `bert_avg_latency_ms` (integer): BERT 平均推理延迟（毫秒）
- `llm_avg_latency_ms` (integer): LLM 平均调用延迟（毫秒）

**调用示例**:

```javascript
// JavaScript
const params = new URLSearchParams({
  session_id: sessionId,
  token: authToken
});

const response = await axios.get(`/api/reports/weekly?${params}`);
const report = response.data;

// 展示情绪分布
console.log('Emotion distribution:', report.emotion_distribution);
console.log('Rating improvement:', report.rating_after_avg - report.rating_before_avg);
```

---

## 错误码说明

| HTTP 状态码 | 错误类型 | 说明 | 解决方案 |
|------------|---------|------|---------|
| 200 | OK | 请求成功 | - |
| 400 | Bad Request | 请求参数错误 | 检查请求体格式和必填字段 |
| 401 | Unauthorized | Token 无效或过期 | 重新调用认证接口获取新 token |
| 404 | Not Found | 资源不存在 | 检查请求路径和参数 |
| 422 | Unprocessable Entity | 数据验证失败 | 检查字段类型和取值范围 |
| 500 | Internal Server Error | 服务器内部错误 | 联系管理员或查看日志 |
| 503 | Service Unavailable | 服务暂时不可用 | 稍后重试 |

**错误响应格式**:
```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "field": "Field name (可选)"
}
```

---

## 通用约定

### 请求头
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}  // 可选
```

### 日期时间格式
所有时间字段使用 ISO 8601 格式：
```
2026-03-01T15:30:00Z
```

### 分页（未来扩展）
```
GET /api/resource?page=1&page_size=20
```

### 限流
- 每个 session 每分钟最多 60 次请求
- 超过限流返回 429 Too Many Requests

---

## 完整调用流程示例

### 前端完整流程（TypeScript）

```typescript
// 1. 初始化：获取匿名 token
const authResponse = await fetch('/api/auth/anonymous', { method: 'POST' });
const { token, session_id } = await authResponse.json();

// 2. 会话开始前自评
await fetch('/api/ratings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    rating_type: 'before',
    score: 3,
    token
  })
});

// 3. 开始对话
const chatResponse = await fetch('/api/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    user_message: 'Hello, I am feeling very anxious',
    token
  })
});

const { assistant_message, emotion_label, is_crisis } = await chatResponse.json();
console.log('AI reply:', assistant_message);
console.log('Emotion:', emotion_label);

// 4. 会话结束后自评
await fetch('/api/ratings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    rating_type: 'after',
    score: 7,
    token
  })
});

// 5. 获取周报
const reportResponse = await fetch(`/api/reports/weekly?session_id=${session_id}&token=${token}`);
const report = await reportResponse.json();
console.log('Weekly report:', report);
```

---

## 待补充内容

- [ ] WebSocket 接口（实时对话）
- [ ] 批量操作接口
- [ ] 管理后台接口
- [ ] 数据导出接口
- [ ] API 速率限制详细说明
- [ ] Webhook 回调机制

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-04  
**维护者**: 后端团队（API设计与实现）+ 前端团队（API调用）
