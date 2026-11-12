"""Optional language-model polish for explanations.

Puzzle Coach is fully usable offline: the rule-search engine and the
template explanations do not need a network or an API key.

If the user sets PUZZLECOACH_LLM_KEY (or OPENAI_API_KEY) and optionally
PUZZLECOACH_LLM_BASE / PUZZLECOACH_LLM_MODEL, this module may rephrase an
already-verified explanation. The model is never asked to invent or choose
the rule — that would be unfaithful tutoring.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

SYSTEM = (
    "You are a patient puzzle tutor. Rephrase the given, already-verified "
    "explanation in clear, friendly English (or Chinese if the user text is "
    "Chinese). Do not change the rule, add new claims, or invent steps. "
    "Keep it under 120 words. Return plain text only."
)


def llm_configured() -> bool:
    return bool(os.environ.get("PUZZLECOACH_LLM_KEY") or os.environ.get("OPENAI_API_KEY"))


def polish(text: str, timeout: float = 8.0) -> dict:
    key = os.environ.get("PUZZLECOACH_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"ok": False, "reason": "no-key", "text": text}
    base = os.environ.get("PUZZLECOACH_LLM_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("PUZZLECOACH_LLM_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
    }
    req = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        out = data["choices"][0]["message"]["content"].strip()
        if not out:
            return {"ok": False, "reason": "empty", "text": text}
        return {"ok": True, "reason": "polished", "text": out, "model": model}
    except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": str(exc), "text": text}
