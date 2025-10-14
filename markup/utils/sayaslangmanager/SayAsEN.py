# -*- coding: utf-8 -*-
import re
from datetime import datetime

class SayAsEN:
    def interpret(self, text: str, interpret_as: str) -> str:
        interpret_as = interpret_as.strip().lower()

        if interpret_as == "digits":
            return " ".join(list(text))
        elif interpret_as == "spell-out":
            return " ".join(list(text.upper()))
        elif interpret_as == "date":
            try:
                dt = datetime.strptime(text.strip(), "%Y-%m-%d")
                return dt.strftime("%B %d %Y")
            except Exception:
                return text
        elif interpret_as == "time":
            try:
                t = datetime.strptime(text.strip(), "%H:%M")
                return t.strftime("%I:%M %p")
            except Exception:
                return text
        elif interpret_as == "telephone":
            spoken = text.replace("+", "plus ")
            return " ".join(re.findall(r"\d", spoken))
        elif interpret_as == "currency":
            return f"{text} dollars"
        else:
            return text
