"""
AlphaAlign — Multi-Provider LLM Client.

Supports OpenAI, Anthropic, Ollama, LM Studio, Azure OpenAI,
and any OpenAI-compatible endpoint.
"""

import json
from typing import Dict, Optional
import httpx


# Default endpoints per provider
PROVIDER_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "ollama": "http://127.0.0.1:11434/v1/chat/completions",
    "lmstudio": "http://127.0.0.1:1234/v1/chat/completions",
    "azure": "",  # User must configure
    "custom": "",  # User must configure
}


async def call_llm(
    provider: str,
    model: str,
    prompt: str,
    system_prompt: str = "",
    endpoint: str = "",
    api_key: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> Dict:
    """
    Call an LLM provider and return the response.

    Returns:
        Dict with: text, provider, model, tokens_used
    """
    url = endpoint or PROVIDER_ENDPOINTS.get(provider, "")
    if not url:
        return {"text": "", "error": f"No endpoint configured for provider: {provider}"}

    try:
        if provider == "anthropic":
            return await _call_anthropic(url, api_key, model, prompt, system_prompt, temperature, max_tokens)
        else:
            # OpenAI-compatible (works for OpenAI, Ollama, LM Studio, Azure, custom)
            return await _call_openai_compatible(url, api_key, model, prompt, system_prompt, temperature, max_tokens)
    except httpx.ConnectError:
        return {"text": "", "error": f"Cannot connect to {provider} at {url}. Is it running?"}
    except Exception as e:
        return {"text": "", "error": str(e)}


async def _call_openai_compatible(
    url: str, api_key: str, model: str,
    prompt: str, system_prompt: str,
    temperature: float, max_tokens: int,
) -> Dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})

    return {
        "text": text,
        "provider": "openai-compatible",
        "model": model,
        "tokens_used": usage.get("total_tokens", 0),
    }


async def _call_anthropic(
    url: str, api_key: str, model: str,
    prompt: str, system_prompt: str,
    temperature: float, max_tokens: int,
) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    usage = data.get("usage", {})
    return {
        "text": text,
        "provider": "anthropic",
        "model": model,
        "tokens_used": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
    }


async def test_connection(
    provider: str, endpoint: str = "", api_key: str = "", model: str = "",
) -> Dict:
    """Test connectivity to an LLM provider."""
    try:
        result = await call_llm(
            provider=provider,
            model=model or "test",
            prompt="Say hello in one word.",
            endpoint=endpoint,
            api_key=api_key,
            max_tokens=10,
        )
        if result.get("error"):
            return {"connected": False, "error": result["error"]}
        return {"connected": True, "model": model}
    except Exception as e:
        return {"connected": False, "error": str(e)}
