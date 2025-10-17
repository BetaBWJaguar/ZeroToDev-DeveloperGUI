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
                result = result.replace(sym, f" {word} ")

            result = re.sub(r"(\d)", r" \1 ", result)
            return re.sub(r"\s+", " ", result.strip())

        else:
            return text