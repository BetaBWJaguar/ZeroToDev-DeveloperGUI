# -*- coding: utf-8 -*-
import re
from datetime import datetime


class SayAsTR:
    def interpret(self, text: str, interpret_as: str) -> str:
        interpret_as = interpret_as.strip().lower()

        if interpret_as == "digits":
            return " ".join(list(text))

        elif interpret_as == "spell-out":
            return " ".join(list(text.upper()))

        elif interpret_as == "date":
            try:
                dt = datetime.strptime(text.strip(), "%Y-%m-%d")
                aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                         "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                return f"{dt.day} {aylar[dt.month - 1]} {dt.year}"
            except Exception:
                return text

        elif interpret_as == "time":
            parts = text.strip().split("|", 1)
            time_str = parts[0].strip()
            context_en = parts[1].strip().lower() if len(parts) > 1 else None

            context_map = {
                "morning": "sabah",
                "afternoon": "öğleden sonra",
                "evening": "akşam",
                "night": "gece"
            }

            try:
                t = datetime.strptime(time_str, "%H:%M")
                if context_en:
                    context = context_map.get(context_en, context_en)
                else:
                    if 5 <= t.hour < 12:
                        context = "sabah"
                    elif 12 <= t.hour < 17:
                        context = "öğleden sonra"
                    elif 17 <= t.hour < 22:
                        context = "akşam"
                    else:
                        context = "gece"

                return f"{t.hour} {t.minute} {context}"
            except Exception:
                return text

        elif interpret_as == "currency":
            return f"{text} lira"

        elif interpret_as == "temperature":
            temp = text.upper().replace("C", "").replace("°", "").strip()
            return f"{temp} derece"

        elif interpret_as == "math":
            math_map = {
                "+": "artı",
                "-": "eksi",
                "*": "çarpı",
                "x": "çarpı",
                "/": "bölü",
                "=": "eşittir"
            }

            result = text
            for sym, word in math_map.items():
                result = re.sub(rf"\s*{re.escape(sym)}\s*", f" {word} ", result)

            result = re.sub(r"^\s*-\s*(\d+)", r"eksi \1", result)

            result = re.sub(r"\s+", " ", result).strip()
            return result

        elif interpret_as == "ordinal":
            try:
                n = int(text)
                suffix_map = {
                    1: "birinci", 2: "ikinci", 3: "üçüncü", 4: "dördüncü",
                    5: "beşinci", 6: "altıncı", 7: "yedinci", 8: "sekizinci",
                    9: "dokuzuncu", 10: "onuncu", 20: "yirminci", 30: "otuzuncu"
                }
                if n in suffix_map:
                    return suffix_map[n]
                return f"{text}. inci"
            except Exception:
                return text

        elif interpret_as == "fraction":
            if "/" in text:
                num, denom = text.split("/", 1)
                num, denom = num.strip(), denom.strip()
                fraction_map = {
                    "2": "yarım", "3": "üçte bir", "4": "dörtte bir",
                    "5": "beşte bir", "6": "altıda bir", "10": "onda bir"
                }
                if num == "1" and denom in fraction_map:
                    return fraction_map[denom]
                return f"{num} bölü {denom}"
            return text

        elif interpret_as == "measurement":
            unit_patterns = {
                "km": "kilometre", "m": "metre", "cm": "santimetre",
                "mm": "milimetre", "kg": "kilogram", "g": "gram",
                "l": "litre", "ml": "mililitre"
            }
            for unit, word in unit_patterns.items():
                if text.lower().endswith(unit):
                    num = re.sub(r"[^0-9.,]", "", text)
                    return f"{num} {word}"
            return text

        else:
            return text