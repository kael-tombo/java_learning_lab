# VISION — SIEM & Monitoring: Detection You Can Prove Works
> Where this lab takes you: from shipping logs to running a detection programme where every rule is measured.

## The Arc
1. **Telemetry** — what to log, at what fidelity, and why "we have logs" is not detection.
2. **Collection & normalisation** — shipping agents, parsing, enrichment, and schema discipline.
3. **Correlation** — single-event rules, sequences, aggregations, and thresholds.
4. **Detection engineering** — the detection lifecycle, tuning, false-positive economics, and coverage gaps.
5. **Response & metrics** — severity, routing, alert fatigue, and measuring detection effectiveness.

## Milestones (checkable)
- [ ] M1: identify the five highest-value security events for one service and justify each.
- [ ] M2: write a correlation rule that detects credential stuffing, and test it with replayed events.
- [ ] M3: build a baseline and show a rule with an acceptable false-positive rate.
- [ ] M4: measure detection coverage against a MITRE-style technique list.
- [ ] M5: reduce alert volume by 50% while keeping true positives — and prove it.

## Core Competencies
- Structured, queryable logging with correlation IDs and stable field names.
- Correlation rule design: thresholds, windows, aggregation, and suppression.
- Detection-as-code: versioned rules, unit tests against event fixtures, CI deployment.
- The false-positive economy: cost of noise versus cost of a miss.

## Anti-Goals
- Alerting on every authentication failure with no aggregation.
- Rules that have never been tested against a real event shape.
- Log messages that are useful to a developer and useless to a correlation engine.

## Anti-Goals note
A detection nobody validated is a hypothesis. Every rule in this lab ships with a test.

## Interview Lens
- "How do you know your detection works?" "What is your false-positive budget?"
- "An attacker used a valid token from an unusual location. What would you see?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: schema design and a first correlation rule.
- Wk2 QUIZ/FLASHCARDS to 90%+; rule tests with fixtures.
- Wk3 MINI_PROJECT: detection-as-code pipeline with metrics.
- Wk4 REAL_WORLD_PROJECT: detection programme with coverage mapping and tuning.

## Done = You Can
- Build, test, deploy, and measure a detection rule, and show evidence it catches a
  simulated attack and tolerates normal traffic.
