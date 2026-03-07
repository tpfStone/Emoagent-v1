# LLM 集成开发方案

## 文档概述

本文档说明在软件开发过程中，LLM（大语言模型）集成部分将经历的三个阶段。为了降低初期开发成本、方便本地调试，项目先使用 Mock LLM 进行开发，待功能稳定后再替换为真实 LLM 服务。

**最后更新**: 2026-03-02  
**维护者**: 模型团队（2人）

---

## 总览

### 为什么要分阶段

在开发初期，直接依赖外部 LLM API 会带来以下问题：需要 API Key、产生费用、网络不稳定影响开发效率、CI/CD 无法自动化运行。因此项目采用分阶段方式接入 LLM：

1. **开发阶段**：使用 Mock LLM，免费且无外部依赖，方便快速迭代
2. **测试阶段**：替换为 DeepSeek 等真实 LLM，验证端到端效果
3. **生产阶段**：按需评估切换为其他 LLM 供应商

### 架构保障

- ✅ **零成本启动**：开发阶段无需 API Key，立即开始
- ✅ **快速迭代**：Mock 模式下验证业务逻辑和流程
- ✅ **一键切换**：通过环境变量切换 LLM 实现，无需改动业务代码
- ✅ **成本可控**：先用免费额度测试，再根据需求投入
- ✅ **供应商无关**：抽象接口设计，支持多种 LLM 供应商

---

## 第一阶段：Mock LLM（开发阶段）

### 适用场景

✅ 适合以下情况：
- 项目初期开发，验证架构和流程
- 前后端联调，无需真实 LLM 响应
- 本地开发环境，网络不稳定或无外网访问
- CI/CD 自动化测试

### 技术实现

#### 1. 配置文件设置

修改 `.env` 文件：

```env
# 第一阶段：Mock LLM（默认配置）
LLM_PROVIDER=mock
# 无需配置 API Key
```

#### 2. Mock LLM 实现原理

```python
# app/services/mock_llm_service.py
import asyncio
from typing import Optional

class MockLLMService:
    """Mock LLM 实现 - 用于开发阶段快速验证流程"""
    
    def __init__(self):
        # 预设情绪响应模板
        self.emotion_responses = {
            "sadness": "I can sense you're going through a tough time right now. It's important to allow yourself to feel these emotions. Would you like to talk about what happened?",
            "joy": "It sounds like you're in a great mood! Would you like to share what's making you happy?",
            "anger": "I understand you're feeling angry right now. Anger is a completely normal emotion. Let's look at what's causing you to feel this way.",
            "fear": "I notice you might be feeling anxious or worried. These feelings aren't easy to face, but you're not alone.",
            "love": "I can feel the warmth and love in your words. That's a beautiful emotion.",
            "surprise": "It sounds like something unexpected happened!",
        }
        #默认响应
        self.default_response = "Thank you for sharing that with me. I'm here to listen. Please go on."
    
    async def generate_response(
        self,
        prompt: str,
        timeout: float = 10.0,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """模拟响应生成"""
        # 模拟网络延迟（可调整）
        await asyncio.sleep(0.3)
        
        # 从 prompt 文本中提取情绪关键词，选择对应模板
        prompt_lower = prompt.lower()
        for emotion, response in self.emotion_responses.items():
            if emotion in prompt_lower:
                return response
        return self.default_response
    
    #状态检测
    async def health_check(self) -> bool:
        """Mock 服务总是健康的"""
        return True
```

#### 3. 响应特点

- **快速响应**：模拟 300ms 延迟
- **情绪感知**：根据 BERT 识别的情绪返回对应模板
- **稳定可靠**：无网络依赖，100% 可用性
- **可扩展**：易于添加更多响应模板

### 使用指南

#### 启动后端服务

```bash
cp .env.example .env
# 确认 LLM_PROVIDER=mock
uvicorn app.main:app --reload
```

#### 测试 Mock LLM

```bash
# 测试聊天接口
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "user_message": "I am feeling really sad today",
    "token": "test-token"
  }'

# 预期响应：基于 sadness 情绪的预设模板
```

### 限制与注意事项

⚠️ **功能限制**：
- 响应内容固定，无法根据上下文动态生成
- 不支持复杂对话逻辑和个性化回复
- 仅用于流程验证，不适合用户体验测试

✅ **使用建议**：
- 开发初期优先使用 Mock LLM
- 验证 API 接口、数据流、情绪识别等核心功能
- 完成基础功能后再切换到真实 LLM

---

## 第二阶段：DeepSeek 免费额度（测试阶段）

### 适用场景

✅ 适合以下情况：
- 需要真实 LLM 对话体验
- 验证 Prompt 工程效果
- 进行端到端集成测试
- 评估系统完整性

### DeepSeek 简介

- **官网**: https://platform.deepseek.com/
- **免费额度**: 新用户提供一定量的免费 tokens
- **中文支持**: 优秀的中文理解和生成能力
- **API 兼容**: 支持 OpenAI SDK，易于集成

### 配置步骤

#### 1. 注册并获取 API Key

1. 访问 https://platform.deepseek.com/
2. 注册账号并完成验证
3. 进入控制台，创建 API Key
4. 复制 API Key（格式：`sk-xxxxxx`）

#### 2. 更新配置文件

修改 `.env` 文件：

```env
# 第二阶段：DeepSeek 免费额度
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

#### 3. 重启服务

```bash
# 后端服务会自动切换到 DeepSeek
uvicorn app.main:app --reload
```

### DeepSeek 实现原理

```python
# app/services/deepseek_llm_service.py
import asyncio
from openai import AsyncOpenAI
from typing import Optional

class DeepSeekLLMService:
    """DeepSeek API 实现 - 通过 OpenAI 兼容接口调用"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat"
    ):
        # 使用 OpenAI SDK（兼容 DeepSeek）
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    async def generate_response(
        self,
        prompt: str,
        timeout: float = 10.0,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                ),
                timeout=timeout
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise TimeoutError(f"DeepSeek API call timed out ({timeout}s)")
        except Exception as e:
            raise RuntimeError(f"DeepSeek API call failed: {e}")
    
    async def health_check(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except:
            return False
```

### Prompt 工程示例

> **注意**：Prompt 模板内容统一维护在 [`config/prompt_template.md`](../config/prompt_template.md)，
> 代码中通过加载该模板并注入运行时变量来构建最终 Prompt，避免硬编码。

```python
# app/services/prompt_builder.py
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "config" / "prompt_template.md"

def _load_template() -> str:
    """加载 prompt_template.md 模板内容（跳过文档头部说明信息，仅保留 Prompt 正文）"""
    raw = TEMPLATE_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i + 1
            break
    return "\n".join(lines[start:]).strip()

_PROMPT_TEMPLATE: str | None = None

def _get_template() -> str:
    global _PROMPT_TEMPLATE
    if _PROMPT_TEMPLATE is None:
        _PROMPT_TEMPLATE = _load_template()
    return _PROMPT_TEMPLATE

def build_emotion_prompt(user_message: str, emotion: str, memory: list) -> str:
    """加载 prompt_template.md 并注入运行时变量，构建最终 Prompt"""
    template = _get_template()

    # 短期记忆（最近 6 轮对话）
    memory_text = "\n".join(
        [f"User: {m['user']}\nAssistant: {m['bot']}" for m in memory[-6:]]
    )

    prompt = template.replace("{{user_input}}", user_message) \
                      .replace("{{detected_emotion}}", emotion)

    if memory_text:
        prompt += f"\n\n**Recent Conversation History:**\n{memory_text}"

    return prompt
```

### LLM 输出解析规则

`config/prompt_template.md` 要求 LLM 按结构化格式输出，包含 **Strategy Analysis** 和 **AI Response** 两个部分。后端在收到 LLM 原始输出后，需要提取 "AI Response" 部分作为 `assistant_message` 返回给前端，而 "Strategy Analysis" 部分仅用于内部日志记录，不暴露给用户。

```python
# app/services/response_parser.py
import re

def extract_ai_response(raw_output: str) -> str:
    """
    从 LLM 结构化输出中提取 '### 2. AI Response' 段落。
    如果 LLM 未按格式输出（如 Mock LLM），则原样返回。
    """
    pattern = r"###\s*2\.\s*AI Response\s*\n(.*)"
    match = re.search(pattern, raw_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_output.strip()
```

在 `ChatService.process_message()` 中调用：

```python
raw_response = await self.llm_service.generate_response(prompt)
assistant_message = extract_ai_response(raw_response)
```

> **Mock LLM** 直接返回纯文本，不含结构化标记，`extract_ai_response` 会原样返回；**真实 LLM** 按 Prompt 模板输出结构化内容，函数自动提取用户可见部分。

### 测试真实对话

```bash
# 测试真实 LLM 响应
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "user_message": "Work didn't go well today, I got criticized by my manager",
    "token": "test-token"
  }'

# 预期响应：DeepSeek 生成的个性化共情回复
```

### 成本控制

#### 免费额度监控

1. 登录 DeepSeek 控制台
2. 查看 API 使用统计
3. 设置用量告警

#### 节省 Token 技巧

```python
# 1. 限制最大 token 数
max_tokens=200  # 控制响应长度

# 2. 优化 Prompt 长度
# 只保留最近 6 轮对话，不传入完整历史

# 3. 调整温度参数
temperature=0.7  # 平衡创造性和稳定性

# 4. 缓存常见响应（可选）
# 对于常见问题，使用缓存避免重复调用
```

### 故障降级策略

```python
# app/services/chat_service.py
async def generate_llm_response(self, prompt: str, emotion: str) -> str:
    try:
        # 尝试调用 LLM
        response = await self.llm_service.generate_response(
            prompt=prompt,
            timeout=10.0
        )
        return response
    except (TimeoutError, RuntimeError) as e:
        # LLM 失败时，降级到静态响应
        logger.warning(f"LLM call failed, using fallback response: {e}")
        return self._get_fallback_response(emotion)

def _get_fallback_response(self, emotion: str) -> str:
    """从 config/llm_fallback_responses.md 加载降级响应"""
    fallback_map = self._load_fallback_map()
    return fallback_map.get(emotion, fallback_map.get("default", "Thank you for sharing. I'm here for you."))

@staticmethod
@lru_cache(maxsize=1)
def _load_fallback_map() -> dict[str, str]:
    """解析 config/llm_fallback_responses.md，返回 {emotion: response} 映射"""
    path = Path(__file__).resolve().parents[2] / "config" / "llm_fallback_responses.md"
    content = path.read_text(encoding="utf-8")
    result = {}
    current_emotion = None
    for line in content.splitlines():
        if line.startswith("## "):
            current_emotion = line[3:].strip().lower()
        elif current_emotion and line.strip():
            result[current_emotion] = line.strip()
            current_emotion = None
    return result
```

---

## 第三阶段：按需替换（生产阶段）

### 适用场景

✅ 当项目进入生产或以下情况出现时：
- DeepSeek 免费额度用尽
- 需要更高的响应质量或特定功能
- 成本优化需求
- 多模态支持需求

### 备选 LLM 方案

#### 1. 通义千问（阿里云）

**优势**：
- 阿里云生态集成好
- 中文能力强
- 支持多模态

**配置示例**：

```env
LLM_PROVIDER=qianwen
QIANWEN_API_KEY=sk-your-qianwen-key
```

```python
# app/services/qianwen_llm_service.py
from dashscope import Generation

class QianWenLLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        response = Generation.call(
            api_key=self.api_key,
            model='qwen-turbo',
            prompt=prompt,
            **kwargs
        )
        return response.output.text
```

#### 2. 文心一言（百度）

**优势**：
- 百度 AI 生态
- 中文理解深度
- 企业级支持

**配置示例**：

```env
LLM_PROVIDER=wenxin
WENXIN_API_KEY=your-api-key
WENXIN_SECRET_KEY=your-secret-key
```

#### 3. 其他开源模型

- **ChatGLM**：清华开源，可本地部署
- **Llama**：Meta 开源，社区活跃
- **Qwen-Local**：通义千问开源版本

### 切换决策矩阵

| 因素 | Mock LLM | DeepSeek | 通义千问 | 文心一言 | 本地模型 |
|------|----------|----------|----------|----------|----------|
| **成本** | 免费 | 低 | 中 | 中 | 高（硬件） |
| **响应质量** | 低 | 高 | 高 | 高 | 中-高 |
| **中文能力** | N/A | 优秀 | 优秀 | 优秀 | 良好 |
| **响应速度** | 极快 | 快 | 中 | 中 | 取决于硬件 |
| **隐私性** | 高 | 中 | 中 | 中 | 极高 |
| **网络依赖** | 无 | 有 | 有 | 有 | 无 |
| **适用阶段** | 开发 | 测试/生产 | 生产 | 生产 | 生产 |

### 切换步骤

#### 1. 评估当前使用情况

```bash
# 查看 API 调用统计
# - 总调用次数
# - Token 消耗量
# - 平均响应时间
# - 错误率
```

#### 2. 选择新的 LLM 供应商

根据以下因素决策：
- **成本预算**
- **响应质量要求**
- **隐私和合规要求**
- **技术栈匹配度**

#### 3. 实现新的 LLM Service

```python
# app/services/new_llm_service.py
class NewLLMService:
    """新 LLM 供应商实现"""
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        # 实现具体调用逻辑
        pass
    
    async def health_check(self) -> bool:
        # 健康检查
        pass
```

#### 4. 更新依赖注入工厂

```python
# app/dependencies.py
def get_llm_service(settings: Settings) -> LLMServiceProtocol:
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "mock":
        return MockLLMService()
    elif provider == "deepseek":
        return DeepSeekLLMService(...)
    elif provider == "new_provider":
        return NewLLMService(...)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

#### 5. 更新配置并测试

```bash
# 更新 .env
LLM_PROVIDER=new_provider
NEW_PROVIDER_API_KEY=sk-xxxxx

# 重启服务
uvicorn app.main:app --reload

# 运行集成测试
pytest tests/integration/test_llm_integration.py
```

---

## 切换操作指南

### 快速切换命令

```bash
# Mock LLM（开发）
echo "LLM_PROVIDER=mock" >> .env

# DeepSeek（测试）
echo "LLM_PROVIDER=deepseek" >> .env
echo "DEEPSEEK_API_KEY=sk-xxxxx" >> .env

# 通义千问（生产）
echo "LLM_PROVIDER=qianwen" >> .env
echo "QIANWEN_API_KEY=sk-xxxxx" >> .env

# 重启服务
docker-compose restart backend
```

### 验证切换成功

```bash
# 1. 检查健康状态
curl http://localhost:8000/health

# 2. 查看日志
tail -f logs/app.log | grep "LLM"

# 3. 测试对话接口
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "user_message": "Hello", "token": "test-token"}'
```

---

## 最佳实践

### 开发阶段

✅ **推荐做法**：
- 默认使用 Mock LLM
- 专注于业务逻辑开发
- 完善情绪识别和短期记忆
- 编写单元测试和集成测试

❌ **避免做法**：
- 过早接入真实 LLM
- 在开发阶段消耗免费额度
- 忽略 Mock 响应的维护

### 测试阶段

✅ **推荐做法**：
- 切换到 DeepSeek 进行真实测试
- 优化 Prompt 工程
- 监控 API 调用和成本
- 准备降级策略

❌ **避免做法**：
- 忘记设置超时和重试
- 未实现降级逻辑
- 忽略成本监控

### 生产阶段

✅ **推荐做法**：
- 评估并选择合适的 LLM
- 配置监控和告警
- 实施严格的成本控制
- 准备多个备用方案

❌ **避免做法**：
- 单点依赖一个 LLM 供应商
- 未配置降级策略
- 忽略用户隐私和数据安全

---

## 常见问题（FAQ）

### Q1: Mock LLM 的响应能满足功能测试吗？

**答**：Mock LLM 适合验证基础流程（API 接口、数据流、情绪识别），但无法测试对话质量和用户体验。建议开发完成后切换到 DeepSeek 进行真实测试。

### Q2: DeepSeek 免费额度有多少？

**答**：具体额度请参考 DeepSeek 官方文档。建议：
- 注册后立即查看控制台
- 设置用量告警
- 规划测试用例，避免浪费

### Q3: 如何在不同环境使用不同的 LLM？

**答**：通过环境变量区分：

```bash
# 开发环境 (.env.development)
LLM_PROVIDER=mock

# 测试环境 (.env.testing)
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-test-key

# 生产环境 (.env.production)
LLM_PROVIDER=qianwen
QIANWEN_API_KEY=sk-prod-key
```

### Q4: LLM 调用失败怎么办？

**答**：系统已实现自动降级：

1. LLM 调用超时或失败
2. 自动使用 [config/llm_fallback_responses.md](../config/llm_fallback_responses.md) 中的静态响应
3. 记录错误日志
4. 继续服务用户

### Q5: 可以同时支持多个 LLM 供应商吗？

**答**：当前架构支持配置一个主用 LLM。如需多供应商支持：

```python
# 扩展工厂函数，支持主备策略
def get_llm_service(settings: Settings) -> LLMServiceProtocol:
    primary = get_primary_llm(settings)
    fallback = get_fallback_llm(settings)
    return LLMServiceWithFallback(primary, fallback)
```

### Q6: 如何评估不同 LLM 的效果？

**答**：建议采用 A/B 测试：

1. 准备测试数据集（100+ 条真实对话）
2. 分别用不同 LLM 生成响应
3. 评估指标：
   - 共情度（人工评分）
   - 响应时间
   - 成本
   - 用户满意度

---

## 附录

### A. 相关文档

- [需求文档](../demand.md) - 系统整体需求
- [架构文档](ARCHITECTURE.md) - LLM 可替换架构设计
- [开发指南](DEVELOPMENT.md) - 本地开发环境配置
- [部署文档](DEPLOYMENT.md) - 生产环境部署
- [LLM 降级响应](../config/llm_fallback_responses.md) - 静态降级响应模板
- [Prompt 模板](../config/prompt_template.md) - LLM Prompt 模板
- [危机干预协议](../config/crisis_intervention_protocols.md) - 危机干预规则

### B. 依赖包版本

```txt
# requirements.txt
openai==1.58.1              # DeepSeek 兼容 OpenAI SDK
dashscope==1.14.0           # 通义千问 SDK（可选）
```

### C. 监控指标

建议监控以下 LLM 相关指标：

- **调用次数**：每小时/每天 API 调用量
- **响应时间**：P50/P95/P99 延迟
- **错误率**：超时、失败、降级比例
- **Token 消耗**：输入/输出 token 数量
- **成本**：每日/每月 API 费用

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-02  
**维护者**: 模型团队（2人）
