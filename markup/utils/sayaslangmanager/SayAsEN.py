# -*- coding: utf-8 -*-
import re
from datetime import datetime

from markup.utils.sayaslangmanager.PhoneFormatter import format_phone_number


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
                return t.strftime("%I %M %p").lstrip("0")
            except Exception:
                return text

        elif interpret_as == "telephone":
            return format_phone_number(text, "en")

        elif interpret_as == "currency":
            try:
                amount = float(text)
                unit = "dollar" if amount == 1 else "dollars"
                return f"{text} {unit}"
            except Exception:
                return f"{text} dollars"

        elif interpret_as == "temperature":
            temp = text.upper().replace("°", "").strip()
            if "C" in temp:
                temp = temp.replace("C", "").strip()
                return f"{temp} degrees Celsius"
            elif "F" in temp:
                temp = temp.replace("F", "").strip()
                return f"{temp} degrees Fahrenheit"
            else:
                return f"{temp} degrees"

        else:
            return text
