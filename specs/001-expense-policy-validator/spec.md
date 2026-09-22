# Feature Specification: Expense Policy Validator

**Feature Branch**: `001-expense-policy-validator`

**Created**: 2026-09-22

**Status**: Clarified

**Input**: User description: "Finance spends two days a month checking expense submissions against the travel policy by hand. We want a command line tool they can run against a submitted expense file that tells them which lines break policy and why. It needs to handle the per diem caps, the receipt rule, and expenses that come in euros or pounds. Finance wants to stop arguing about whether a rule was applied consistently."

## Clarifications

### Session 2026-09-22

- Q: Should the expense submission and policy data use JSON files for version one? → A: Option A - Use JSON for both expense submissions and policy data.
- Q: Should the validator’s default output be human-readable text, machine-readable JSON, or both? → A: Option C - Provide human-readable text by default plus optional JSON output.
- Q: Which exit codes should the validator use for clean results, policy violations, and input or setup errors? → A: Option A - 0 clean, 1 policy violations, 2 input/setup errors.
- Q: Which rounding rule should the validator use when reporting monetary amounts? → A: Option A - Round half up at reporting time to the policy-defined precision.
- Q: Should exchange rates in policy data convert each foreign-currency unit directly into one unit of the policy currency? → A: Option A - Yes; each rate is foreign currency to policy currency, so the submitted amount is multiplied by the rate.
- Q: Should an expense exactly equal to the receipt threshold require a receipt? → A: Option B - Require a receipt only when the amount is greater than the threshold.
- Q: Which travel days should receive the partial-day multiplier before comparing an expense with its per diem cap? → A: Option A - Apply the multiplier on both the trip arrival day and departure day, while applying the full cap on complete days between them.
- Q: Should line locations use one-based positions in the `line_items` array? → A: Option A - Use one-based `line_items` positions, with the first expense reported as line 1.
- Q: How many expense lines should the representative submission contain for the under-30-second performance criterion? → A: 1,000 lines.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate an Expense Submission (Priority: P1)

As a Finance reviewer, I can run the validator against a submitted expense file and receive a result for every expense line, including a clear explanation for each policy violation.

**Why this priority**: This is the core workflow that replaces manual checking and makes policy application consistent.

**Independent Test**: Run the validator against a file containing compliant and non-compliant expenses and confirm that the output identifies each affected line, states the violated rule, and does not stop after the first violation.

**Acceptance Scenarios**:

1. **Given** an expense file with compliant lines, **When** Finance validates it, **Then** the tool reports that no policy violations were found and returns the documented success exit status.
2. **Given** an expense file with multiple violations, **When** Finance validates it, **Then** the tool reports every violating line in one result and explains the rule and relevant values for each violation.
3. **Given** a line that is exactly at a policy limit, **When** Finance validates it, **Then** the line is accepted as compliant.
4. **Given** a validation run, **When** Finance uses the default output mode, **Then** the tool presents findings as human-readable text and provides an option to emit the same result as JSON.

### User Story 2 - Apply Travel and Receipt Rules (Priority: P1)

As a Finance reviewer, I can see whether meal or daily travel spending exceeds the applicable per diem cap and whether a required receipt is missing.

**Why this priority**: Per diem caps and receipt requirements are the named policy checks and account for the current manual review effort.

**Independent Test**: Run separate submissions containing under-cap, at-cap, over-cap, receipt-present, receipt-missing, and receipt-not-required lines and compare the reported outcomes with the supplied policy data.

**Acceptance Scenarios**:

1. **Given** a meal expense below its applicable per diem cap, **When** the line is validated, **Then** it passes the cap check.
2. **Given** a meal expense above its applicable per diem cap, **When** the line is validated, **Then** the output identifies the line, names the per diem rule, and states the amount over the cap.
3. **Given** an expense that requires a receipt and has none recorded, **When** the line is validated, **Then** the output identifies the missing receipt as a policy violation.

### User Story 3 - Validate Multiple Currencies (Priority: P2)

As a Finance reviewer, I can validate expenses submitted in euros or pounds using the exchange rates supplied with the policy so that currency does not change the policy decision.

**Why this priority**: International submissions must be evaluated consistently, while the primary value remains the policy review itself.

**Independent Test**: Validate equivalent expenses expressed in the policy currency, euros, and pounds with supplied exchange rates and confirm that converted comparisons produce the expected same or different cap outcomes.

**Acceptance Scenarios**:

1. **Given** a euro-denominated expense and a supplied euro exchange rate, **When** it is validated, **Then** the tool converts it for policy comparison and reports the original currency and converted comparison amount.
2. **Given** a pound-denominated expense and a supplied pound exchange rate, **When** it is validated, **Then** the tool converts it for policy comparison and reports the original currency and converted comparison amount.
3. **Given** a submission using a currency or exchange rate not supplied by the policy data, **When** it is validated, **Then** the tool reports an input or policy-data error rather than making an untraceable assumption.

### Edge Cases

- An empty expense file is rejected as invalid input and does not report a misleading successful policy review.
- A malformed line, missing required field, invalid amount, or unsupported currency is reported with its one-based `line_items` position and a corrective explanation; other valid lines are still evaluated when possible.
- A missing policy data file, malformed policy data, or missing exchange rate is reported as a clear validation setup error.
- A receipt value is interpreted according to the documented input convention; an explicitly false or missing receipt fails when the rule requires one, while an explicitly true receipt passes that check. An expense exactly equal to the receipt threshold is not required to have a receipt.
- The partial-day multiplier applies to expenses dated on the trip arrival day or departure day; complete days between those dates use the full applicable cap.
- Currency conversion and cap comparisons preserve exact monetary precision, and the reported amount is rounded once using half-up rounding at the policy-defined reporting precision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The validator MUST accept a JSON expense submission file and a JSON policy data file as command-line inputs.
- **FR-002**: The validator MUST evaluate every valid expense line against all applicable policy rules in a single run rather than stopping at the first violation.
- **FR-003**: The validator MUST check each applicable expense against the per diem cap defined by the policy data for its expense type and travel context, applying the partial-day multiplier on both the trip arrival day and departure day and the full cap on complete days between them.
- **FR-004**: The validator MUST check whether each expense includes a receipt when the policy requires one, and the receipt threshold MUST be exclusive: an expense equal to the threshold does not require a receipt.
- **FR-005**: The validator MUST support expense amounts denominated in the policy currency, euros, and pounds.
- **FR-006**: The validator MUST multiply euro and pound amounts by the supplied foreign-currency-to-policy-currency exchange rate for comparison and MUST report an error when a required rate is unavailable.
- **FR-007**: For every violation, the validator MUST report the one-based `line_items` position, the rule that was violated, the submitted amount or relevant value, and why the line failed.
- **FR-008**: The validator MUST distinguish policy violations from invalid submission or policy input errors and explain both in its output.
- **FR-009**: The validator MUST return exit code 0 when the submission has no policy violations, exit code 1 when one or more policy violations are found, and exit code 2 when input or setup errors prevent reliable validation.
- **FR-010**: The validator MUST read caps, receipt requirements, currency settings, exchange rates, and reporting precision from policy data rather than embedding those rule values in application logic.
- **FR-011**: The validator MUST preserve exact monetary values for conversion and cap comparison, then apply half-up rounding once at reporting time using the precision defined by the policy data.
- **FR-012**: The validator MUST operate without network access, API keys, or paid services.
- **FR-013**: The validator MUST present human-readable findings by default and MUST provide an optional JSON output mode containing the same validation results and error details.

### Key Entities *(include if data involved)*

- **Expense Submission**: A file containing one or more expense lines submitted for review.
- **Expense Line**: A submitted expense with a line location, date or travel context, expense type, amount, currency, and receipt information.
- **Policy Data**: The authoritative set of per diem caps, receipt requirements, supported currencies, exchange rates, and reporting rules used for a validation run.
- **Validation Finding**: A reported policy violation or input/setup error linked to the relevant expense line or policy data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Finance can validate a submission containing 1,000 expense lines in under 30 seconds from invoking the command to receiving the complete result.
- **SC-002**: In test submissions containing multiple independent violations, 100% of policy violations are reported in one run rather than only the first violation.
- **SC-003**: For a reference suite covering caps, receipts, currencies, boundaries, and malformed inputs, 100% of expected validation outcomes and explanations match the policy data.
- **SC-004**: At least 90% of Finance reviewers can identify the violated rule and reason from the output without consulting application code.
- **SC-005**: Finance reduces manual expense-policy checking time from approximately two days per month to no more than half a day per month for the same submission volume.

## Assumptions

- The submitted expense file and policy data use JSON, with schemas documented as part of the command's input contract.
- Policy data identifies the policy currency, applicable cap by expense type and travel context, receipt requirement, supported currencies, exchange rates, and reporting precision.
- Euro and pound exchange rates are supplied for each validation run; each rate represents policy-currency units per one unit of the foreign currency and is multiplied by the submitted amount.
- Finance reviewers are trusted users of the command line and have access to the submitted file and the relevant policy data file.
- Version one validates a single submission in each invocation; batch scheduling, interactive editing, and remote policy retrieval are out of scope.
- The documented exit statuses are part of the command's contract and remain stable unless a later specification explicitly changes them.