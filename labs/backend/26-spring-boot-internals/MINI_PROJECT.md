# Mini Project: Spring Boot Configuration Internals

## What to build

This Spring Boot configuration internals mini build produces a working configuration-resolution observatory you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the configuration-resolution observatory implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
Resist adding features beyond the configuration-resolution observatory acceptance checks.

## Steps

1. Stack six competing property sources over one observatory service for the service.
2. Predict the winning value per key before booting.
3. Prove relaxed-binding variants resolve identically.
4. Activate profile documents and map their precedence.
5. Break one binding deliberately and read the failure analyzer.

## Architecture in miniature

- Property-source ordering.
- Relaxed binding rules.
- Profile-specific documents.
- Condition evaluation reports.
- Failure-analyzer diagnostics.

## How it is judged

- [ ] Prediction sheet scores 10 of 12 winning values correctly in the solution.
- [ ] Binding proof covers 4 naming variants per key in the platform.
- [ ] Profile precedence map matches observed behavior.
- [ ] Failure-analyzer output quoted in the postmortem note.
- [ ] Conditions report explains 3 surprise inclusions.

## Extension

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
