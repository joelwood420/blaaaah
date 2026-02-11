import os
import requests
from typing import Optional


GEMMA_API_URL = os.environ.get("")
GEMMA_API_KEY = os.environ.get("")


def _call_remote(prompt: str, max_tokens: int = 300) -> Optional[str]:
    """Call a configured Gemma-like HTTP API. The exact response schema may vary,
    so we try a few common shapes. Returns generated text on success or None.
    """
    if not GEMMA_API_URL or not GEMMA_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {GEMMA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt, "max_tokens": max_tokens}
    try:
        resp = requests.post(GEMMA_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # try common keys
        if isinstance(data, dict):
            if "text" in data and isinstance(data["text"], str):
                return data["text"]
            if "output" in data and isinstance(data["output"], str):
                return data["output"]
            if "generated_text" in data and isinstance(data["generated_text"], str):
                return data["generated_text"]
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                choice = data["choices"][0]
                if isinstance(choice, dict) and "text" in choice:
                    return choice["text"]
                if isinstance(choice, str):
                    return choice
        # fallback to raw text
        return resp.text
    except Exception:
        return None


def rewrite_notes(content: str, max_tokens: int = 300) -> str:
    """Rewrite bullet-point notes into a short daily reflection.

    If GEMMA_API_URL and GEMMA_API_KEY are configured in the environment this will
    attempt a remote call. Otherwise it falls back to a local heuristic rewrite so
    the feature can be tested offline.
    """
    prompt = (
        "Rewrite the following bullet-point notes into a concise, reflective daily "
        "reflection of about 150-250 words. Keep the tone first-person and introspective.\n\n"
        f"Notes:\n{content}\n\nReflection:\n"
    )

    # Try remote API
    remote = _call_remote(prompt, max_tokens=max_tokens)
    if remote:
        return remote.strip()

    # Fallback simple heuristic rewrite
    lines = [l.strip().lstrip("-*\u007f ") for l in content.splitlines() if l.strip()]
    if not lines:
        return "No notes to rewrite."
    # join bullets into sentences
    sentences = []
    for l in lines:
        if not l.endswith(('.', '?', '!')):
            sentences.append(l + '.')
        else:
            sentences.append(l)
    reflection = (
        "Today I reflected on the following points: "
        + " ".join(sentences)
        + " Overall, these observations made me consider what I can change or continue doing to improve my work and wellbeing." 
    )
    return reflection
