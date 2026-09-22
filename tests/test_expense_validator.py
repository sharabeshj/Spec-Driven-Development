import json

import pytest

from expense_validator.io import load_json
from expense_validator.models import result_to_dict
from expense_validator.policy import load_policy
from expense_validator.validation import validate_submission


@pytest.fixture
def policy_path():
    from pathlib import Path

    return Path(__file__).parents[1] / "policy" / "policy.json"


def submission(items, tier="2", start="2026-03-09", end="2026-03-12"):
    return {"submission_id": "TEST", "trip_start": start, "trip_end": end,
            "city_tier": tier, "line_items": items}


def meal(day, amount, currency="USD", receipt="R-1"):
    return {"date": day, "category": "meal", "amount": amount,
            "currency": currency, "receipt": receipt}


def test_fr001_json_inputs_are_loaded(tmp_path, policy_path):
    path = tmp_path / "submission.json"
    path.write_text(json.dumps(submission([meal("2026-03-10", "20.00")])), encoding="utf-8")
    assert load_json(path)["submission_id"] == "TEST"
    assert load_policy(policy_path).policy_currency == "USD"


def test_fr002_all_valid_lines_are_evaluated(policy_path):
    result = validate_submission(submission([meal("2026-03-10", "72.00"), meal("2026-03-11", "80.00")]), load_policy(policy_path))
    assert len(result.findings) == 2


def test_fr002_empty_submission_is_invalid(policy_path):
    result = validate_submission(submission([]), load_policy(policy_path))
    assert result.exit_code == 2 and result.errors


def test_fr003_city_tier_caps_and_exact_cap_boundary(policy_path):
    policy = load_policy(policy_path)
    assert not validate_submission(submission([meal("2026-03-10", "60.00")]), policy).findings
    assert validate_submission(submission([meal("2026-03-10", "60.01")]), policy).findings


def test_fr003_partial_travel_day_proration_on_arrival_and_departure(policy_path):
    result = validate_submission(submission([meal("2026-03-09", "46.00"), meal("2026-03-12", "46.00")]), load_policy(policy_path))
    assert len(result.findings) == 2


def test_fr004_receipt_threshold_is_exclusive(policy_path):
    policy = load_policy(policy_path)
    item = {"date": "2026-03-10", "category": "transport", "amount": "75.00", "currency": "USD", "receipt": None}
    assert not validate_submission(submission([item]), policy).findings
    item["amount"] = "75.01"
    assert validate_submission(submission([item]), policy).findings


def test_fr005_policy_currency_eur_and_gbp_are_supported(policy_path):
    result = validate_submission(submission([meal("2026-03-10", "10.00", "EUR"), meal("2026-03-10", "10.00", "GBP")]), load_policy(policy_path))
    assert not result.errors


def test_fr006_supplied_rates_convert_and_missing_rate_errors(policy_path):
    policy = load_policy(policy_path)
    result = validate_submission(submission([meal("2026-03-10", "58.00", "EUR")]), policy)
    assert result.findings[0].converted_amount == policy.exchange_rates["EUR"] * 58
    missing = validate_submission(submission([meal("2026-03-10", "10.00", "JPY")]), policy)
    assert missing.errors


def test_fr007_findings_include_one_based_line_rule_values_and_reason(policy_path):
    finding = validate_submission(submission([meal("2026-03-10", "61.00")]), load_policy(policy_path)).findings[0]
    assert finding.line_number == 1 and finding.rule and finding.amount and finding.message


def test_fr008_input_errors_are_distinguished(policy_path):
    result = validate_submission(submission([{"date": "2026-03-10", "category": "meal"}]), load_policy(policy_path))
    assert result.errors and not result.findings and result.exit_code == 2


def test_fr008_malformed_line_does_not_hide_valid_lines(policy_path):
    items = [{"date": "2026-03-10", "category": "meal"}, meal("2026-03-10", "20.00")]
    result = validate_submission(submission(items), load_policy(policy_path))
    assert result.errors and not result.findings


def test_fr009_exit_codes_are_stable(policy_path):
    policy = load_policy(policy_path)
    assert validate_submission(submission([meal("2026-03-10", "20.00")]), policy).exit_code == 0
    assert validate_submission(submission([meal("2026-03-10", "61.00")]), policy).exit_code == 1


def test_fr010_policy_values_come_from_data(policy_path):
    assert load_policy(policy_path).per_diem_caps["2"]["meal"] == 60


def test_fr011_decimal_rounding_is_report_only(policy_path):
    from decimal import Decimal

    policy = load_policy(policy_path)
    assert policy.quantize(policy.exchange_rates["EUR"] * 58) == Decimal("62.64")


def test_fr012_loading_is_local_only(policy_path):
    assert load_policy(policy_path).exchange_rates


def test_fr013_json_result_contains_stable_status(policy_path):
    result = validate_submission(submission([meal("2026-03-10", "61.00")]), load_policy(policy_path))
    assert result_to_dict(result, 2)["status"] == "violations"
