import json
import subprocess
import sys
import time


def test_sc001_cli_validates_1000_lines_under_30_seconds(tmp_path):
    submission = {
        "submission_id": "PERF-1000",
        "trip_start": "2026-03-09",
        "trip_end": "2026-03-12",
        "city_tier": 2,
        "line_items": [
            {"date": "2026-03-10", "category": "meal", "amount": "20.00",
             "currency": "USD", "receipt": "R-1"}
            for _ in range(1000)
        ],
    }
    path = tmp_path / "performance.json"
    path.write_text(json.dumps(submission), encoding="utf-8")
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "-m", "expense_validator.cli", str(path), "--policy", "policy/policy.json"],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - started
    assert completed.returncode == 0
    assert elapsed < 30