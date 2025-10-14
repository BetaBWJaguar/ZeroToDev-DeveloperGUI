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
                aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
                return f"{dt.day} {aylar[dt.month - 1]} {dt.year}"
            except Exception:
                return text
        elif interpret_as == "time":
            try:
                t = datetime.strptime(text.strip(), "%H:%M")
                saat = f"{t.hour} {t.minute}"
                return f"{saat} {'akşam' if t.hour >= 12 else 'sabah'}"
            except Exception:
                return text
        elif interpret_as == "telephone":
            spoken = text.replace("+", "artı ")
            return " ".join(re.findall(r"\d", spoken))
        elif interpret_as == "currency":
            return f"{text} lira"
        else:
            return text
