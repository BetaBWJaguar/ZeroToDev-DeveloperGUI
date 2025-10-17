# -*- coding: utf-8 -*-
import json
import os
import re
from typing import Dict, List


def load_phone_patterns() -> Dict[str, List[int]]:
    path = os.path.join(os.path.dirname(__file__), "Phone_formats.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


PHONE_PATTERNS = load_phone_patterns()


def format_phone_number(text: str) -> str:
    text = text.strip().replace(" ", "")
    digits = re.sub(r"\D", "", text)

    prefix = "plus"

    groups = None
    for code, pattern in PHONE_PATTERNS.items():
        if code == "default":
            continue
        if digits.startswith(code):
            groups = pattern
            break
    if not groups:
        groups = PHONE_PATTERNS.get("default", [3, 3, 3])

    grouped_numbers = []
    i = 0
    for size in groups:
        part = digits[i:i + size]
        if not part:
            break

        if len(part) > 4:
            subparts = [part[j:j + 3] for j in range(0, len(part), 3)]
            grouped_numbers.extend(subparts)
        else:
            grouped_numbers.append(part)

        i += size
        if i >= len(digits):
            break

    formatted = f"{prefix} " + ", ".join(grouped_numbers)
    return formatted
