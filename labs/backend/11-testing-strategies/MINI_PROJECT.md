# Mini Project: Testing Strategies

## What to build

This testing strategies mini build produces a working invoice-service layered suite you can run locally.
Scope stays deliberately small so every testing strategies behavior remains observable.
Budget roughly one focused evening for the invoice-service layered suite implementation.
Success means demonstrating testing strategies judgment, not just compiling code.
Keep a lab journal noting each testing strategies surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Steps

1. Cover invoice math with fast focused unit tests for the service.
2. Slice-test the web layer without booting everything.
3. Run repository tests against a real database.
4. Lock the PDF-export contract with a boundary test.
5. Quarantine one flaky timing test with documented cause.

## Architecture in miniature

- Test-slice concept for layers.
- Integration tests with real dependencies.
- Contract-style boundary checks.
- Test-data builders.
- Flaky-test quarantine discipline.

## How it is judged

- [ ] Suite covers calculation, web, and persistence layers distinctly in the solution.
- [ ] Web slice runs without full application boot in the platform.
- [ ] Repository tests execute against a genuine database.
- [ ] Boundary test pins the export shape.
- [ ] Flaky test quarantined with cause and re-run evidence.

## Extension

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which testing strategies decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
