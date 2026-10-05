# VISION — Data Quality (Advanced): Contracts, Observability, and SLAs
> Where this lab takes you: from per-run checks to a quality system that
  detects problems nobody wrote a rule for, and proves trustworthiness.

## The Arc
1. **Contracts** — producer/consumer agreements, expectations as code.
2. **Statistics** — distributions, drift, anomaly detection, seasonality.
3. **Correlations** — multi-table invariants, cross-system reconciliation.
4. **Observability** — the three pillars: freshness, volume, distribution.
5. **Trust** — SLIs, error budgets, published quality scores, feedback.

## Milestones (checkable)
- [ ] M1: write a data contract with schema, semantics, and SLAs, and enforce it.
- [ ] M2: detect an anomaly in a seasonal series without a hand-written rule.
- [ ] M3: implement a cross-system reconciliation between two independent sources.
- [ ] M4: build a freshness/volume/distribution dashboard with error budgets.
- [ ] M5: present a trust score to consumers and act on a low one.

## Anti-Goals
- A metric per column with no threshold and no owner.
- Alerting on every anomaly; a noisy monitor is a deleted monitor.
- Treating a data contract as a PDF.

## Interview Lens
- "How would you know, without being told, that a pipeline silently broke?"
- "Show me how you'd catch a 3% revenue shift caused by a rounding change."
- "What does a data contract actually contain?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L7. Wk2 MINI_PROJECT with anomaly detection.
- Wk3 add contracts and reconciliation. Wk4 REAL_WORLD_PROJECT with an incident story.

## Done = You Can
- Detect unknown unknowns in data and back it with a trust argument.
