from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


class PolicyError(ValueError):
    pass


def parse_decimal(value: Any, field_name: str) -> Decimal:
    if not isinstance(value, str):
        raise PolicyError(f"{field_name} must be a decimal string")
    try:
        return Decimal(value if isinstance(value, str) else str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PolicyError(f"{field_name} must be a valid decimal") from exc


@dataclass(frozen=True)
class Policy:
    policy_currency: str
    supported_currencies: frozenset[str]
    exchange_rates: dict[str, Decimal]
    per_diem_caps: dict[str, dict[str, Decimal]]
    partial_day_multiplier: Decimal
    receipt_threshold: Decimal
    reporting_precision: int

    def quantize(self, value: Decimal) -> Decimal:
        quantum = Decimal(1).scaleb(-self.reporting_precision)
        return value.quantize(quantum, rounding=ROUND_HALF_UP)

    def convert(self, amount: Decimal, currency: str) -> Decimal:
        if currency == self.policy_currency:
            return amount
        rate = self.exchange_rates.get(currency)
        if rate is None:
            raise PolicyError(f"no exchange rate supplied for {currency}")
        return amount * rate


def load_policy(path: str | Path) -> Policy:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read policy data: {exc}") from exc
    try:
        currency = data["policy_currency"]
        supported = frozenset(data["supported_currencies"])
        rates = {
            key: parse_decimal(value, f"exchange_rates.{key}")
            for key, value in data.get("exchange_rates", {}).items()
        }
        caps = {
            str(tier): {
                category: parse_decimal(value, f"per_diem_caps.{tier}.{category}")
                for category, value in categories.items()
            }
            for tier, categories in data["per_diem_caps"].items()
        }
        multiplier = parse_decimal(data["partial_day_multiplier"], "partial_day_multiplier")
        threshold = parse_decimal(data["receipt_threshold"], "receipt_threshold")
        precision = int(data["reporting_precision"])
    except (KeyError, TypeError, ValueError, PolicyError) as exc:
        raise PolicyError(f"invalid policy data: {exc}") from exc
    if currency not in supported or any(key not in supported for key in rates):
        raise PolicyError("policy currency and exchange rates must use supported currencies")
    return Policy(currency, supported, rates, caps, multiplier, threshold, precision)