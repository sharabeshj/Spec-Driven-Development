import json

from expense_validator.cli import main


def _submission(path, amount="20.00"):
    path.write_text(json.dumps({
        "submission_id": "CLI-1",
        "trip_start": "2026-03-09",
        "trip_end": "2026-03-12",
        "city_tier": 2,
        "line_items": [{"date": "2026-03-10", "category": "meal", "amount": amount,
                         "currency": "USD", "receipt": "R-1"}],
    }), encoding="utf-8")


def test_fr001_cli_accepts_expense_and_policy_paths(tmp_path, capsys):
    submission = tmp_path / "submission.json"
    _submission(submission)
    assert main([str(submission), "--policy", "policy/policy.json"]) == 0
    assert "no policy violations" in capsys.readouterr().out


def test_fr009_exit_codes_are_stable(tmp_path):
    submission = tmp_path / "submission.json"
    _submission(submission, "61.00")
    assert main([str(submission), "--policy", "policy/policy.json"]) == 1
    missing = tmp_path / "missing.json"
    assert main([str(missing), "--policy", "policy/policy.json"]) == 2


def test_fr013_default_text_and_json_output_match(tmp_path, capsys):
    submission = tmp_path / "submission.json"
    _submission(submission, "61.00")
    assert main([str(submission), "--policy", "policy/policy.json", "--json"]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "violations" and output["findings"]