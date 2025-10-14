# -*- coding: utf-8 -*-
from markup.utils.sayaslangmanager.SayAsEN import SayAsEN
from markup.utils.sayaslangmanager.SayAsTR import SayAsTR


class SayAsTagManager:
    def __init__(self, locale: str = "en"):
        self.locale = locale.split("-")[0].lower()
        self.strategies = {
            "english": SayAsEN(),
            "turkish": SayAsTR(),
        }

    def interpret(self, text: str, interpret_as: str) -> str:
        strategy = self.strategies.get(self.locale, self.strategies["en"])
        return strategy.interpret(text, interpret_as)
