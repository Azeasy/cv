"""Translation API backends: DeepL (primary) and OpenAI (optional)."""

import json
import urllib.parse
import urllib.request


def translate_deepl(texts: list[str], api_key: str) -> list[str]:
    endpoint = "https://api-free.deepl.com/v2/translate"
    # Header-based auth (DeepL-Auth-Key) per 2025 deprecation of legacy form-body auth_key.
    data = urllib.parse.urlencode(
        [("target_lang", "RU")] + [("text", t) for t in texts],
    ).encode()
    req = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": f"DeepL-Auth-Key {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return [t["text"] for t in result["translations"]]


def translate_openai(texts: list[str], api_key: str) -> list[str]:
    endpoint = "https://api.openai.com/v1/chat/completions"
    translations = []
    for text in texts:
        payload = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Translate the following "
                        "CV bullet point from English to Russian. Return only the "
                        "translated text, preserving LaTeX commands (\\textbf{}, etc.) "
                        "exactly as-is."
                    ),
                },
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        }).encode()
        req = urllib.request.Request(
            endpoint, data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        translations.append(result["choices"][0]["message"]["content"].strip())
    return translations
