from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "config" / "prompt_template.md"

_PROMPT_TEMPLATE: str | None = None


def _load_template() -> str:
    """加载 prompt_template.md，跳过文档头部元信息（--- 分隔线之前）"""
    raw = TEMPLATE_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i + 1
            break
    return "\n".join(lines[start:]).strip()


def _get_template() -> str:
    global _PROMPT_TEMPLATE
    if _PROMPT_TEMPLATE is None:
        _PROMPT_TEMPLATE = _load_template()
    return _PROMPT_TEMPLATE


def build_emotion_prompt(user_message: str, emotion: str, memory: list[dict]) -> str:
    """加载 prompt_template.md 并注入运行时变量，构建最终 Prompt"""
    template = _get_template()

    memory_text = "\n".join(
        [f"User: {m['user']}\nAssistant: {m['assistant']}" for m in memory[-6:]]
    )

    prompt = template.replace("{{user_input}}", user_message).replace(
        "{{detected_emotion}}", emotion
    )

    if memory_text:
        prompt += f"\n\n**Recent Conversation History:**\n{memory_text}"

    return prompt
