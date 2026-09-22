git remote add origin git@github.com:sharabeshj/Spec-Driven-Development.git
git branch -M main
git push -u origin main# Implementation Plan: Expense Policy Validator

**Branch**: `001-expense-policy-validator` | **Date**: 2026-09-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-expense-policy-validator/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Build an offline command-line validator that reads a JSON expense submission and JSON
policy data, evaluates every line against configured caps and receipt rules using exact
decimal arithmetic, and reports all findings. The command-line layer stays thin: file
loading, argument parsing, output formatting, and exit-code selection delegate to
testable validation functions. Policy values live in `policy/policy.json` as quoted
decimal strings.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13 (pinned by project configuration)

**Primary Dependencies**: No runtime dependencies; Python standard library only

**Storage**: Local JSON files; authoritative policy at `policy/policy.json`

**Testing**: pytest

**Target Platform**: Offline macOS/Linux command line with Python 3.13

**Project Type**: Single-package CLI with `expense-validate` entry point

**Performance Goals**: Validate a submission containing 1,000 expense lines and emit complete output in under 30 seconds

**Constraints**: Offline; no network, API keys, paid services, or hard-coded policy values; Decimal for all money; half-up rounding only at reporting

**Scale/Scope**: One JSON submission per invocation; every valid line evaluated; malformed lines reported when other lines can still be processed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Policy rules are data-driven: caps, thresholds, currencies, rates, and precision are read from `policy/policy.json`.
- [x] Every `FR-###` will map to an automated pytest whose name includes that identifier.
- [x] Runtime dependencies remain standard-library only; pytest is test-only.
- [x] All monetary parsing, conversion, comparison, and proration use `decimal.Decimal`; rounding occurs once during reporting.
- [x] Validation collects all findings and returns the specified exit codes: `0` clean, `1` violations, `2` input/setup errors.
- [x] The tool remains offline and reads exchange rates from local policy data.
- [x] Python 3.13 is already pinned in `pyproject.toml` and `.python-version`.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
└── expense_validator/
  ├── __init__.py
  ├── cli.py
  ├── io.py
  ├── models.py
  ├── policy.py
  └── validation.py

tests/
├── test_cli.py
├── test_io.py
├── test_policy.py
└── test_validation.py

policy/
└── policy.json
```

**Structure Decision**: Use one installable package under `src/expense_validator` with
pure validation and policy modules beneath a thin CLI adapter. Keep policy data in a
top-level `policy/` directory so Finance can update values without changing code.
Place contract and end-to-end tests alongside focused unit tests under `tests/`.
Update `pyproject.toml` to package `src/expense_validator` and expose the
`expense-validate` console script.
The validator reports one-based `line_items` positions, applies the partial-day
multiplier on arrival and departure dates only, treats the receipt threshold as
exclusive, and multiplies foreign amounts by rates expressed as policy-currency units
per foreign-currency unit.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The design follows all constitutional constraints. |
