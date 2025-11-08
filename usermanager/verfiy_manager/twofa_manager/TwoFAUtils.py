# -*- coding: utf-8 -*-
import pyotp
import re


class TwoFAUtils:

    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def verify_code_format(code: str) -> bool:
        return bool(re.match(r"^[0-9]{6}$", code))

    @staticmethod
    def get_totp(secret: str) -> pyotp.TOTP:
        return pyotp.TOTP(secret)
