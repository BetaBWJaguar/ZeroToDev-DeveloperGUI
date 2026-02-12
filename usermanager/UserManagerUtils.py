# -*- coding: utf-8 -*-
import bcrypt
import re
from datetime import datetime


class UserManagerUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes,bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(input_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                input_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False


    @staticmethod
    def validate_username(username: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9_.-]{3,20}$", username))

    @staticmethod
    def validate_password(password: str) -> bool:
        if len(password) < 10:
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            return False
        return True

    @staticmethod
    def timestamp() -> str:
        return datetime.utcnow().isoformat()
