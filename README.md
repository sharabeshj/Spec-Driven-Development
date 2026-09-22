# Expense Policy Validator

Run the offline validator with Python 3.13:

```sh
uv run expense-validate samples/berlin-trip.json --policy policy/policy.json
```

The default output is human-readable. Add `--json` for automation. Exit codes are:

- `0`: no policy violations
- `1`: one or more policy violations
- `2`: input or policy setup error

Policy values and exchange rates are stored in `policy/policy.json`. Monetary policy
values are quoted decimal strings; EUR and GBP amounts are multiplied by their supplied
foreign-to-policy currency rates. Findings use one-based `line_items` positions.

Run the tests with:

```sh
uv run pytest
```