# -*- coding: utf-8 -*-
import json
import uuid
from pathlib import Path
from pymongo import MongoClient
from typing import Optional

from usermanager.UserManagerUtils import UserManagerUtils
from usermanager.user.User import User
from usermanager.user.UserStatus import UserStatus


class UserManager:
    def __init__(self, config_file: str = "database_config.json"):
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["users"]

    def register_user(self, username: str, email: str, password: str,
                      first_name: str, last_name: str):

        if not UserManagerUtils.validate_username(username):
            return "Invalid username format."

        if not UserManagerUtils.validate_password(password):
            return "Password must include an uppercase letter and a number (min 8 chars)."

        if self.collection.find_one({"username": username}):
            return "Username already exists."

        if self.collection.find_one({"email": email}):
            return "Email already registered."

        hashed_pw = UserManagerUtils.hash_password(password)
        user = User.create(
            username=username,
            email=email,
            password=hashed_pw,
            first_name=first_name,
            last_name=last_name,
            status=UserStatus.PENDING
        )

        self.collection.insert_one(user.to_dict())

        return {
            "message": f"✅ User '{username}' registered successfully. Email verification required.",
            "verify_token": user.email_verification_token
        }

    def login_user(self, username: str, password: str):
        user_doc = self.collection.find_one({"username": username})
        if not user_doc:
            return "User not found."

        if not UserManagerUtils.verify_password(password, user_doc["password"]):
            return "Incorrect password."

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {"last_login": UserManagerUtils.timestamp()}}
        )

        return User.from_dict(user_doc)

    def request_password_reset(self, email: str):
        user_doc = self.collection.find_one({"email": email})
        if not user_doc:
            return "❗ Email not registered."

        token = str(uuid.uuid4())

        self.collection.update_one(
            {"email": email},
            {"$set": {"password_reset_token": token}}
        )

        return {
            "message": "🔐 Password reset token generated.",
            "reset_token": token
        }

    def reset_password(self, token: str, new_password: str):
        if not UserManagerUtils.validate_password(new_password):
            return "⚠️ Password must include uppercase and number (min 8 chars)."

        user_doc = self.collection.find_one({"password_reset_token": token})
        if not user_doc:
            return "❗ Invalid or expired token."

        hashed_pw = UserManagerUtils.hash_password(new_password)

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {"password": hashed_pw, "password_reset_token": None}}
        )

        return "✅ Password reset successfully."

    def get_user(self, user_id: str) -> Optional[User]:
        user_doc = self.collection.find_one({"id": user_id}, {"password": 0})
        return User.from_dict(user_doc) if user_doc else None

    def delete_user(self, user_id: str):
        result = self.collection.delete_one({"id": user_id})
        if result.deleted_count > 0:
            return f"User with ID '{user_id}' deleted successfully."
        return "User not found."
