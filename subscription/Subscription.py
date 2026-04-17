# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from subscription.SubscriptionPlan import SubscriptionPlan
from subscription.SubscriptionStatus import SubscriptionStatus
from subscription.SubscriptionFeatures import SubscriptionFeatures


class Subscription:

    def __init__(
            self,
            id: Optional[str] = None,
            user_id: Optional[str] = None,
            plan: SubscriptionPlan = SubscriptionPlan.FREE,
            status: SubscriptionStatus = SubscriptionStatus.PENDING,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            auto_renew: bool = False,
            payment_method_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None,
            _id: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.plan = plan
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.auto_renew = auto_renew
        self.payment_method_id = payment_method_id
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self._id = _id
    
    @classmethod
    def create(
            cls,
            user_id: str,
            plan: SubscriptionPlan = SubscriptionPlan.FREE,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            auto_renew: bool = False,
            payment_method_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> "Subscription":
        now = datetime.utcnow().isoformat()
        
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            plan=plan,
            status=SubscriptionStatus.PENDING if plan != SubscriptionPlan.FREE else SubscriptionStatus.ACTIVE,
            start_date=start_date or now,
            end_date=end_date,
            auto_renew=auto_renew,
            payment_method_id=payment_method_id,
            metadata=metadata,
            created_at=now,
            updated_at=now
        )
    
    def activate(self) -> None:
        self.status = SubscriptionStatus.ACTIVE
        self.updated_at = datetime.utcnow().isoformat()
    
    def cancel(self) -> None:
        self.status = SubscriptionStatus.CANCELLED
        self.auto_renew = False
        self.updated_at = datetime.utcnow().isoformat()
    
    def suspend(self) -> None:
        self.status = SubscriptionStatus.SUSPENDED
        self.updated_at = datetime.utcnow().isoformat()
    
    def is_active(self) -> bool:
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.end_date:
            return datetime.fromisoformat(self.end_date) > datetime.utcnow()
        return True
    
    def is_expired(self) -> bool:
        if self.status == SubscriptionStatus.EXPIRED:
            return True
        if self.end_date and datetime.fromisoformat(self.end_date) <= datetime.utcnow():
            return True
        return False
    
    def upgrade_plan(self, new_plan: SubscriptionPlan) -> None:
        if new_plan.value in [p.value for p in SubscriptionPlan]:
            self.plan = new_plan
            self.updated_at = datetime.utcnow().isoformat()
    
    def extend_subscription(self, days: int) -> None:
        if self.end_date:
            current_end = datetime.fromisoformat(self.end_date)
        else:
            current_end = datetime.utcnow()
        
        from datetime import timedelta
        new_end = current_end + timedelta(days=days)
        self.end_date = new_end.isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan.value if isinstance(self.plan, SubscriptionPlan) else self.plan,
            "status": self.status.value if isinstance(self.status, SubscriptionStatus) else self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "auto_renew": self.auto_renew,
            "payment_method_id": self.payment_method_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscription":
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            plan=SubscriptionPlan(data.get("plan", "FREE")),
            status=SubscriptionStatus(data.get("status", "PENDING")),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            auto_renew=data.get("auto_renew", False),
            payment_method_id=data.get("payment_method_id"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )
    
    def __repr__(self) -> str:
        return (f"Subscription(id={self.id}, user_id={self.user_id}, "
                f"plan={self.plan.value}, status={self.status.value})")
    

    def is_feature_available(self, feature: str) -> bool:
        return SubscriptionFeatures.is_feature_available(self.plan, feature)
    
    def get_available_features(self) -> list[str]:
        return SubscriptionFeatures.get_available_features(self.plan)
    
    def get_feature_limit(self, feature: str, limit_key: str) -> Any:
        return SubscriptionFeatures.get_feature_limit(self.plan, feature, limit_key)
    
    def get_all_limits(self) -> Dict[str, Dict[str, Any]]:
        return SubscriptionFeatures.get_all_limits(self.plan)
    
    def can_use_feature(self, feature: str, **kwargs) -> tuple[bool, Optional[str]]:
        if not self.is_active():
            return False, "Subscription is not active"

        if not self.is_feature_available(feature):
            return False, f"'{feature}' feature is not available in the {self.plan.value} plan"

        limits = SubscriptionFeatures.get_all_feature_limits(self.plan, feature)
        if not limits:
            return True, None

        for limit_key, limit_value in limits.items():
            current_value = kwargs.get(limit_key)
            if current_value is not None and not SubscriptionFeatures.is_unlimited(limit_value):
                if current_value >= limit_value:
                    return False, f"Limit exceeded: {current_value} >= {limit_value}"

        return True, None
