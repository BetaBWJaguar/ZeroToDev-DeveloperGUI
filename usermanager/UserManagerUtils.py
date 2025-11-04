# -*- coding: utf-8 -*-
import hashlib
import re
from datetime import datetime


class UserManagerUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return UserManagerUtils.hash_password(password) == hashed

    @staticmethod
    def validate_username(username: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9_.-]{3,20}$", username))

    @staticmethod
    def validate_password(password: str) -> bool:
        return bool(re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", password))

    @staticmethod
    def timestamp() -> str:
        return datetime.utcnow().isoformat()
