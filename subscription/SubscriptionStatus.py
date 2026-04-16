# -*- coding: utf-8 -*-
from enum import Enum


class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
