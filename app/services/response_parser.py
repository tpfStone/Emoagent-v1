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
