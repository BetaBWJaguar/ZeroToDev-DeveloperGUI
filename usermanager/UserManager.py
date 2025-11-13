# -*- coding: utf-8 -*-
import json
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Optional

from PathHelper import PathHelper
from usermanager.ActivityManager import ActivityManager
from usermanager.UserManagerUtils import UserManagerUtils
from usermanager.user.User import User
from usermanager.user.UserStatus import UserStatus


class UserManager:
    def __init__(self, config_file: str = "database_config.json"):
        self.MAX_FAILED_ATTEMPTS = 4
        self.LOCK_TIME_MINUTES = 10
        config_path = PathHelper.resource_path(f"usermanager/{config_file}")
        if not config_path.exists():
            raise FileNotFoundError(f"Database config not found at {config_path.resolve()}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["users"]
        self.activity = ActivityManager(config_file)

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
            self.activity.log("unknown", "LOGIN_FAILED", f"Username not found: {username}")
            return "User not found."

        lock_until = user_doc.get("lock_until")
        if lock_until and datetime.utcnow() < lock_until:
            remaining = (lock_until - datetime.utcnow()).seconds // 60
            self.activity.log(user_doc["id"], "LOGIN_BLOCKED", f"Locked for {remaining} minutes")
            return f"⛔ Account locked. Try again in {remaining} minutes."

        if not UserManagerUtils.verify_password(password, user_doc["password"]):
            failed = user_doc.get("failed_attempts", 0) + 1

            self.activity.log(user_doc["id"], "LOGIN_FAILED", f"Failed attempt {failed}")

            if failed >= self.MAX_FAILED_ATTEMPTS:
                lock_until = datetime.utcnow() + timedelta(minutes=self.LOCK_TIME_MINUTES)

                self.collection.update_one(
                    {"id": user_doc["id"]},
                    {"$set": {"failed_attempts": failed, "lock_until": lock_until}}
                )

                self.activity.log(user_doc["id"], "ACCOUNT_LOCKED", f"Locked for {self.LOCK_TIME_MINUTES} minutes")
                return f"⛔ Too many failed attempts. Account locked for {self.LOCK_TIME_MINUTES} minutes."

            self.collection.update_one(
                {"id": user_doc["id"]},
                {"$set": {"failed_attempts": failed}}
            )

            attempts_left = self.MAX_FAILED_ATTEMPTS - failed
            return f"❗ Incorrect password. Attempts remaining: {attempts_left}"

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "failed_attempts": 0,
                "lock_until": None,
                "last_login": UserManagerUtils.timestamp()
            }}
        )

        self.activity.log(user_doc["id"], "LOGIN_SUCCESS")
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

    def logout_user(self, user_id: str):
        user_doc = self.collection.find_one({"id": user_id})
        if not user_doc:
            return "User not found."

        self.collection.update_one(
            {"id": user_id},
            {"$set": {"last_logout": UserManagerUtils.timestamp()}}
        )

        self.activity.log(user_id, "LOGOUT_SUCCESS", "User logged out successfully.")
        return "User logged out successfully."

