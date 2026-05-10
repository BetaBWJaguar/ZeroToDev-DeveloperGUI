# -*- coding: utf-8 -*-
import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any


class PaymentMethod:
    TYPE_CREDIT_CARD = "credit_card"
    TYPE_DEBIT_CARD = "debit_card"

    def __init__(
            self,
            id: Optional[str] = None,
            user_id: Optional[str] = None,
            method_type: str = TYPE_CREDIT_CARD,
            card_holder_name: Optional[str] = None,
            card_number_last4: Optional[str] = None,
            card_number_hash: Optional[str] = None,
            expiry_month: Optional[int] = None,
            expiry_year: Optional[int] = None,
            billing_address: Optional[Dict[str, str]] = None,
            is_default: bool = False,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.method_type = method_type
        self.card_holder_name = card_holder_name
        self.card_number_last4 = card_number_last4
        self.card_number_hash = card_number_hash
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.billing_address = billing_address or {}
        self.is_default = is_default
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    @classmethod
    def create(
            cls,
            user_id: str,
            card_holder_name: str,
            card_number: str,
            expiry_month: int,
            expiry_year: int,
            method_type: str = TYPE_CREDIT_CARD,
            billing_address: Optional[Dict[str, str]] = None,
            is_default: bool = False,
    ) -> "PaymentMethod":
        card_number_clean = card_number.replace(" ", "").replace("-", "")
        last4 = card_number_clean[-4:] if len(card_number_clean) >= 4 else card_number_clean
        card_hash = hashlib.sha256(card_number_clean.encode()).hexdigest()

        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            method_type=method_type,
            card_holder_name=card_holder_name,
            card_number_last4=last4,
            card_number_hash=card_hash,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            billing_address=billing_address,
            is_default=is_default,
        )

    def get_display_number(self) -> str:
        if self.card_number_last4:
            return f"•••• •••• •••• {self.card_number_last4}"
        return "•••• •••• •••• ••••"

    def get_expiry_display(self) -> str:
        if self.expiry_month and self.expiry_year:
            return f"{self.expiry_month:02d}/{self.expiry_year % 100:02d}"
        return "--/--"

    def is_expired(self) -> bool:
        if not self.expiry_month or not self.expiry_year:
            return True
        now = datetime.utcnow()
        if self.expiry_year < now.year:
            return True
        if self.expiry_year == now.year and self.expiry_month < now.month:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "method_type": self.method_type,
            "card_holder_name": self.card_holder_name,
            "card_number_last4": self.card_number_last4,
            "card_number_hash": self.card_number_hash,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "billing_address": self.billing_address,
            "is_default": self.is_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentMethod":
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            method_type=data.get("method_type", cls.TYPE_CREDIT_CARD),
            card_holder_name=data.get("card_holder_name"),
            card_number_last4=data.get("card_number_last4"),
            card_number_hash=data.get("card_number_hash"),
            expiry_month=data.get("expiry_month"),
            expiry_year=data.get("expiry_year"),
            billing_address=data.get("billing_address"),
            is_default=data.get("is_default", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (f"PaymentMethod(id={self.id}, user_id={self.user_id}, "
                f"type={self.method_type}, last4={self.card_number_last4})")

    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        clean = card_number.replace(" ", "").replace("-", "")
        if not clean.isdigit():
            return False
        if len(clean) < 13 or len(clean) > 19:
            return False

        total = 0
        reverse_digits = clean[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    @staticmethod
    def get_card_type(card_number: str) -> str:
        clean = card_number.replace(" ", "").replace("-", "")
        if clean.startswith("4"):
            return "visa"
        elif clean[:2] in ("51", "52", "53", "54", "55") or 2221 <= int(clean[:4]) <= 2720:
            return "mastercard"
        elif clean[:2] in ("34", "37"):
            return "amex"
        elif clean[:4] == "6011" or clean.startswith("65"):
            return "discover"
        return "unknown"
