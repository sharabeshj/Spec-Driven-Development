# Research: Expense Policy Validator

## Decision: Use the Python standard library at runtime

**Rationale**: The constitution requires no third-party runtime dependencies. `json`,
`argparse`, `decimal`, `pathlib`, and `dataclasses` cover file loading, CLI parsing,
exact money, and internal data representation. pytest remains a test-only dependency.

**Alternatives considered**: A schema or CLI framework would add runtime dependencies
without being necessary for this single-package tool.

## Decision: Keep JSON as the external file format

**Rationale**: The clarified specification selects JSON for both submissions and policy
data. It supports nested travel context and policy rules while remaining easy to inspect,
version, and validate offline.

**Alternatives considered**: CSV cannot represent policy tiers and exchange-rate metadata
cleanly; supporting both formats would expand the v1 contract without user value.

## Decision: Represent money as quoted decimal strings in policy data and parse with Decimal

**Rationale**: JSON numbers can be read as binary floating-point values by callers. Quoted
strings preserve the exact source value, and `Decimal` keeps conversion, cap comparison,
proration, and reporting deterministic.

**Alternatives considered**: JSON numeric literals and floats violate the constitution's
money rule; integer minor units would make policy files less readable and would not remove
the need to define currency precision.

## Decision: Use a result model that separates findings from input/setup errors

**Rationale**: Policy violations return exit code 1 after all lines are evaluated. Invalid
submission or policy data returns exit code 2 and includes actionable errors. This keeps
review outcomes distinct from failures to perform a reliable review.

**Alternatives considered**: Raising on the first malformed line would violate the
report-everything principle and would hide findings from other valid lines.

## Decision: Default to text with an explicit JSON output mode

**Rationale**: Finance needs readable command-line review, while automation needs a stable
machine-readable representation. Both modes serialize the same result model.

**Alternatives considered**: Text-only prevents automation; JSON-only makes the primary
manual workflow less usable.

## Decision: Use `Decimal.quantize` with `ROUND_HALF_UP` only when formatting output

**Rationale**: The clarified specification requires half-up rounding once at reporting
time. Comparisons use unrounded Decimal values and precision comes from policy data.

**Alternatives considered**: Rounding during conversion can change cap decisions; binary
float rounding is non-deterministic for financial boundaries.

## Decision: Define currency rates as foreign-currency units to policy-currency units

**Rationale**: Each rate represents policy-currency units per one unit of EUR or GBP, so
the submitted foreign amount is multiplied by the rate. This makes the conversion
direction explicit and prevents reciprocal-rate mistakes.

**Alternatives considered**: Defining rates in the reverse direction would require
division and would be easier to misread in the policy file.

## Decision: Use exclusive receipt thresholds and arrival/departure partial days

**Rationale**: An amount equal to the receipt threshold does not require a receipt. The
partial-day multiplier applies on both the trip arrival and departure dates; complete
days between them use the full cap.

**Alternatives considered**: Inclusive thresholds and applying proration to only one or
neither boundary day would create inconsistent treatment of common travel patterns.

## Decision: Identify findings by one-based `line_items` position

**Rationale**: Finance-facing output uses the first expense as line 1, matching ordinary
document conventions and giving malformed entries a stable reference.

**Alternatives considered**: Zero-based positions are less natural for reviewers; a
separate caller-supplied identifier would add an input requirement not requested for v1.

## Decision: Measure performance with a 1,000-line submission

**Rationale**: The success criterion is concrete: complete validation and output for 1,000
expense lines must finish in under 30 seconds.

**Alternatives considered**: An undefined representative workload would make the target
non-repeatable and prevent meaningful acceptance testing.