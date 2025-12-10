import json
import secrets
import string
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
    def __init__(self,lang: dict, config_file: str = "database_config.json"):
        self.MAX_FAILED_ATTEMPTS = 4
        self.LOCK_TIME_MINUTES = 10
        self.lang = lang

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
            self.activity.log(username, "REGISTER_FAILED", "Invalid username format")
            return self.lang.get("user_register_invalid_username")


        if not UserManagerUtils.validate_password(password):
            self.activity.log(username, "REGISTER_FAILED", "Weak/invalid password")
            return self.lang.get("user_register_invalid_password")


        if self.collection.find_one({"username": username}):
            self.activity.log(username, "REGISTER_FAILED", "Username already exists")
            return self.lang.get("user_register_username_exists")


        if self.collection.find_one({"email": email}):
            self.activity.log(username, "REGISTER_FAILED", "Email already exists")
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
        self.activity.log(username, "REGISTER_SUCCESS", "User registered successfully")

        try:
            from usermanager.verfiy_manager.VerifyUtils import VerifyUtils
            verify_utils = VerifyUtils(lang_manager=self.lang)

            verify_utils.send_verification_email(
                to_email=email,
                token=user.email_verification_token,
                app_url="http://localhost:9090"
            )

            self.activity.log(username, "REGISTER_EMAIL_SENT", "Verification email sent")

        except Exception as e:
            self.activity.log(username, "REGISTER_EMAIL_FAILED", str(e))

        return {
            "message": self.lang.get("user_register_success"),
            "verify_token": user.email_verification_token
        }

    def login_user(self, username: str, password: str):
        user_doc = self.collection.find_one({"username": username})

        if not user_doc:
            self.activity.log("unknown", "LOGIN_FAILED", f"User not found: {username}")
            return self.lang.get("user_login_not_found")


        lock_until = user_doc.get("lock_until")
        if lock_until and datetime.utcnow() < lock_until:
            remaining = (lock_until - datetime.utcnow()).seconds // 60
            self.activity.log(username, "LOGIN_LOCKED",
                              f"Account locked for {remaining} minutes")
            return self.lang.get("user_login_locked").format(remaining)


        if not UserManagerUtils.verify_password(password, user_doc["password"]):
            failed_attempts = user_doc.get("failed_attempts", 0) + 1

            if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                lock_until = datetime.utcnow() + timedelta(minutes=self.LOCK_TIME_MINUTES)

                self.collection.update_one(
                    {"id": user_doc["id"]},
                    {"$set": {"failed_attempts": failed_attempts, "lock_until": lock_until}}
                )

                self.activity.log(username, "LOGIN_FAILED_LOCKED",
                                  f"Too many attempts ({failed_attempts})")

                return self.lang.get("user_login_locked").format(self.LOCK_TIME_MINUTES)

            self.collection.update_one(
                {"id": user_doc["id"]},
                {"$set": {"failed_attempts": failed_attempts}}
            )

            attempts_left = self.MAX_FAILED_ATTEMPTS - failed_attempts
            self.activity.log(username, "LOGIN_FAILED",
                              f"Wrong password. Attempts left: {attempts_left}")

            return self.lang.get("user_login_incorrect_password").format(attempts_left)


        email_verified = bool(user_doc.get("email_verified", False))
        if not email_verified:
            self.activity.log(username, "LOGIN_FAILED_EMAIL_NOT_VERIFIED", "Email not verified")
            return self.lang.get("auth_error_email_not_verified")

        twofa_enabled = user_doc.get("twofa_enabled", False)
        twofa_verified = user_doc.get("twofa_verified", False)


        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "failed_attempts": 0,
                "lock_until": None,
                "last_login": UserManagerUtils.timestamp()
            }}
        )

        self.activity.log(username, "LOGIN_SUCCESS", "User logged in successfully")


        clean_user_doc = {
            "id": user_doc.get("id"),
            "username": user_doc.get("username"),
            "email": user_doc.get("email"),
            "password": user_doc.get("password"),
            "first_name": user_doc.get("first_name"),
            "last_name": user_doc.get("last_name"),
            "role": user_doc.get("role", "USER"),
            "status": user_doc.get("status", "ACTIVE"),
            "email_verified": email_verified,
            "last_login": user_doc.get("last_login"),
            "created_at": user_doc.get("created_at"),
            "twofa_enabled": twofa_enabled,
            "twofa_secret": user_doc.get("twofa_secret"),
            "twofa_verified": twofa_verified
        }

        return User(clean_user_doc)


    def request_password_reset(self, email: str):
        user_doc = self.collection.find_one({"email": email})
        if not user_doc:
            self.activity.log("unknown", "RESET_FAILED", f"Email not found: {email}")
            return self.lang.get("user_login_not_found")


        existing_token = user_doc.get("password_reset_token")
        existing_expires = user_doc.get("password_reset_expires")

        if existing_token and existing_expires and datetime.utcnow() < existing_expires:
            minutes_left = int((existing_expires - datetime.utcnow()).total_seconds() // 60)

            self.activity.log(
                user_doc["username"],
                "RESET_ALREADY_REQUESTED",
                f"Password reset already requested. {minutes_left} minutes remaining"
            )

            return self.lang.get("user_reset_already_requested").format(minutes_left)


        new_password_plain = self.generate_secure_password()
        new_password_hashed = UserManagerUtils.hash_password(new_password_plain)

        token = str(uuid.uuid4())
        expires = datetime.utcnow() + timedelta(minutes=15)

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "password_reset_token": token,
                "password_reset_expires": expires,
                "password_reset_temp_password": new_password_hashed
            }}
        )

        self.activity.log(
            user_doc["username"],
            "RESET_TOKEN_CREATED",
            "Password reset token generated with pending password"
        )

        try:
            from usermanager.verfiy_manager.VerifyUtils import VerifyUtils
            verify_utils = VerifyUtils(lang_manager=self.lang)

            verify_utils.send_password_reset_confirm_email(
                to_email=email,
                username=user_doc["username"],
                token=token,
                new_password=new_password_plain,
                app_url="http://localhost:9090/"
            )

            self.activity.log(
                user_doc["username"],
                "RESET_EMAIL_SENT",
                "Password reset confirmation email sent"
            )

        except Exception as e:
            self.activity.log(
                user_doc["username"],
                "RESET_EMAIL_FAILED",
                str(e)
            )

            return self.lang.get("user_reset_mail_failed")

        return self.lang.get("user_reset_token_created")



    def reset_password(self, token: str, new_password: str):
        if not UserManagerUtils.validate_password(new_password):
            return self.lang.get("user_register_invalid_password")

        user_doc = self.collection.find_one({"password_reset_token": token})
        if not user_doc:
            self.activity.log("unknown", "RESET_FAILED", "Invalid reset token")
            return self.lang.get("user_reset_invalid_token")

        hashed_pw = UserManagerUtils.hash_password(new_password)

        self.collection.update_one(
            {"id": user_doc["id"]},
            {"$set": {"password": hashed_pw, "password_reset_token": None}}
        )

        self.activity.log(user_doc["username"], "RESET_SUCCESS", "Password successfully updated")
        return self.lang.get("user_reset_success")

    def delete_user(self, user_id: str):
        doc = self.collection.find_one({"id": user_id})
        if not doc:
            self.activity.log("unknown", "DELETE_FAILED", f"User not found: {user_id}")
            return self.lang.get("user_delete_not_found")

        result = self.collection.delete_one({"id": user_id})
        if result.deleted_count > 0:
            self.activity.log(doc["username"], "DELETE_SUCCESS", "User deleted successfully")
            return self.lang.get("user_delete_success")

        self.activity.log(doc["username"], "DELETE_FAILED", "Unknown error occurred")
        return self.lang.get("user_delete_not_found")

    def validate_password(self, username: str, password: str) -> bool:
        user_doc = self.collection.find_one({"username": username})
        if not user_doc:
            return False

        hashed = user_doc.get("password", "")

        return UserManagerUtils.verify_password(password, hashed)

    def update_password(self, user_id: str, new_password: str) -> bool:
        if not UserManagerUtils.validate_password(new_password):
            return False

        hashed_pw = UserManagerUtils.hash_password(new_password)

        result = self.collection.update_one(
            {"id": user_id},
            {"$set": {"password": hashed_pw}}
        )

        if result.modified_count > 0:
            self.activity.log(user_id, "PASSWORD_CHANGED", "User changed password")
            return True

        return False

    def update_username(self, user_id: str, new_username: str):

        if not UserManagerUtils.validate_username(new_username):
            return self.lang.get("user_register_invalid_username")

        user_doc = self.collection.find_one({"id": user_id})
        if not user_doc:
            self.activity.log("unknown", "USERNAME_UPDATE_FAILED", f"User not found: {user_id}")
            return self.lang.get("user_update_not_found")

        existing = self.collection.find_one({"username": new_username})
        if existing and existing["id"] != user_id:
            self.activity.log(user_doc["username"], "USERNAME_UPDATE_FAILED",
                              f"Username '{new_username}' already taken")
            return self.lang.get("user_register_username_exists")

        result = self.collection.update_one(
            {"id": user_id},
            {"$set": {"username": new_username}}
        )

        if result.modified_count > 0:
            self.activity.log(user_doc["username"], "USERNAME_UPDATED",
                              f"Username changed to {new_username}")
            return self.lang.get("user_update_success")

        return self.lang.get("user_update_no_change")

    def generate_secure_password(self, length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))
