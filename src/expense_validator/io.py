from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .models import InputError
from .policy import PolicyError


def load_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read JSON input: {exc}") from exc


def parse_submission(data: Any, supported_currencies: frozenset[str]) -> tuple[dict[str, Any], list[InputError]]:
    errors: list[InputError] = []
    if not isinstance(data, dict):
        return {}, [InputError("submission must be a JSON object")]
    line_items = data.get("line_items")
    if not isinstance(line_items, list):
        return data, [InputError("line_items must be an array")]
    if not line_items:
        return data, [InputError("line_items must contain at least one expense")]
    valid_items: list[dict[str, Any]] = []
    for position, item in enumerate(line_items, start=1):
        if not isinstance(item, dict):
            errors.append(InputError("expense line must be an object", position))
            continue
        missing = [key for key in ("date", "category", "amount", "currency") if key not in item]
        if missing:
            errors.append(InputError(f"missing required field(s): {', '.join(missing)}", position))
            continue
        try:
            date.fromisoformat(item["date"])
            if not isinstance(item["amount"], str) or isinstance(item["amount"], bool):
                raise ValueError("amount must be a decimal string")
            amount = Decimal(item["amount"])
            if amount < 0:
                raise ValueError("amount must be non-negative")
            if item["currency"] not in supported_currencies:
                raise ValueError(f"unsupported currency {item['currency']}")
        except (ValueError, InvalidOperation) as exc:
            errors.append(InputError(str(exc), position))
            continue
        valid_items.append({**item, "_line_number": position, "_amount": amount})
    return {**data, "line_items": valid_items}, errors