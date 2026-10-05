# VISION — Data Quality (Foundations): Checks That Catch Real Bugs
> Where this lab takes you: from a nightly row-count assertion to a layered
> validation system that fails the pipeline before users see bad numbers.

## The Arc
1. **Dimensions** — completeness, validity, uniqueness, consistency, timeliness.
2. **Profiling** — distributions, nulls, cardinality, drift detection.
3. **Contracts** — expectations, thresholds, and severity.
4. **Placement** — inline vs post-load vs sampling, cost of a check.
5. **Response** — quarantine, alerts, ownership, feedback loops.

## Milestones (checkable)
- [ ] M1: write 15 expectations for an orders table across all 5 dimensions.
- [ ] M2: build a profiler that emits a statistical summary you can eyeball.
- [ ] M3: detect a seeded schema drift and a seeded null-injection in an automated test.
- [ ] M4: place checks so total validation cost stays under 2% of pipeline runtime.
- [ ] M5: design a quarantine + alerting path that does not page at 3am for a known issue.

## Anti-Goals
- Checks with no owner and no action; they become noise and get disabled.
- Validating only row counts; a wrong value in every row passes a count check.
- Blocking loads on soft warnings; severity must be explicit.

## Interview Lens
- "How do you know a metric is trustworthy?"
- "Your dashboard moved 40% — data problem or business event? How do you tell?"
- "Sampling vs full validation: when is sampling wrong?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 build MINI_PROJECT profiler + checks.
- Wk3 add drift detection and a quarantine path. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Ship a quality layer that is cheap, specific, and actually gets acted on.
