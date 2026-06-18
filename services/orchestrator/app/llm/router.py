import os
from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

TaskType = Literal["light", "heavy"]


def get_llm(task_type: TaskType = "light"):
    """根据任务类型路由到本地或云端 LLM"""

    if task_type == "light":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
            temperature=0.3,
        )

    provider = os.getenv("CLOUD_LLM_PROVIDER", "anthropic")
    if provider == "anthropic":
        return ChatAnthropic(
            model=os.getenv("CLOUD_LLM_MODEL", "claude-sonnet-4-20250514"),
            api_key=os.getenv("CLOUD_LLM_API_KEY"),
            temperature=0.7,
        )
    elif provider == "openai":
        return ChatOpenAI(
            model=os.getenv("CLOUD_LLM_MODEL", "gpt-4o"),
            api_key=os.getenv("CLOUD_LLM_API_KEY"),
            temperature=0.7,
        )
    else:
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
            temperature=0.7,
        )