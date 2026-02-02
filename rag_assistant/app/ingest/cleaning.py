from __future__ import annotations

import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text)
    return normalized.strip()
