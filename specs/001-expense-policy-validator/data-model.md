# Data Model: Expense Policy Validator

## Expense Submission

Top-level JSON object containing `submission_id`, trip context, and `line_items`.

- `submission_id`: required string used to identify the review.
- `trip_start`, `trip_end`: required ISO dates used for travel-day rules.
- `city_tier`: required string key resolved against policy per diem tiers.
- `line_items`: required non-empty array for a meaningful review; each item is evaluated independently and referenced in output by its one-based array position.

## Expense Line

- `date`: required ISO date within the submission travel period.
- `category`: required policy category such as `meal` or `transport`.
- `amount`: required non-negative decimal value; submission values are parsed without float conversion.
- `currency`: required supported currency code.
- `receipt`: receipt identifier or null; missing/null fails only when policy requires a receipt.

## Policy Data

Stored in `policy/policy.json`. Every monetary amount and exchange rate is a quoted
decimal string.

- `policy_currency`: base comparison currency.
- `supported_currencies`: allowed currency codes.
- `exchange_rates`: rate from each supported foreign currency to the policy currency.
- `per_diem_caps`: cap by city tier and expense category.
- `partial_day_multiplier`: decimal multiplier applied on the trip arrival day and departure day; complete days between them use the full cap.
- `receipt_threshold`: decimal threshold above which a receipt is required; equality does not require a receipt.
- `reporting_precision`: number of decimal places used for final output.

## Validation Finding

An immutable result record containing one-based `line_number` (when line-specific), `code`,
`rule`, `message`, `amount`, `currency`, `converted_amount`, and `limit` where relevant.
Findings are ordered by input line and rule evaluation order.

## Validation Result

Contains the submission identifier, all policy findings, all input/setup errors that can
be associated with a line or file, and the selected output representation. Exit status is
derived from the result: 0 for no findings/errors, 1 for policy findings, 2 for input or
setup errors.