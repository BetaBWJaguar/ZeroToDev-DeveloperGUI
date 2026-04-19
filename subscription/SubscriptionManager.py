# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from subscription.Subscription import Subscription
from subscription.SubscriptionPlan import SubscriptionPlan
from subscription.SubscriptionStatus import SubscriptionStatus
from logs_manager.LogsManager import LogsManager


class SubscriptionManager:
    def __init__(self):
        self.logger = LogsManager.get_logger("SubscriptionManager")
        self._subscriptions = {}
        self._user_subscriptions = {}

    def create_subscription(
        self,
        user_id: str,
        plan: SubscriptionPlan = SubscriptionPlan.FREE,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        auto_renew: bool = False,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        subscription = Subscription.create(
            user_id=user_id,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            auto_renew=auto_renew,
            payment_method_id=payment_method_id,
            metadata=metadata
        )

        if plan == SubscriptionPlan.FREE:
            subscription.activate()

        self._subscriptions[subscription.id] = subscription

        if user_id not in self._user_subscriptions:
            self._user_subscriptions[user_id] = []
        self._user_subscriptions[user_id].append(subscription)

        self.logger.info(f"Subscription created: {subscription.id} for user {user_id}, plan: {plan.value}")
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        return self._subscriptions.get(subscription_id)

    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        subscriptions = self._user_subscriptions.get(user_id, [])
        for sub in subscriptions:
            if sub.is_active():
                return sub
        return None

    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        return self._user_subscriptions.get(user_id, []).copy()

    def upgrade_subscription(
        self,
        user_id: str,
        new_plan: SubscriptionPlan,
        payment_method_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        current_subscription = self.get_user_subscription(user_id)

        if not current_subscription:
            return False, "No active subscription found"

        current_plan = current_subscription.plan

        plan_order = [SubscriptionPlan.FREE, SubscriptionPlan.BASIC, SubscriptionPlan.PRO, SubscriptionPlan.ENTERPRISE]
        current_index = plan_order.index(current_plan)
        new_index = plan_order.index(new_plan)

        if new_index <= current_index:
            return False, f"Cannot downgrade from {current_plan.value} to {new_plan.value}"

        current_subscription.upgrade_plan(new_plan)
        current_subscription.activate()

        if payment_method_id:
            current_subscription.payment_method_id = payment_method_id

        current_subscription.updated_at = datetime.utcnow().isoformat()

        self.logger.info(f"Subscription upgraded: {current_subscription.id} from {current_plan.value} to {new_plan.value}")
        return True, None

    def downgrade_subscription(
        self,
        user_id: str,
        new_plan: SubscriptionPlan
    ) -> tuple[bool, Optional[str]]:
        current_subscription = self.get_user_subscription(user_id)

        if not current_subscription:
            return False, "No active subscription found"

        current_plan = current_subscription.plan

        plan_order = [SubscriptionPlan.FREE, SubscriptionPlan.BASIC, SubscriptionPlan.PRO, SubscriptionPlan.ENTERPRISE]
        current_index = plan_order.index(current_plan)
        new_index = plan_order.index(new_plan)

        if new_index >= current_index:
            return False, f"Cannot upgrade from {current_plan.value} to {new_plan.value}"

        current_subscription.upgrade_plan(new_plan)
        current_subscription.updated_at = datetime.utcnow().isoformat()

        self.logger.info(f"Subscription downgraded: {current_subscription.id} from {current_plan.value} to {new_plan.value}")
        return True, None

    def cancel_subscription(self, user_id: str) -> tuple[bool, Optional[str]]:
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return False, "No active subscription found"

        subscription.cancel()

        self.logger.info(f"Subscription cancelled: {subscription.id} for user {user_id}")
        return True, None

    def renew_subscription(self, user_id: str, days: int = 30) -> tuple[bool, Optional[str]]:
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return False, "No active subscription found"

        if subscription.status == SubscriptionStatus.CANCELLED:
            return False, "Cannot renew cancelled subscription"

        subscription.extend_subscription(days)
        subscription.activate()

        self.logger.info(f"Subscription renewed: {subscription.id} for {days} days")
        return True, None

    def suspend_subscription(self, user_id: str) -> tuple[bool, Optional[str]]:
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return False, "No active subscription found"

        subscription.suspend()

        self.logger.info(f"Subscription suspended: {subscription.id} for user {user_id}")
        return True, None

    def activate_subscription(self, user_id: str) -> tuple[bool, Optional[str]]:
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return False, "No subscription found"

        subscription.activate()

        self.logger.info(f"Subscription activated: {subscription.id} for user {user_id}")
        return True, None

    def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return {
                "has_subscription": False,
                "plan": None,
                "status": None,
                "is_active": False,
                "is_expired": False,
                "start_date": None,
                "end_date": None,
                "auto_renew": False,
                "features": [],
                "limits": {},
            }

        return {
            "has_subscription": True,
            "subscription_id": subscription.id,
            "plan": subscription.plan.value,
            "status": subscription.status.value,
            "is_active": subscription.is_active(),
            "is_expired": subscription.is_expired(),
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "auto_renew": subscription.auto_renew,
            "features": subscription.get_available_features(),
            "limits": subscription.get_all_limits(),
        }

    def check_subscription_expiry(self, user_id: str) -> bool:
        subscription = self.get_user_subscription(user_id)
        return subscription.is_expired() if subscription else True

    def get_expiring_subscriptions(self, days: int = 7) -> List[Subscription]:
        expiring = []
        threshold = datetime.utcnow() + timedelta(days=days)

        for subscription in self._subscriptions.values():
            if subscription.end_date and subscription.status == SubscriptionStatus.ACTIVE:
                end_date = datetime.fromisoformat(subscription.end_date)
                if end_date <= threshold:
                    expiring.append(subscription)

        return expiring

    def get_active_subscriptions(self) -> List[Subscription]:
        active = []
        for subscription in self._subscriptions.values():
            if subscription.is_active():
                active.append(subscription)

        return active

    def delete_subscription(self, subscription_id: str) -> bool:
        subscription = self._subscriptions.get(subscription_id)

        if not subscription:
            return False

        user_id = subscription.user_id
        if user_id in self._user_subscriptions:
            self._user_subscriptions[user_id] = [
                sub for sub in self._user_subscriptions[user_id]
                if sub.id != subscription_id
            ]

        del self._subscriptions[subscription_id]

        self.logger.info(f"Subscription deleted: {subscription_id}")
        return True
