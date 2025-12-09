# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from usermanager.user.UserRole import UserRole
from usermanager.user.UserStatus import UserStatus


class User:
    def __init__(
            self,
            id: Optional[str] = None,
            username: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            created_at: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            role: UserRole = UserRole.USER,
            status: UserStatus = UserStatus.PENDING,
            last_login: Optional[str] = None,
            email_verified: bool = False,
            email_verification_token: Optional[str] = None,
            password_reset_token: Optional[str] = None,
            password_reset_expires: Optional[str] = None,
            password_reset_temp_password: Optional[str] = None,
            twofa_enabled: bool = False,
            twofa_secret: Optional[str] = None,
            twofa_verified: bool = False,
            _id: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.status = status
        self.last_login = last_login
        self.email_verified = email_verified
        self.email_verification_token = email_verification_token or str(uuid.uuid4())
        self.password_reset_token = password_reset_token
        self.password_reset_expires = password_reset_expires
        self.password_reset_temp_password = password_reset_temp_password
        self.twofa_enabled = twofa_enabled
        self.twofa_secret = twofa_secret
        self.twofa_verified = twofa_verified
        self._id = _id

    @classmethod
    def create(
            cls,
            username: str,
            email: str,
            password: str,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            role: UserRole = UserRole.USER,
            status: UserStatus = UserStatus.PENDING,
            email_verified: bool = False,
    ) -> "User":

        now = datetime.utcnow().isoformat()

        return cls(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            created_at=now,
            role=role,
            status=status,
            last_login=None,
            email_verified=email_verified,
            email_verification_token=str(uuid.uuid4()),
            password_reset_token=None,
            twofa_enabled=False,
            twofa_secret=None,
            twofa_verified=False
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "status": self.status.value if isinstance(self.status, UserStatus) else self.status,
            "last_login": self.last_login,
            "email_verified": self.email_verified,
            "email_verification_token": self.email_verification_token,
            "password_reset_token": self.password_reset_token,
            "password_reset_expires": self.password_reset_expires,
            "password_reset_temp_password": self.password_reset_temp_password,
            "twofa_enabled": self.twofa_enabled,
            "twofa_secret": self.twofa_secret,
            "twofa_verified": self.twofa_verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            created_at=data.get("created_at"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            role=UserRole(data.get("role", "USER")),
            status=UserStatus(data.get("status", "ACTIVE")),
            last_login=data.get("last_login"),
            email_verified=data.get("email_verified", False),
            email_verification_token=data.get("email_verification_token"),
            password_reset_token=data.get("password_reset_token"),
            password_reset_expires=data.get("password_reset_expires"),
            password_reset_temp_password=data.get("password_reset_temp_password"),
            twofa_enabled=data.get("twofa_enabled", False),
            twofa_secret=data.get("twofa_secret"),
            twofa_verified=data.get("twofa_verified", False),
            _id=str(data.get("_id")) if data.get("_id") else None
        )
