import json
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient

from PathHelper import PathHelper
from usermanager.ActivityManager import ActivityManager
from usermanager.UserManagerUtils import UserManagerUtils
from usermanager.user.User import User
from usermanager.user.UserStatus import UserStatus

from data_manager.MemoryManager import MemoryManager
from language_manager.LangManager import LangManager


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

        langs_dir = PathHelper.resource_path("langs")
        ui_lang = MemoryManager.get("ui_language", "english")

        self.lang = LangManager(langs_dir=langs_dir, default_lang=ui_lang)

    def register_user(self, username: str, email: str, password: str,
                      first_name: str, last_name: str):

        if not UserManagerUtils.validate_username(username):
            return self.lang.get("user_register_invalid_username")

        if not UserManagerUtils.validate_password(password):
            return self.lang.get("user_register_invalid_password")

        if self.collection.find_one({"username": username}):
            return self.lang.get("user_register_username_exists")

        if self.collection.find_one({"email": email}):
            return self.lang.get("user_register_email_exists")

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
            "message": self.lang.get("user_register_success"),
            "verify_token": user.email_verification_token
        }

    def login_user(self, username: str, password: str):
        user_doc = self.collection.find_one({"username": username})
        if not user_doc:
            self.activity.log("unknown", "LOGIN_FAILED", f"Username not found: {username}")
            return self.lang.get("user_login_not_found")

        lock_until = user_doc.get("lock_until")
        if lock_until and datetime.utcnow() < lock_until:
            remaining = (lock_until - datetime.utcnow()).seconds // 60
            return self.lang.get("user_login_locked").format(remaining)

        if not UserManagerUtils.verify_password(password, user_doc["password"]):
            failed = user_doc.get("failed_attempts", 0) + 1

            if failed >= self.MAX_FAILED_ATTEMPTS:
                lock_until = datetime.utcnow() + timedelta(minutes=self.LOCK_TIME_MINUTES)
                self.collection.update_one(
                    {"id": user_doc["id"]},
                    {"$set": {"failed_attempts": failed, "lock_until": lock_until}}
                )
                return self.lang.get("user_login_locked").format(self.LOCK_TIME_MINUTES)

            self.collection.update_one(
                {"id": user_doc["id"]},
                {"$set": {"failed_attempts": failed}}
            )

            attempts_left = self.MAX_FAILED_ATTEMPTS - failed
            return self.lang.get("user_login_incorrect_password").format(attempts_left)

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "failed_attempts": 0,
                "lock_until": None,
                "last_login": UserManagerUtils.timestamp()
            }}
        )
        user = User(user_doc)

        return user

    def request_password_reset(self, email: str):
        user_doc = self.collection.find_one({"email": email})
        if not user_doc:
            return self.lang.get("user_login_not_found")

        token = str(uuid.uuid4())
        self.collection.update_one(
            {"email": email},
            {"$set": {"password_reset_token": token}}
        )

        return {
            "message": self.lang.get("user_reset_token_created"),
            "reset_token": token
        }

    def reset_password(self, token: str, new_password: str):
        if not UserManagerUtils.validate_password(new_password):
            return self.lang.get("user_register_invalid_password")

        user_doc = self.collection.find_one({"password_reset_token": token})
        if not user_doc:
            return self.lang.get("user_reset_invalid_token")

        hashed_pw = UserManagerUtils.hash_password(new_password)
        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {"password": hashed_pw, "password_reset_token": None}}
        )

        return self.lang.get("user_reset_success")

    def delete_user(self, user_id: str):
        result = self.collection.delete_one({"id": user_id})
        if result.deleted_count > 0:
            return self.lang.get("user_delete_success")
        return self.lang.get("user_delete_not_found")
