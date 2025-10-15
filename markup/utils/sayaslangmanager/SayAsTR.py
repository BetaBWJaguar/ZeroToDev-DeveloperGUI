# -*- coding: utf-8 -*-
import re
from datetime import datetime

from markup.utils.sayaslangmanager.PhoneFormatter import format_phone_number


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
            try:
                t = datetime.strptime(text.strip(), "%H:%M")
                return f"{t.hour} {t.minute} {'akşam' if t.hour >= 12 else 'sabah'}"
            except Exception:
                return text

        elif interpret_as == "telephone":
            return format_phone_number(text, "tr")

        elif interpret_as == "currency":
            return f"{text} lira"

        elif interpret_as == "temperature":
            temp = text.upper().replace("C", "").replace("°", "").strip()
            return f"{temp} derece"

        else:
            return text
