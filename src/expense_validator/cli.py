from __future__ import annotations

import argparse
import json

from .io import load_json
from .models import InputError, ValidationResult, result_to_dict
from .policy import PolicyError, load_policy
from .validation import validate_submission


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense-validate")
    parser.add_argument("expenses", help="JSON expense submission path")
    parser.add_argument("--policy", default="policy/policy.json", help="JSON policy path")
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit JSON output")
    return parser


def _error_result(message: str) -> ValidationResult:
    return ValidationResult(None, errors=[InputError(message)])


def _print_text(result: ValidationResult, precision: int) -> None:
    print(f"status: {result.status}")
    serialized = result_to_dict(result, precision)
    for finding in serialized["findings"]:
        print(f"line {finding['line_number']}: {finding['message']} (amount {finding['amount']})")
    for error in result.errors:
        location = f"line {error.line_number}: " if error.line_number else ""
        print(f"error: {location}{error.message}")
    if not result.findings and not result.errors:
        print("no policy violations found")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        policy = load_policy(args.policy)
        result = validate_submission(load_json(args.expenses), policy)
    except PolicyError as exc:
        policy = None
        result = _error_result(str(exc))
    precision = policy.reporting_precision if policy else 2
    if args.json_output:
        print(json.dumps(result_to_dict(result, precision), sort_keys=True))
    else:
        _print_text(result, precision)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())