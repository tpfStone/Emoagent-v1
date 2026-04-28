import asyncio
from typing import Protocol


class LLMServiceProtocol(Protocol):
    async def generate_response(
        self,
        prompt: str,
        timeout: float = 10.0,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str: ...

    async def health_check(self) -> bool: ...


class MockLLMService:
    """Mock LLM 实现 - 用于开发阶段快速验证流程"""

    def __init__(self):
        self.emotion_responses = {
            "sadness": (
                "I can sense you're going through a tough time right now. "
                "It's important to allow yourself to feel these emotions. "
                "Would you like to talk about what happened?"
            ),
            "joy": (
                "It sounds like you're in a great mood! "
                "Would you like to share what's making you happy?"
            ),
            "anger": (
                "I understand you're feeling angry right now. "
                "Anger is a completely normal emotion. "
                "Let's look at what's causing you to feel this way."
            ),
            "fear": (
                "I notice you might be feeling anxious or worried. "
                "These feelings aren't easy to face, but you're not alone."
            ),
            "love": (
                "I can feel the warmth and love in your words. "
                "That's a beautiful emotion."
            ),
            "surprise": "It sounds like something unexpected happened!",
        }
        self.default_response = (
            "Thank you for sharing that with me. I'm here to listen. Please go on."
        )

    async def generate_response(
        self,
        prompt: str,
        timeout: float = 10.0,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        await asyncio.sleep(0.3)

        prompt_lower = prompt.lower()
        for emotion, response in self.emotion_responses.items():
            if emotion in prompt_lower:
                return response
        return self.default_response

    async def health_check(self) -> bool:
        return True
