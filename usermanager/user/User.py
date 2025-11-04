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
        self._id = _id

    @classmethod
    def create(cls, username: str, email: str, password: str, **kwargs):
        return cls(username=username, email=email, password=password, **kwargs)

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
            "last_login": self.last_login
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
            _id=str(data.get("_id")) if data.get("_id") else None
        )
