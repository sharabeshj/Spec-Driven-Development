# Quickstart: Expense Policy Validator

## Prerequisites

- Python 3.13
- The project environment with pytest installed for tests

## Validate a submission

From the repository root:

```sh
uv run expense-validate samples/berlin-trip.json --policy policy/policy.json
```

The default output is readable text. The command exits `0` for a clean submission, `1`
when policy findings exist, and `2` when the files cannot be validated reliably.

## Produce automation output

```sh
uv run expense-validate samples/multi-currency.json --policy policy/policy.json --json
```

The output is JSON with the same findings and errors represented by the text mode.

## Validate the performance target

Use a submission containing 1,000 expense lines and confirm that complete validation and
output finish in under 30 seconds on the supported Python 3.13 environment.

The automated equivalent is `tests/test_performance.py`.

## Run the test suite

```sh
uv run pytest
```

The suite covers the requirements in `spec.md`, including caps, partial travel days,
receipts, EUR/GBP conversion, exact boundaries, complete finding collection, output
modes, and exit statuses. The field definitions are documented in [data-model.md](data-model.md)
and the command contract is documented in [contracts/cli.md](contracts/cli.md).