"""LLM provider layer. Zero dependencies — pure stdlib HTTP.

Picks a provider automatically:
  1. If ANTHROPIC_API_KEY is set  -> Anthropic API
  2. Else if GEMINI_API_KEY is set -> Google Gemini API
  3. Else if GROQ_API_KEY is set   -> Groq API (OpenAI-compatible)
  4. Else if Ollama is reachable  -> local model (no key, fully offline)
"""

import json
import os
import urllib.error
import urllib.request

SYSTEM_PROMPT = (
    "You are `oops`, a CLI that fixes failed shell commands. "
    "You are given the command the user ran and the error output it produced. "
    "Respond with ONLY a JSON object, no markdown and no backticks, of the form: "
    '{"explanation": "<one short sentence on what went wrong>", '
    '"command": "<the corrected shell command to run>"}. '
    "The corrected command must be a single line, runnable as-is. "
    "If you cannot determine a fix, set command to an empty string."
)

OLLAMA_URL = os.environ.get("OOPS_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OOPS_OLLAMA_MODEL", "llama3.2")
ANTHROPIC_MODEL = os.environ.get("OOPS_MODEL", "claude-haiku-4-5-20251001")
GEMINI_MODEL = os.environ.get("OOPS_GEMINI_MODEL", "gemini-2.0-flash")
GROQ_MODEL = os.environ.get("OOPS_GROQ_MODEL", "llama-3.3-70b-versatile")


class LLMError(Exception):
    pass


def _build_user_prompt(command: str, output: str) -> str:
    return (
        f"Command:\n{command}\n\n"
        f"Error output:\n{output.strip() or '(no output captured)'}"
    )


def _parse_json(text: str) -> dict:
    text = text.strip()
    # Strip code fences if the model added them anyway.
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text[3:] else text[3:]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    text = text.strip().strip("`").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Last-ditch: find the first {...} block.
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise LLMError(f"Model did not return JSON:\n{text}")
        data = json.loads(text[start : end + 1])
    return {
        "explanation": str(data.get("explanation", "")).strip(),
        "command": str(data.get("command", "")).strip(),
    }


def _post(url: str, payload: dict, headers: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            # Some APIs (Groq) sit behind Cloudflare, which blocks the default
            # "Python-urllib" agent with a 403/1010. Send a plain app identifier.
            "User-Agent": "oops-cli/0.1",
            **headers,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise LLMError(f"HTTP {e.code}: {e.read().decode()[:300]}") from e
    except urllib.error.URLError as e:
        raise LLMError(f"Could not reach {url}: {e.reason}") from e


def _ask_anthropic(command: str, output: str) -> dict:
    data = _post(
        "https://api.anthropic.com/v1/messages",
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 300,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": _build_user_prompt(command, output)}],
        },
        {
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return _parse_json(text)


def _ask_gemini(command: str, output: str) -> dict:
    # Key goes in a header, never in the URL query string.
    data = _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": _build_user_prompt(command, output)}]}],
            "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 300},
        },
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
    )
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise LLMError(f"Unexpected Gemini response: {json.dumps(data)[:300]}")
    return _parse_json(text)


def _ask_groq(command: str, output: str) -> dict:
    # Groq is OpenAI-compatible.
    data = _post(
        "https://api.groq.com/openai/v1/chat/completions",
        {
            "model": GROQ_MODEL,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(command, output)},
            ],
        },
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
    )
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise LLMError(f"Unexpected Groq response: {json.dumps(data)[:300]}")
    return _parse_json(text)


def _ask_ollama(command: str, output: str) -> dict:
    data = _post(
        f"{OLLAMA_URL}/api/generate",
        {
            "model": OLLAMA_MODEL,
            "system": SYSTEM_PROMPT,
            "prompt": _build_user_prompt(command, output),
            "stream": False,
            "format": "json",
        },
        {},
    )
    return _parse_json(data.get("response", ""))


def _ollama_available() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def suggest_fix(command: str, output: str) -> dict:
    """Return {'explanation': str, 'command': str} or raise LLMError."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return _ask_anthropic(command, output)
    if os.environ.get("GEMINI_API_KEY"):
        return _ask_gemini(command, output)
    if os.environ.get("GROQ_API_KEY"):
        return _ask_groq(command, output)
    if _ollama_available():
        return _ask_ollama(command, output)
    raise LLMError(
        "No LLM provider available.\n"
        "  Set ANTHROPIC_API_KEY, GEMINI_API_KEY or GROQ_API_KEY, or run a "
        "local model with Ollama (https://ollama.com)."
    )