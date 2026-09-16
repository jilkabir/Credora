#!/usr/bin/env python3
"""Provider adapters for Credora draft generation.

API keys are read from environment variables only. No secret is written to disk.
Uses Python's standard library so Credora does not require provider SDK packages.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODELS = {
    "openai": "gpt-5.6-terra",
    "anthropic": "claude-sonnet-5",
}


def _post_json(url: str, headers: dict[str, str], payload: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            message = parsed.get("error", {}).get("message") or body
        except json.JSONDecodeError:
            message = body
        raise RuntimeError(f"Provider API error ({exc.code}): {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach provider API: {exc.reason}") from exc
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Provider returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Provider returned an unexpected response")
    return result


def _prompt(request: dict) -> str:
    safe_request = {
        "task": request.get("task", {}),
        "platform_rules": request.get("platform_rules", ""),
        "personalization": request.get("personalization", {}),
        "instructions": request.get("instructions", []),
        "warnings": request.get("warnings", []),
    }
    return (
        "You are Credora's drafting model. Follow the supplied context exactly. "
        "Do not invent unsupported personal facts or results. Return only the final social-media draft, "
        "with no analysis, labels, markdown fences, or explanation.\n\n"
        + json.dumps(safe_request, ensure_ascii=False, indent=2)
    )


def _openai_text(response: dict) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    texts = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for block in item.get("content", []):
            if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                value = block.get("text")
                if isinstance(value, str) and value.strip():
                    texts.append(value.strip())
    if not texts:
        raise RuntimeError("OpenAI response contained no draft text")
    return "\n".join(texts).strip()


def _anthropic_text(response: dict) -> str:
    texts = []
    for block in response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            value = block.get("text")
            if isinstance(value, str) and value.strip():
                texts.append(value.strip())
    if not texts:
        raise RuntimeError("Anthropic response contained no draft text")
    return "\n".join(texts).strip()


def generate(request: dict, provider: str, model: str | None = None, timeout: int = 120) -> dict:
    provider = provider.strip().lower()
    if provider not in DEFAULT_MODELS:
        raise ValueError("Provider must be 'openai' or 'anthropic'")
    selected_model = model or DEFAULT_MODELS[provider]
    prompt = _prompt(request)

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        response = _post_json(
            OPENAI_URL,
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            {"model": selected_model, "input": prompt},
            timeout,
        )
        text = _openai_text(response)
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        response = _post_json(
            ANTHROPIC_URL,
            {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            {"model": selected_model, "max_tokens": 3000, "messages": [{"role": "user", "content": prompt}]},
            timeout,
        )
        text = _anthropic_text(response)

    return {"provider": provider, "model": selected_model, "text": text}
