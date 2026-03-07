# 前端开发指南

## 技术选型

### 框架选择

本项目前端采用React技术栈，具体配置如下：

#### 为什么选择React？

基于项目特点和团队配置（1人前端开发），选择React的核心理由：

1. **生态成熟**：
   - 社区活跃，问题解决快
   - 第三方库丰富（Ant Design、Recharts等）
   - 文档完善，学习资源多

2. **组件化优势**：
   - 适合本项目的聊天界面、评分组件等模块化需求
   - 复用性强，减少1人团队的开发工作量
   - 清晰的组件层次（ChatWindow → MessageList → MessageItem）

3. **TypeScript支持**：
   - 与后端API类型定义无缝对接
   - 减少类型错误，提高单人开发效率
   - IDE智能提示，降低调试时间

4. **状态管理简单**：
   - Zustand轻量级，学习成本低
   - 比Redux更适合中小型项目
   - API简洁，1人团队易于维护

5. **构建工具高效**：
   - Vite开发服务器启动快（<1s）
   - 热更新迅速，提升开发体验
   - 生产构建优化好

6. **测试友好**：
   - React Testing Library简单直观
   - Vitest速度快，集成度高
   - 适合单人快速编写测试用例

#### 核心技术栈
**基础框架**:
- React 18.3+
- TypeScript 5.5+
- Vite 5.x（构建工具）

**状态管理与数据流**:
- Zustand 5.x（状态管理，轻量级适合1人维护）
- Axios（HTTP 客户端）

**UI与可视化**:
- Ant Design 5.x（企业级 UI 组件库，开箱即用）
- @ant-design/icons（图标库）
- Recharts（React原生图表库）

**测试框架**:
- Vitest（单元测试）
- React Testing Library（组件测试）

---

## 项目结构

### 项目目录结构（React）

```
frontend/
├── src/
│   ├── api/                       # API 调用封装
│   │   ├── client.ts              # Axios 实例配置
│   │   ├── types.ts               # API 类型定义
│   │   ├── auth.ts                # 认证相关 API
│   │   ├── chat.ts                # 聊天相关 API
│   │   ├── rating.ts              # 自评相关 API
│   │   └── report.ts              # 周记相关 API
│   ├── components/                # UI 组件
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx     # 聊天窗口主容器
│   │   │   ├── MessageList.tsx    # 消息列表
│   │   │   ├── MessageItem.tsx    # 单条消息
│   │   │   ├── MessageInput.tsx   # 输入框
│   │   │   └── EmotionBadge.tsx   # 情绪标签
│   │   ├── common/
│   │   │   ├── CrisisAlert.tsx    # 危机提示
│   │   │   ├── LoadingSpinner.tsx # 加载动画
│   │   │   └── ErrorBoundary.tsx  # 错误边界
│   │   ├── rating/
│   │   │   ├── RatingModal.tsx    # 自评弹窗
│   │   │   └── RatingSlider.tsx   # 评分滑块
│   │   └── report/
│   │       ├── ReportCard.tsx     # 统计卡片
│   │       ├── EmotionChart.tsx   # 情绪分布图
│   │       └── RatingComparison.tsx # 评分对比图
│   ├── locales/                   # 多语言翻译（i18n）
│   │   ├── en.ts                  # 英文（默认 & 类型定义来源）
│   │   ├── zh.ts                  # 中文
│   │   └── index.ts               # 统一导出，控制当前语言
│   ├── pages/                     # 页面组件
│   │   ├── ChatPage.tsx           # 聊天页面
│   │   ├── ReportPage.tsx         # 周记页面
│   │   └── NotFound.tsx           # 404 页面
│   ├── stores/                    # 状态管理
│   │   ├── sessionStore.ts        # 会话状态（token, session_id）
│   │   ├── chatStore.ts           # 聊天状态（消息列表）
│   │   └── uiStore.ts             # UI 状态（加载、弹窗）
│   ├── types/                     # TypeScript 类型定义
│   │   ├── api.ts                 # API 请求/响应类型
│   │   ├── models.ts              # 数据模型类型
│   │   └── enums.ts               # 枚举类型
│   ├── utils/                     # 工具函数
│   │   ├── storage.ts             # 本地存储封装
│   │   ├── formatters.ts          # 格式化函数
│   │   └── constants.ts           # 常量定义（引用 locales）
│   ├── hooks/                     # 自定义 Hooks（React）
│   │   ├── useSession.ts          # 会话管理 Hook
│   │   ├── useChat.ts             # 聊天功能 Hook
│   │   └── useRating.ts           # 自评功能 Hook
│   ├── styles/                    # 样式文件
│   │   ├── global.css             # 全局样式
│   │   ├── variables.css          # CSS 变量
│   │   └── emotion-colors.css     # 情绪颜色定义
│   ├── App.tsx                    # 根组件
│   └── main.tsx                   # 入口文件
├── public/
│   ├── favicon.ico
│   └── logo.png
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .env.example                   # 环境变量模板
├── .eslintrc.js                   # ESLint 配置
├── .prettierrc                    # Prettier 配置
└── README.md
```

---

## API 调用封装

### 1. Axios 客户端配置

```typescript
// src/api/client.ts
import axios, { AxiosError } from 'axios';
import { useSessionStore } from '../stores/sessionStore';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：自动添加 token
apiClient.interceptors.request.use(
  (config) => {
    const token = useSessionStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一错误处理
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token 失效，重新获取
      await useSessionStore.getState().initSession();
      return apiClient.request(error.config!);
    }
    
    // 其他错误统一处理
    const message = (error.response?.data as any)?.detail || t.error.requestFailed;
    console.error('API Error:', message);
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2. API 类型定义

```typescript
// src/api/types.ts

// 认证相关
export interface AuthResponse {
  token: string;
  session_id: string;
}

// 聊天相关
export interface ChatRequest {
  session_id: string;
  user_message: string;
  token: string;
}

export interface ChatResponse {
  assistant_message: string;
  emotion_label: string | null;
  is_crisis: boolean;
  turn_index: number;
}

// 自评相关
export interface RatingRequest {
  session_id: string;
  rating_type: 'before' | 'after';
  score: number; // 1-10
  token: string;
}

export interface RatingResponse {
  id: number;
  session_id: string;
  rating_type: 'before' | 'after';
  score: number;
  created_at: string;
}

// 周记相关
export interface WeeklyReportResponse {
  session_id: string;
  time_range: {
    start: string;
    end: string;
  };
  session_count: number;
  total_turns: number;
  avg_turns_per_session: number;
  emotion_distribution: Record<string, number>;
  crisis_count: number;
  rating_before_avg: number;
  rating_after_avg: number;
  rating_missing_rate: number;
  bert_avg_latency_ms: number;
  llm_avg_latency_ms: number;
}
```

### 3. API 函数封装

```typescript
// src/api/auth.ts
import apiClient from './client';
import { AuthResponse } from './types';

export const authAPI = {
  getAnonymousToken: async (): Promise<AuthResponse> => {
    const { data } = await apiClient.post<AuthResponse>('/api/auth/anonymous');
    return data;
  },
};

// src/api/chat.ts
import apiClient from './client';
import { ChatRequest, ChatResponse } from './types';

export const chatAPI = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>('/api/chat/message', request);
    return data;
  },
};

// src/api/rating.ts
import apiClient from './client';
import { RatingRequest, RatingResponse } from './types';

export const ratingAPI = {
  submitRating: async (request: RatingRequest): Promise<RatingResponse> => {
    const { data } = await apiClient.post<RatingResponse>('/api/ratings', request);
    return data;
  },
};

// src/api/report.ts
import apiClient from './client';
import { WeeklyReportResponse } from './types';

export const reportAPI = {
  getWeeklyReport: async (sessionId: string, token: string): Promise<WeeklyReportResponse> => {
    const { data } = await apiClient.get<WeeklyReportResponse>(
      `/api/reports/weekly?session_id=${sessionId}&token=${token}`
    );
    return data;
  },
};
```

---

## 状态管理

### Zustand 示例（React）

```typescript
// src/stores/sessionStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';

interface SessionState {
  token: string | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  initSession: () => Promise<void>;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      token: null,
      sessionId: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      initSession: async () => {
        if (get().isAuthenticated) return;
        
        set({ isLoading: true, error: null });
        try {
          const { token, session_id } = await authAPI.getAnonymousToken();
          set({
            token,
            sessionId: session_id,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: 'Failed to get session',
            isLoading: false,
          });
        }
      },
      
      clearSession: () => {
        set({
          token: null,
          sessionId: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: 'session-storage',
    }
  )
);

// src/stores/chatStore.ts
import { create } from 'zustand';
import { chatAPI } from '../api/chat';
import { useSessionStore } from './sessionStore';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  emotion?: string | null;
  isCrisis?: boolean;
  turnIndex: number;
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,
  
  sendMessage: async (text: string) => {
    const { token, sessionId } = useSessionStore.getState();
    if (!token || !sessionId) {
      set({ error: 'Session not initialized' });
      return;
    }
    
    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content: text,
      turnIndex: get().messages.length + 1,
      timestamp: new Date(),
    };
    set({ messages: [...get().messages, userMessage], isLoading: true, error: null });
    
    try {
      const response = await chatAPI.sendMessage({
        session_id: sessionId,
        user_message: text,
        token,
      });
      
      // 添加 AI 回复
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.assistant_message,
        emotion: response.emotion_label,
        isCrisis: response.is_crisis,
        turnIndex: response.turn_index,
        timestamp: new Date(),
      };
      
      set({
        messages: [...get().messages, assistantMessage],
        isLoading: false,
      });
    } catch (error) {
      set({
        error: 'Failed to send message',
        isLoading: false,
      });
    }
  },
  
  clearMessages: () => {
    set({ messages: [] });
  },
}));
```


---

## 核心组件设计

### ChatWindow（聊天窗口）

```typescript
// src/components/chat/ChatWindow.tsx
import React, { useEffect } from 'react';
import { Spin } from 'antd';
import { useChatStore } from '../../stores/chatStore';
import { useSessionStore } from '../../stores/sessionStore';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

import t from '../../locales';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, sendMessage } = useChatStore();
  const { initSession, isAuthenticated } = useSessionStore();

  useEffect(() => {
    initSession();
  }, []);

  const handleSendMessage = async (text: string) => {
    await sendMessage(text);
  };

  if (!isAuthenticated) {
    return <Spin tip={t.chat.initializing} size="large" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatWindow;
```

### EmotionBadge（情绪标签）

```typescript
// src/components/chat/EmotionBadge.tsx
import React from 'react';
import { Tag } from 'antd';
import { EMOTION_COLORS, EMOTION_LABELS } from '../../utils/constants';

interface EmotionBadgeProps {
  emotion: string | null;
}

const EmotionBadge: React.FC<EmotionBadgeProps> = ({ emotion }) => {
  if (!emotion) return null;

  return (
    <Tag color={EMOTION_COLORS[emotion] || 'default'}>
      {EMOTION_LABELS[emotion] || emotion}
    </Tag>
  );
};

export default EmotionBadge;
```

### RatingModal（自评弹窗）

```typescript
// src/components/rating/RatingModal.tsx
import React, { useState } from 'react';
import { Modal, Slider, Typography } from 'antd';
import { ratingAPI } from '../../api/rating';
import { useSessionStore } from '../../stores/sessionStore';

const { Text, Title } = Typography;

interface RatingModalProps {
  type: 'before' | 'after';
  open: boolean;
  onClose: () => void;
}

const sliderMarks: Record<number, string> = {
  1: '1',
  5: '5',
  10: '10',
};

import t from '../../locales';

const RatingModal: React.FC<RatingModalProps> = ({ type, open, onClose }) => {
  const [score, setScore] = useState(5);
  const [loading, setLoading] = useState(false);
  const { token, sessionId } = useSessionStore();

  const handleSubmit = async () => {
    if (!token || !sessionId) return;

    setLoading(true);
    try {
      await ratingAPI.submitRating({
        session_id: sessionId,
        rating_type: type,
        score,
        token,
      });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={t.rating.title}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      okText={t.rating.submit}
      cancelText={t.rating.cancel}
      confirmLoading={loading}
      maskClosable={false}
    >
      <Text>
        {type === 'before' ? t.rating.promptBefore : t.rating.promptAfter}
      </Text>
      <Slider
        min={1}
        max={10}
        value={score}
        onChange={setScore}
        marks={sliderMarks}
        style={{ marginTop: 24 }}
      />
      <div style={{ textAlign: 'center', marginTop: 8 }}>
        <Title level={3}>{score} / 10</Title>
      </div>
    </Modal>
  );
};

export default RatingModal;
```

---

## 样式设计

### Ant Design 全局主题配置

通过 `ConfigProvider` 在应用入口统一配置主题，营造适合心理支持产品的温暖视觉风格：

```typescript
// src/App.tsx
import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

const App: React.FC = () => {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#5B8FB9',
          borderRadius: 12,
          colorBgContainer: '#fafafa',
        },
      }}
    >
      {/* 路由和页面组件 */}
    </ConfigProvider>
  );
};

export default App;
```

### 情绪颜色系统

情绪标签的颜色通过 `EmotionBadge` 组件中的 Ant Design `Tag color` 属性统一管理，不再需要独立的 CSS 文件：

```typescript
// src/utils/constants.ts

/** 情绪 → 颜色映射（用于 Ant Design Tag color 属性） */
export const EMOTION_COLORS: Record<string, string> = {
  joy: '#3b82f6',
  sadness: '#6b7280',
  fear: '#f97316',
  anger: '#ef4444',
  love: '#ec4899',
  surprise: '#8b5cf6',
};

/** 情绪 → 标签映射（从 locales 取值，支持多语言） */
import t from '../locales';

export const EMOTION_LABELS: Record<string, string> = { ...t.emotions };
```

### 危机提示样式

危机提示直接使用 Ant Design 的 `Alert` 组件，无需手写 CSS：

```typescript
// src/components/common/CrisisAlert.tsx
import React from 'react';
import { Alert } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

interface CrisisAlertProps {
  message: string;
}

import t from '../../locales';

const CrisisAlert: React.FC<CrisisAlertProps> = ({ message }) => {
  return (
    <Alert
      message={t.crisis.title}
      description={message}
      type="error"
      showIcon
      icon={<WarningOutlined />}
      style={{ marginBottom: 16 }}
    />
  );
};

export default CrisisAlert;
```

---

## 开发规范

### TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "baseUrl": "./src",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### ESLint + Prettier

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
};
```

### Git Commit 规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试
chore: 构建/工具

示例: feat(chat): 添加情绪标签显示
```

---

## 测试

### 组件测试示例（Vitest + React Testing Library）

```typescript
// src/components/chat/EmotionBadge.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EmotionBadge from './EmotionBadge';

describe('EmotionBadge', () => {
  it('renders english label for known emotion', () => {
    render(<EmotionBadge emotion="fear" />);
    expect(screen.getByText('Fear')).toBeInTheDocument();
  });

  it('returns null when emotion is null', () => {
    const { container } = render(<EmotionBadge emotion={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders Ant Design Tag component', () => {
    render(<EmotionBadge emotion="joy" />);
    const tag = screen.getByText('Joy');
    expect(tag.closest('.ant-tag')).not.toBeNull();
  });
});
```

---

## 环境配置

```env
# .env.example
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENABLE_DEV_TOOLS=true
```

---

## 国际化方案（i18n）

### 架构设计

本项目采用**集中式 locale 文件**方案实现前端多语言支持。所有 UI 文案集中管理在 `src/locales/` 目录下，组件通过统一的 `t` 对象引用翻译键，不允许在组件中硬编码任何用户可见的文本。

```
src/locales/
├── en.ts          # 英文翻译（默认语言，同时作为类型定义来源）
├── zh.ts          # 中文翻译
└── index.ts       # 统一导出入口，控制当前使用的语言
```

### 核心文件说明

#### 1. 英文翻译 & 类型定义（`en.ts`）

`en.ts` 是类型的**唯一来源**（Single Source of Truth），所有其他语言文件必须实现相同的结构：

```typescript
// src/locales/en.ts
const en = {
  emotions: {
    joy: 'Joy',
    sadness: 'Sadness',
    fear: 'Fear',
    anger: 'Anger',
    love: 'Love',
    surprise: 'Surprise',
  },
  chat: {
    title: 'EmoAgent',
    initializing: 'Initializing session...',
    thinking: 'Thinking...',
    placeholder: 'Type a message... (Enter to send, Shift+Enter for new line)',
    send: 'Send',
    greeting: "Hi, I'm your emotional support assistant",
    greetingSub: 'Feel free to share anything on your mind',
  },
  rating: {
    title: 'Self-Assessment',
    submit: 'Submit',
    cancel: 'Cancel',
    promptBefore: 'Rate your emotional state before the session (1-10)',
    promptAfter: 'Rate your emotional state after the session (1-10)',
  },
  crisis: { title: 'Safety Alert' },
  report: {
    title: 'Weekly Report',
    button: 'Report',
    loading: 'Loading report...',
    totalTurns: 'Total Turns',
    crisisTriggers: 'Crisis Triggers',
    ratingBefore: 'Pre-Session Rating',
    ratingAfter: 'Post-Session Rating',
    emotionDist: 'Emotion Distribution',
    performance: 'Performance Metrics',
    bertLatency: 'BERT Avg Latency',
    llmLatency: 'LLM Avg Latency',
    missingRate: 'Rating Missing Rate',
    improvement: 'Mood Improvement',
    noData: 'No data available',
    noReport: 'No report data yet. Start a conversation first.',
  },
  notFound: { subtitle: 'Page not found', backHome: 'Back to Home' },
  error: { requestFailed: 'Request failed' },
};

export type Locale = typeof en;
export default en;
```

#### 2. 其他语言文件（`zh.ts` 等）

其他语言文件通过 `Locale` 类型约束，保证与英文翻译的结构完全一致。TypeScript 编译器会在编译期捕获任何缺失或多余的键：

```typescript
// src/locales/zh.ts
import type { Locale } from './en';

const zh: Locale = {
  emotions: {
    joy: '喜悦',
    sadness: '悲伤',
    // ... 必须覆盖全部键，否则编译报错
  },
  // ...
};

export default zh;
```

#### 3. 导出入口（`index.ts`）

切换全局语言只需修改这一行 import：

```typescript
// src/locales/index.ts
import en from './en';        // ← 切换语言：改为 import zh from './zh'

export type { Locale } from './en';
export default en;
```

### 组件中的使用方式

组件通过 `import t from '../locales'` 获取当前语言的翻译对象：

```typescript
import t from '../locales';

// 直接使用翻译键
<Spin tip={t.chat.initializing} />
<Button>{t.rating.submit}</Button>
<Statistic title={t.report.totalTurns} value={100} />
```

`constants.ts` 中的 `EMOTION_LABELS` 也从 locale 取值：

```typescript
// src/utils/constants.ts
import t from '../locales';

export const EMOTION_LABELS: Record<string, string> = { ...t.emotions };
```

### 添加新语言的步骤

1. **复制 `en.ts` 为新语言文件**（例如 `ja.ts`）：
   ```typescript
   // src/locales/ja.ts
   import type { Locale } from './en';

   const ja: Locale = {
     emotions: { joy: '喜び', sadness: '悲しみ', /* ... */ },
     // 翻译所有键...
   };
   export default ja;
   ```

2. **修改 `index.ts` 的 import**：
   ```typescript
   import ja from './ja';
   export type { Locale } from './en';
   export default ja;
   ```

3. **运行测试**确认无回归：`npm test`

### 进阶：运行时语言切换（可选扩展）

当前方案为**编译时**语言选择（通过修改 import）。如需运行时切换，可扩展 `index.ts` 为：

```typescript
import en from './en';
import zh from './zh';
import type { Locale } from './en';

const locales: Record<string, Locale> = { en, zh };

function getLocale(): Locale {
  const lang = localStorage.getItem('lang') || navigator.language.split('-')[0];
  return locales[lang] || en;
}

export type { Locale };
export default getLocale();
```

配合 Zustand store 或 React Context 可实现不刷新页面的实时切换。

---

## 待补充内容

- [ ] 响应式设计规范（移动端适配）
- [x] ~~国际化方案（i18n）~~
- [ ] 性能优化最佳实践
- [ ] 无障碍访问（Accessibility）
- [ ] PWA 配置（离线支持）
- [ ] WebSocket 实时通信实现
- [ ] 埋点统计方案

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-06  
**维护者**: 前端开发者（1人）
