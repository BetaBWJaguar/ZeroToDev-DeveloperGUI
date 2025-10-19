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
            parts = text.strip().split("|", 1)
            time_str = parts[0].strip()
            custom_context = parts[1].strip().lower() if len(parts) > 1 else None

            try:
                t = datetime.strptime(time_str, "%H:%M")
                context = t.strftime("%p").lower()

                if custom_context:
                    context = custom_context
                hour = t.strftime("%I").lstrip("0") or "12"
                minute = t.strftime("%M")
                return f"{hour} {minute} {context}"
            except Exception:
                return text


        elif interpret_as == "telephone":
            return format_phone_number(text)

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

        elif interpret_as == "ordinal":
            try:
                n = int(text)
                suffix = "th"
                if n % 10 == 1 and n % 100 != 11:
                    suffix = "st"
                elif n % 10 == 2 and n % 100 != 12:
                    suffix = "nd"
                elif n % 10 == 3 and n % 100 != 13:
                    suffix = "rd"
                return f"{n}{suffix}"
            except Exception:
                return text

        elif interpret_as == "fraction":
            if "/" in text:
                num, denom = text.split("/", 1)
                num, denom = num.strip(), denom.strip()
                fraction_map = {
                    "2": "half", "3": "third", "4": "quarter",
                    "5": "fifth", "6": "sixth", "7": "seventh",
                    "8": "eighth", "9": "ninth", "10": "tenth"
                }
                word = fraction_map.get(denom, f"over {denom}")
                return f"{num} {word}" if num != "1" else word
            return text

        elif interpret_as == "measurement":
            unit_patterns = {
                "km": "kilometers", "m": "meters", "cm": "centimeters",
                "mm": "millimeters", "kg": "kilograms", "g": "grams",
                "l": "liters", "ml": "milliliters"
            }
            for unit, word in unit_patterns.items():
                if text.lower().endswith(unit):
                    num = re.sub(r"[^0-9.,]", "", text)
                    return f"{num} {word}"
            return text

        else:
            return text
