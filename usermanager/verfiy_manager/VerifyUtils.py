# -*- coding: utf-8 -*-
import json
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from pymongo import MongoClient
from usermanager.user.UserStatus import UserStatus


class VerifyUtils:
    def __init__(self,
                 config_filename: str = "database_config.json",
                 smtp_filename: str = "smtp_config.json"):
        base_dir = Path(__file__).resolve().parents[1]

        config_path = base_dir / config_filename
        if not config_path.exists():
            raise FileNotFoundError(f"DB config not found at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        uri = f"mongodb://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['authSource']}"
        self.client = MongoClient(uri)
        self.db = self.client[cfg["name"]]
        self.collection = self.db["users"]

        smtp_path = base_dir / smtp_filename
        if not smtp_path.exists():
            raise FileNotFoundError(f"SMTP config not found at {smtp_path}")

        with open(smtp_path, "r", encoding="utf-8") as f:
            smtp_cfg = json.load(f)

        self.SMTP_EMAIL = smtp_cfg["email"]
        self.SMTP_PASS = smtp_cfg["password"]
        self.SMTP_HOST = smtp_cfg["host"]
        self.SMTP_PORT = smtp_cfg["port"]
        self.SMTP_USE_SSL = smtp_cfg.get("use_ssl", True)

    def send_verification_email(self, to_email: str, token: str, app_url: str) -> bool:
        verify_link = f"{app_url.rstrip('/')}/verify/email?token={token}"

        body = f"""
        """

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = "Email Verification"
        msg["From"] = self.SMTP_EMAIL
        msg["To"] = to_email

        try:
            if self.SMTP_USE_SSL:
                with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT) as server:
                    server.login(self.SMTP_EMAIL, self.SMTP_PASS)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                    server.starttls()
                    server.login(self.SMTP_EMAIL, self.SMTP_PASS)
                    server.send_message(msg)
            return True
        except Exception as e:
            return False

    def verify_email_token(self, token: str):
        user_doc = self.collection.find_one({"email_verification_token": token})

        if not user_doc:
            return {"success": False, "message": "Invalid or expired token."}

        self.collection.update_one(
            {"id": user_doc["id"]},
            {
                "$set": {"email_verified": True, "status": UserStatus.ACTIVE.value},
                "$unset": {"email_verification_token": ""}
            }
        )

        return {"success": True, "message": "Email verified successfully."}
