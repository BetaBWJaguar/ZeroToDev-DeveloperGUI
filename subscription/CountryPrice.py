# -*- coding: utf-8 -*-
from typing import Dict, Optional, Any
from subscription.SubscriptionPlan import SubscriptionPlan


class CountryPrice:
    CURRENCY_USD = "USD"
    CURRENCY_TRY = "TRY"
    CURRENCY_EUR = "EUR"
    CURRENCY_GBP = "GBP"

    DEFAULT_COUNTRY = "US"

    PLAN_PRICES: Dict[str, Dict[SubscriptionPlan, Dict[str, Any]]] = {
        "US": {
            SubscriptionPlan.FREE: {"price": 0.00, "currency": CURRENCY_USD},
            SubscriptionPlan.BASIC: {"price": 2.99, "currency": CURRENCY_USD},
            SubscriptionPlan.PRO: {"price": 7.99, "currency": CURRENCY_USD},
            SubscriptionPlan.ENTERPRISE: {"price": 14.99, "currency": CURRENCY_USD},
        },
        "TR": {
            SubscriptionPlan.FREE: {"price": 0.00, "currency": CURRENCY_TRY},
            SubscriptionPlan.BASIC: {"price": 89.00, "currency": CURRENCY_TRY},
            SubscriptionPlan.PRO: {"price": 249.00, "currency": CURRENCY_TRY},
            SubscriptionPlan.ENTERPRISE: {"price": 449.00, "currency": CURRENCY_TRY},
        },
        "DE": {
            SubscriptionPlan.FREE: {"price": 0.00, "currency": CURRENCY_EUR},
            SubscriptionPlan.BASIC: {"price": 2.79, "currency": CURRENCY_EUR},
            SubscriptionPlan.PRO: {"price": 7.49, "currency": CURRENCY_EUR},
            SubscriptionPlan.ENTERPRISE: {"price": 13.99, "currency": CURRENCY_EUR},
        },
        "GB": {
            SubscriptionPlan.FREE: {"price": 0.00, "currency": CURRENCY_GBP},
            SubscriptionPlan.BASIC: {"price": 2.49, "currency": CURRENCY_GBP},
            SubscriptionPlan.PRO: {"price": 6.49, "currency": CURRENCY_GBP},
            SubscriptionPlan.ENTERPRISE: {"price": 12.49, "currency": CURRENCY_GBP},
        },
    }

    @classmethod
    def get_price(cls, country_code: str, plan: SubscriptionPlan) -> Optional[Dict[str, Any]]:
        country_code = country_code.upper()
        country_prices = cls.PLAN_PRICES.get(country_code)
        if country_prices:
            return country_prices.get(plan)
        return cls.PLAN_PRICES.get(cls.DEFAULT_COUNTRY, {}).get(plan)

    @classmethod
    def get_price_value(cls, country_code: str, plan: SubscriptionPlan) -> float:
        price_info = cls.get_price(country_code, plan)
        return price_info["price"] if price_info else 0.0

    @classmethod
    def get_currency(cls, country_code: str, plan: SubscriptionPlan) -> str:
        price_info = cls.get_price(country_code, plan)
        return price_info["currency"] if price_info else cls.CURRENCY_USD

    @classmethod
    def get_all_prices(cls, country_code: str) -> Dict[SubscriptionPlan, Dict[str, Any]]:
        country_code = country_code.upper()
        country_prices = cls.PLAN_PRICES.get(country_code)
        if country_prices:
            return country_prices.copy()
        default_prices = cls.PLAN_PRICES.get(cls.DEFAULT_COUNTRY, {})
        return default_prices.copy()

    @classmethod
    def get_formatted_price(cls, country_code: str, plan: SubscriptionPlan) -> str:
        price_info = cls.get_price(country_code, plan)
        if not price_info:
            return "$0.00"

        currency = price_info["currency"]
        price = price_info["price"]

        currency_symbols = {
            cls.CURRENCY_USD: "$",
            cls.CURRENCY_TRY: "₺",
            cls.CURRENCY_EUR: "€",
            cls.CURRENCY_GBP: "£",
        }

        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{price:.2f}"

    @classmethod
    def add_country_pricing(
            cls,
            country_code: str,
            prices: Dict[SubscriptionPlan, Dict[str, Any]]
    ) -> None:
        cls.PLAN_PRICES[country_code.upper()] = prices

    @classmethod
    def get_supported_countries(cls) -> list[str]:
        return list(cls.PLAN_PRICES.keys())
