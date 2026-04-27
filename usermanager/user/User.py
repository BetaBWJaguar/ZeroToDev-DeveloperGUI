# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from usermanager.user.UserRole import UserRole
from usermanager.user.UserStatus import UserStatus
from subscription.SubscriptionPlan import SubscriptionPlan
from subscription.SubscriptionStatus import SubscriptionStatus
from subscription.SubscriptionFeatures import SubscriptionFeatures


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
            last_recommendation_time: Optional[str] = None,
            recommendation_interval_seconds: Optional[int] = None,
            subscription_id: Optional[str] = None,
            subscription_plan: Optional[str] = None,
            subscription_status: Optional[str] = None,
            subscription_end_date: Optional[str] = None,
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
        self.last_recommendation_time = last_recommendation_time
        self.recommendation_interval_seconds = recommendation_interval_seconds
        self.subscription_id = subscription_id
        self.subscription_plan = subscription_plan
        self.subscription_status = subscription_status
        self.subscription_end_date = subscription_end_date
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
            subscription_id: Optional[str] = None,
            subscription_plan: Optional[str] = SubscriptionPlan.FREE.value,
            subscription_status: Optional[str] = SubscriptionStatus.ACTIVE.value,
            subscription_end_date: Optional[str] = None,
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
            twofa_verified=False,
            subscription_id=subscription_id or str(uuid.uuid4()),
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_end_date=subscription_end_date
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
            "last_recommendation_time": self.last_recommendation_time,
            "recommendation_interval_seconds": self.recommendation_interval_seconds,
            "subscription_id": self.subscription_id,
            "subscription_plan": self.subscription_plan,
            "subscription_status": self.subscription_status,
            "subscription_end_date": self.subscription_end_date,
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
            last_recommendation_time=data.get("last_recommendation_time"),
            recommendation_interval_seconds=data.get("recommendation_interval_seconds"),
            subscription_id=data.get("subscription_id"),
            subscription_plan=data.get("subscription_plan"),
            subscription_status=data.get("subscription_status"),
            subscription_end_date=data.get("subscription_end_date"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )


    def get_subscription_plan(self) -> Optional[SubscriptionPlan]:
        if self.subscription_plan:
            try:
                return SubscriptionPlan(self.subscription_plan)
            except ValueError:
                return None
        return None

    def get_subscription_status(self) -> Optional[SubscriptionStatus]:
        if self.subscription_status:
            try:
                return SubscriptionStatus(self.subscription_status)
            except ValueError:
                return None
        return None

    def has_subscription(self) -> bool:
        return self.subscription_id is not None

    def is_subscription_active(self) -> bool:
        if not self.has_subscription():
            return False
        if self.subscription_status != SubscriptionStatus.ACTIVE.value:
            return False
        if self.subscription_end_date:
            try:
                end_date = datetime.fromisoformat(self.subscription_end_date)
                return end_date > datetime.utcnow()
            except (ValueError, TypeError):
                return False
        return True

    def is_subscription_expired(self) -> bool:
        if not self.has_subscription():
            return True
        if self.subscription_status == SubscriptionStatus.EXPIRED.value:
            return True
        if self.subscription_end_date:
            try:
                end_date = datetime.fromisoformat(self.subscription_end_date)
                return end_date <= datetime.utcnow()
            except (ValueError, TypeError):
                return True
        return False

    def get_subscription_end_date(self) -> Optional[str]:
        return self.subscription_end_date

    def set_subscription(
        self,
        subscription_id: str,
        plan: SubscriptionPlan,
        status: SubscriptionStatus,
        end_date: Optional[str] = None
    ) -> None:
        self.subscription_id = subscription_id
        self.subscription_plan = plan.value
        self.subscription_status = status.value
        self.subscription_end_date = end_date

    def clear_subscription(self) -> None:
        self.subscription_id = None
        self.subscription_plan = None
        self.subscription_status = None
        self.subscription_end_date = None

    def can_use_feature(self, feature: str, **kwargs) -> tuple[bool, Optional[str]]:
        if not self.has_subscription():
            return False, "No subscription found"

        plan = self.get_subscription_plan()
        if not plan:
            return False, "Invalid subscription plan"

        if not self.is_subscription_active():
            return False, "Subscription is not active"

        if not SubscriptionFeatures.is_feature_available(plan, feature):
            return False, f"'{feature}' feature is not available in the {plan.value} plan"

        limits = SubscriptionFeatures.get_all_feature_limits(plan, feature)
        if not limits:
            return True, None

        for limit_key, limit_value in limits.items():
            current_value = kwargs.get(limit_key)
            if current_value is not None and not SubscriptionFeatures.is_unlimited(limit_value):
                if current_value >= limit_value:
                    return False, f"Limit exceeded: {current_value} >= {limit_value}"

        return True, None

    def get_available_features(self) -> List[str]:
        plan = self.get_subscription_plan()
        if not plan:
            return []
        return SubscriptionFeatures.get_available_features(plan)

    def get_feature_limit(self, feature: str, limit_key: str) -> Any:
        plan = self.get_subscription_plan()
        if not plan:
            return None
        return SubscriptionFeatures.get_feature_limit(plan, feature, limit_key)

    def get_all_limits(self) -> Dict[str, Dict[str, Any]]:
        plan = self.get_subscription_plan()
        if not plan:
            return {}
        return SubscriptionFeatures.get_all_limits(plan)

    def get_subscription_info(self) -> Dict[str, Any]:
        return {
            "has_subscription": self.has_subscription(),
            "subscription_id": self.subscription_id,
            "plan": self.subscription_plan,
            "status": self.subscription_status,
            "is_active": self.is_subscription_active(),
            "is_expired": self.is_subscription_expired(),
            "end_date": self.subscription_end_date,
            "features": self.get_available_features(),
            "limits": self.get_all_limits(),
        }

