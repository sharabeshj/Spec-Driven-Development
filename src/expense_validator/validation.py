from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from .io import parse_submission
from .models import Finding, InputError, ValidationResult
from .policy import Policy, PolicyError


def validate_submission(submission: dict[str, Any], policy: Policy) -> ValidationResult:
    parsed, errors = parse_submission(submission, policy.supported_currencies)
    result = ValidationResult(submission.get("submission_id"), errors=list(errors))
    try:
        start = date.fromisoformat(parsed["trip_start"])
        end = date.fromisoformat(parsed["trip_end"])
        tier = str(parsed["city_tier"])
    except (KeyError, TypeError, ValueError) as exc:
        result.errors.append(InputError(f"invalid travel context: {exc}"))
        return result
    for item in parsed.get("line_items", []):
        line = item["_line_number"]
        amount = item["_amount"]
        currency = item["currency"]
        try:
            converted = policy.convert(amount, currency)
        except PolicyError as exc:
            result.errors.append(InputError(str(exc), line))
            continue
        category = item["category"]
        cap = policy.per_diem_caps.get(tier, {}).get(category)
        item_date = date.fromisoformat(item["date"])
        if cap is not None:
            if item_date in (start, end):
                cap *= policy.partial_day_multiplier
            if converted > cap:
                result.findings.append(Finding(
                    line, "PER_DIEM_EXCEEDED", "per_diem_cap",
                    f"line {line} exceeds the {category} per diem cap",
                    amount, currency, converted, cap,
                ))
        if converted > policy.receipt_threshold and not item.get("receipt"):
            result.findings.append(Finding(
                line, "RECEIPT_REQUIRED", "receipt_rule",
                f"line {line} exceeds the receipt threshold and has no receipt",
                amount, currency, converted, policy.receipt_threshold,
            ))
    return result