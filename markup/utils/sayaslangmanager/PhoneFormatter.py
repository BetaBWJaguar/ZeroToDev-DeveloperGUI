# -*- coding: utf-8 -*-
import json
import os
import re

def load_phone_patterns():
    path = os.path.join(os.path.dirname(__file__), "phone_formats.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

PHONE_PATTERNS = load_phone_patterns()

def format_phone_number(text: str, locale: str) -> str:
    text = text.strip().replace(" ", "")
    prefix = "artı " if locale == "tr" else "plus "
    digits = re.sub(r"\D", "", text)

    formatted = None
    for code, groups in PHONE_PATTERNS.items():
        if code != "default" and digits.startswith(code):
            parts = []
            i = 0
            for g in groups:
                parts.append(digits[i:i+g])
                i += g
                if i >= len(digits):
                    break
            formatted = " ".join(filter(None, parts))
            break

    if not formatted:
        default_group = PHONE_PATTERNS.get("default", [3])
        formatted = " ".join([digits[i:i+default_group[0]] for i in range(0, len(digits), default_group[0])])

    return f"{prefix}{formatted}"
