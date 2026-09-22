# CLI Contract: `expense-validate`

## Invocation

```text
expense-validate EXPENSES.json [--policy POLICY.json] [--json]
```

- `EXPENSES.json`: required expense submission path.
- `--policy POLICY.json`: optional policy path; defaults to `policy/policy.json`.
- `--json`: optional machine-readable output mode; without it, output is human-readable text.
- `--help`: displays usage and exits 0.

## Exit Status

- `0`: validation completed with no policy violations or input/setup errors.
- `1`: validation completed and one or more policy violations were found.
- `2`: input or policy setup errors prevented reliable validation.

## Text Output

Text output includes a summary, one finding per one-based `line_items` position/rule, the submitted and converted
amounts where relevant, and an explanation. Input/setup errors are clearly labeled and
include the source file or line when available.

## JSON Output

The JSON document contains stable top-level keys:

```json
{
  "submission_id": "SUB-001",
  "status": "violations",
  "findings": [],
  "errors": []
}
```

`status` is one of `clean`, `violations`, or `error`. Monetary values in output are
strings rounded half up to policy-defined precision. The JSON and text modes represent
the same validation result.