---

description: "Task list for implementing the Expense Policy Validator"
---

# Tasks: Expense Policy Validator

**Input**: Design documents from `/specs/001-expense-policy-validator/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Organization**: Tasks are grouped by user story so each increment can be implemented and tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the installable Python package, policy data location, and test layout.

- [X] T001 Update `pyproject.toml` to package `src/expense_validator`, require Python 3.13, keep runtime dependencies empty, retain pytest as a dev dependency, and expose the `expense-validate` console script.
- [X] T002 [P] Create package scaffolding in `src/expense_validator/__init__.py`, `src/expense_validator/cli.py`, `src/expense_validator/io.py`, `src/expense_validator/models.py`, `src/expense_validator/policy.py`, and `src/expense_validator/validation.py`.
- [X] T003 [P] Create the policy data directory and initial schema-shaped file at `policy/policy.json`, storing every monetary amount and exchange rate as a quoted decimal string.
- [X] T004 [P] Create test module placeholders at `tests/test_cli.py`, `tests/test_io.py`, `tests/test_policy.py`, and `tests/test_validation.py` with shared fixture helpers in `tests/conftest.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared models, Decimal handling, file parsing, and policy loading before story work.

**Critical**: User story implementation depends on this phase.

- [X] T005 Implement immutable expense, policy, finding, validation-result, and input-error models in `src/expense_validator/models.py` using explicit required, nullable, and field constraints from `specs/001-expense-policy-validator/data-model.md`.
- [X] T006 Implement quoted-string-to-`Decimal` parsing, non-negative amount validation, policy-precision quantization, and half-up reporting helpers in `src/expense_validator/policy.py` without converting monetary values through float.
- [X] T007 [P] Implement JSON file loading and structured submission parsing in `src/expense_validator/io.py`, including one-based `line_items` position context, required-field errors, malformed JSON errors, and the documented ISO-date and supported-currency constraints.
- [X] T008 [P] Implement policy-file loading and validation in `src/expense_validator/policy.py`, including policy currency, supported currencies, quoted decimal values, per diem caps, receipt threshold, exchange rates, partial-day multiplier, and reporting precision.
- [X] T009 [P] Add foundational tests named `test_fr001_json_inputs_are_loaded`, `test_fr008_input_errors_are_distinguished`, `test_fr010_policy_values_come_from_data`, `test_fr011_decimal_rounding_is_report_only`, and `test_fr012_loading_is_local_only` in `tests/test_io.py` and `tests/test_policy.py`.

**Checkpoint**: Models and data boundaries are stable; user-story work can begin.

---

## Phase 3: User Story 1 - Validate an Expense Submission (Priority: P1) 🎯 MVP

**Goal**: Produce a complete validation result for every valid expense line, including all findings and actionable line references.

**Independent Test**: Supply a JSON submission with clean lines and multiple violations; confirm all findings are returned in input order and a clean submission produces no findings.

### Tests for User Story 1

- [X] T010 [P] [US1] Add `test_fr002_all_valid_lines_are_evaluated` and `test_fr002_empty_submission_behavior` to `tests/test_validation.py`.
- [X] T011 [P] [US1] Add `test_fr007_findings_include_line_rule_values_and_reason` to `tests/test_validation.py`.
- [X] T012 [P] [US1] Add `test_fr008_malformed_line_reports_input_error_without_hiding_valid_lines` to `tests/test_validation.py`.

### Implementation for User Story 1

- [X] T013 [US1] Implement the core validation-result aggregation in `src/expense_validator/validation.py` so every valid line is evaluated and findings/errors retain deterministic line and rule order.
- [X] T014 [US1] Implement line-location, rule-code, relevant-value, and explanation construction in `src/expense_validator/validation.py` for policy findings and input errors.
- [X] T015 [US1] Implement clean-result and violation-result status derivation in `src/expense_validator/models.py` or `src/expense_validator/validation.py` with exit-code mapping reserved for the CLI adapter.

**Checkpoint**: US1 independently reports clean submissions, all line findings, and input errors through testable functions.

---

## Phase 4: User Story 2 - Apply Travel and Receipt Rules (Priority: P1)

**Goal**: Apply policy-defined per diem caps, travel-context proration, and receipt requirements consistently.

**Independent Test**: Validate under-cap, exact-cap, over-cap, receipt-present, receipt-missing, partial-day, and receipt-not-required lines using only values from `policy/policy.json`.

### Tests for User Story 2

- [X] T016 [P] [US2] Add `test_fr003_city_tier_caps_and_exact_cap_boundary` to `tests/test_validation.py`.
- [X] T017 [P] [US2] Add `test_fr003_partial_travel_day_proration_on_arrival_and_departure` to `tests/test_validation.py`.
- [X] T018 [P] [US2] Add `test_fr004_receipt_required_missing_and_present` and `test_fr004_receipt_not_required` to `tests/test_validation.py`.
- [X] T019 [P] [US2] Add `test_fr007_over_cap_finding_reports_amount_and_limit` to `tests/test_validation.py`.

### Implementation for User Story 2

- [X] T020 [US2] Implement policy lookup and exact Decimal comparison for expense category, city tier, and travel context in `src/expense_validator/validation.py`.
- [X] T021 [US2] Implement partial-day cap adjustment in `src/expense_validator/validation.py` so the policy multiplier applies on both arrival and departure dates while complete days between them use the full cap, preserving unrounded values until reporting.
- [X] T022 [US2] Implement receipt-threshold and receipt-presence evaluation in `src/expense_validator/validation.py`, treating the threshold as exclusive so equality does not require a receipt.
- [X] T023 [US2] Add representative policy values and fixture submissions for tier caps, partial days, receipts, and exact boundaries in `policy/policy.json` and `tests/conftest.py`.

**Checkpoint**: US1 and US2 independently cover the primary policy review workflow.

---

## Phase 5: User Story 3 - Validate Multiple Currencies (Priority: P2)

**Goal**: Convert EUR and GBP expenses using policy-supplied rates and report missing-rate errors without assumptions.

**Independent Test**: Validate equivalent policy-currency, EUR, and GBP expenses, then validate an unsupported currency and a missing exchange rate.

### Tests for User Story 3

- [X] T024 [P] [US3] Add `test_fr005_policy_currency_eur_and_gbp_are_supported` to `tests/test_validation.py`.
- [X] T025 [P] [US3] Add `test_fr006_supplied_rates_convert_to_policy_currency` and `test_fr006_missing_rate_is_input_error` to `tests/test_validation.py`.
- [X] T026 [P] [US3] Add `test_fr011_currency_conversion_preserves_precision_until_reporting` to `tests/test_validation.py`.

### Implementation for User Story 3

- [X] T027 [US3] Implement currency lookup and conversion in `src/expense_validator/policy.py` and `src/expense_validator/validation.py` using rates expressed as policy-currency units per foreign-currency unit and multiplying the submitted amount.
- [X] T028 [US3] Add missing-rate, unsupported-currency, malformed-rate, and conversion-context findings to `src/expense_validator/validation.py` with exit-code-2 input/setup semantics.
- [X] T029 [US3] Add EUR and GBP rates plus multi-currency sample submissions in `policy/policy.json`, `samples/multi-currency.json`, and `tests/conftest.py`.

**Checkpoint**: All three user stories are independently testable through core validation functions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Expose the stable CLI contract, documentation, and end-to-end coverage.

- [X] T030 Implement thin argument parsing, default policy path, `--json` mode, human-readable formatting, JSON serialization, and exit codes `0`, `1`, and `2` in `src/expense_validator/cli.py` according to `specs/001-expense-policy-validator/contracts/cli.md`.
- [X] T031 [P] Add CLI contract tests named `test_fr009_exit_codes_are_stable`, `test_fr013_default_text_and_json_output_match`, and `test_fr007_cli_reports_findings` in `tests/test_cli.py`.
- [X] T032 [P] Add end-to-end sample files for clean, over-cap, receipt-missing, partial-day, currency, and malformed cases in `samples/` and document their expected outcomes in `specs/001-expense-policy-validator/quickstart.md`.
- [X] T033 [P] Update `README.md` or the project usage documentation with installation, `expense-validate` invocation, policy-file location, output modes, and exit-code semantics.
- [X] T034 Run the complete pytest suite and the quickstart scenarios, then fix any requirement-to-test gaps or packaging failures in `tests/`, `src/expense_validator/`, `policy/policy.json`, and `pyproject.toml`.
- [X] T035 [P] Add a performance test for `SC-001` that validates a generated submission containing 1,000 expense lines and asserts complete output is produced in under 30 seconds in `tests/test_performance.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes package, policy, and test paths.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP validation-result pipeline.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 result aggregation; its policy checks can be implemented after US1 models are stable.
- **User Story 3 (Phase 5)**: Depends on Foundational and the shared result model; conversion findings integrate with US1 and US2 comparisons.
- **Polish (Phase 6)**: Depends on the desired user stories, especially the result model and validation functions.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; no dependency on another story.
- **US2 (P1)**: Can start after Phase 2; uses the shared aggregation from US1 but remains independently testable through validation functions.
- **US3 (P2)**: Can start after Phase 2; uses the shared Decimal and finding models, and can be developed in parallel with US2 after those foundations exist.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel after setup begins.
- T007, T008, and T009 can run in parallel once the shared models are agreed.
- Within US1, T010, T011, and T012 are independent test files/sections and can be prepared in parallel.
- Within US2, T016, T017, T018, and T019 are independent scenario groups.
- Within US3, T024, T025, and T026 are independent scenario groups.
- After Phase 2, US2 and US3 can proceed in parallel with US1 if the shared model contracts are stable.
- T031, T032, and T033 can proceed in parallel after the CLI contract and sample schema are settled.
- T035 can proceed in parallel with documentation after the validation pipeline and policy fixtures are stable.

## Parallel Example: User Story 1

```text
Task: T010 [US1] Core aggregation tests in tests/test_validation.py
Task: T011 [US1] Finding-detail tests in tests/test_validation.py
Task: T012 [US1] Malformed-line tests in tests/test_validation.py
```

## Parallel Example: User Story 2

```text
Task: T016 [US2] Cap and exact-boundary tests in tests/test_validation.py
Task: T017 [US2] Partial-day tests in tests/test_validation.py
Task: T018 [US2] Receipt-rule tests in tests/test_validation.py
Task: T019 [US2] Finding-detail tests in tests/test_validation.py
```

## Parallel Example: User Story 3

```text
Task: T024 [US3] Supported-currency tests in tests/test_validation.py
Task: T025 [US3] Exchange-rate and missing-rate tests in tests/test_validation.py
Task: T026 [US3] Precision tests in tests/test_validation.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational models, Decimal helpers, JSON loading, and policy loading.
3. Complete Phase 3 US1 aggregation and finding behavior.
4. Complete the minimum CLI slice in T030 for text output and exit codes.
5. Run US1 tests and demonstrate a submission with multiple findings before adding policy-specific refinements.

### Incremental Delivery

1. Add US2 cap, proration, and receipt rules while preserving US1 aggregation.
2. Add US3 currency conversion and missing-rate handling.
3. Complete JSON output, samples, documentation, and full quickstart validation.

### Traceability

Every functional requirement is represented by a named test task: FR-001/T009, FR-002/T010,
FR-003/T016-T017, FR-004/T018, FR-005/T024, FR-006/T025, FR-007/T011/T019/T031,
FR-008/T012, FR-009/T031, FR-010/T009, FR-011/T026, FR-012/T009, and FR-013/T031.
SC-001 is covered by T035 with a 1,000-line workload and a 30-second limit.

## Notes

- Every task uses the required checkbox, sequential ID, optional `[P]`, story label where applicable, and concrete file path format.
- Tests are included because the constitution requires each `FR-###` to map to an automated test.
- Policy values remain in `policy/policy.json`; task descriptions do not authorize hard-coded rule literals.
