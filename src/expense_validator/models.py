from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Finding:
    line_number: int | None
    code: str
    rule: str
    message: str
    amount: Decimal | None = None
    currency: str | None = None
    converted_amount: Decimal | None = None
    limit: Decimal | None = None


@dataclass(frozen=True)
class InputError:
    message: str
    line_number: int | None = None


@dataclass
class ValidationResult:
    submission_id: str | None
    findings: list[Finding] = field(default_factory=list)
    errors: list[InputError] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.errors:
            return "error"
        return "violations" if self.findings else "clean"

    @property
    def exit_code(self) -> int:
        return 2 if self.errors else 1 if self.findings else 0


def decimal_to_text(value: Decimal | None, precision: int) -> str | None:
    if value is None:
        return None
    return format(value, f".{precision}f")


def result_to_dict(result: ValidationResult, precision: int) -> dict[str, Any]:
    def finding_dict(finding: Finding) -> dict[str, Any]:
        return {
            "line_number": finding.line_number,
            "code": finding.code,
            "rule": finding.rule,
            "message": finding.message,
            "amount": decimal_to_text(finding.amount, precision),
            "currency": finding.currency,
            "converted_amount": decimal_to_text(finding.converted_amount, precision),
            "limit": decimal_to_text(finding.limit, precision),
        }

    return {
        "submission_id": result.submission_id,
        "status": result.status,
        "findings": [finding_dict(item) for item in result.findings],
        "errors": [
            {"line_number": error.line_number, "message": error.message}
            for error in result.errors
        ],
    }