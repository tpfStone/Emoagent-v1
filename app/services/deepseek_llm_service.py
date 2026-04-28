import asyncio
import logging

from openai import AsyncOpenAI

logger = logging.getLogger("emoagent")


class DeepSeekLLMService:
    """DeepSeek API 实现 - 通过 OpenAI 兼容接口调用"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate_response(
        self,
        prompt: str,
        timeout: float = 10.0,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                timeout=timeout,
            )
            return response.choices[0].message.content or ""
        except asyncio.TimeoutError:
            raise TimeoutError(f"DeepSeek API call timed out ({timeout}s)")
        except Exception as e:
            raise RuntimeError(f"DeepSeek API call failed: {e}")

    async def health_check(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
