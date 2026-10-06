# Lab 14: LLMOps (LLM Operations) — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Release Manifest and Hash (E)

Build `ReleaseManifest` with model, prompt, index, tool registry, policy, generation
config, and evaluator versions. `hash()` is a sha256 over a canonical serialization.

**Verify**: changing any single field changes the hash; reordering fields does not.

---

## Exercise 2: Trace Schema (E)

Implement `Trace` with the full span structure from THEORY section 7, JSONL writer,
and a reader. Payloads hashed, not inlined.

**Verify**: a round-trip read reproduces the trace; the rendered prompt hash matches
Lab 03's renderer.

---

## Exercise 3: Percentile Metrics (M)

Implement a streaming p50/p95/p99 estimator (reservoir sampling plus exact for small
n) for TTFT and TPOT.

**Verify**: on a known distribution the estimates match exact percentiles within 1%.

---

## Exercise 4: Cost Attribution (M)

Attribute cost per request, per feature, per tenant, per model version, and per cache
status. Include a reconciliation check against a synthetic invoice.

**Verify**: per-request sum equals the invoice within 2%.

---

## Exercise 5: Canary Controller (H)

Implement a ladder controller (1% -> 10% -> 50% -> 100%) with per-step gates on
quality, safety, latency, and cost; automatic rollback on breach; minimum sample size
per step.

**Verify**: a deliberately degraded candidate is rolled back at the 1% step.

---

## Exercise 6: Stable User Assignment (M)

Hash a user id to a bucket so a user always sees the same variant within a session
and across a window.

**Verify**: assignment is stable for 100% of users across restarts.

---

## Exercise 7: PSI Drift Detector (M)

Implement Population Stability Index over binned distributions and a rolling-window
comparator.

**Verify**: identical distributions give PSI ~0; a shifted one exceeds 0.25.

---

## Exercise 8: Sampling Strategy (M)

Implement stratified sampling: 100% of errors/escalations, 100% of high-value users,
100% of signal-disagreement cases, plus a random sample sized to a budget.

**Verify**: the random sample is unbiased; the mix is reported separately.

---

## Exercise 9: Quality Monitor (M)

Score sampled responses with the Lab 09 metrics plus cheap signals on all responses
(schema validity, refusal, length, PII). Produce the quality dashboard inputs.

---

## Exercise 10: Prompt A/B Experiment (H)

Run two prompt variants over a fixed item set; compute paired win rate with bootstrap
CI and a per-category diff.

**Verify**: a fake improvement is correctly reported as within noise.

---

## Exercise 11: Component Version Diff for Triage (H)

Given two consecutive incident traces, diff the release manifests and report which
component changed.

**Verify**: a prompt-only change is correctly isolated.

---

## Exercise 12: Safe Mode (M)

Implement safe mode: strict policy, tools disabled, retrieval off, forced output
blocking, previous version pinned. Verify graceful degradation.

---

## Exercise 13: Retry Storm Detection (H)

Detect retry amplification from a combination of timeouts, retry counts, and
duplicate trace patterns. Alert before the bill arrives.

---

## Exercise 14: Load Shedding Policy (M)

Implement priority-based shedding: shed batch-tier traffic first, then long contexts,
then interactive. Report the protected fraction.

---

## Exercise 15: Release Ladder with Confidence (H)

Require a minimum sample size such that the paired CI width is below a threshold
before advancing a canary step.

**Verify**: the controller refuses to advance on a noisy metric.

---

## Exercise 16: Feedback Queue and Labeling (H)

Build a review queue from user signals (ranked by user value x severity), a labeling
schema, and an export into the eval suite format.

---

## Exercise 17: Incident Drill Simulator (H)

Script three incidents (latency spike, quality drop, cost spike), run the runbook
decision tree, and measure time-to-diagnose for each.

---

## Exercise 18: Cache Hit Rate Collapse Alert (M)

Detect a drop in prefix/semantic cache hit rate as an early indicator of a
deployment or key-change bug.

---

## Stretch A: Automated Rollback Drill (H)

Continuously deploy a randomized set of known-bad configs to a canary slice and
verify the controller rolls each back. Measures rollback reliability.

---

## Stretch B: Shadow Deployment Comparison (M)

Mirror 100% of traffic to a candidate config, score both, and report the delta with
paired CI at zero user risk.

---

## Stretch C: Multi-Model Fleet Scheduling (H)

Schedule traffic across several model versions by cost and quality, respecting
headroom. Simulate a version deprecation.

---

## Stretch D: Eval Set Drift (M)

Measure how well the eval set still represents traffic (intent mix, length
distribution). Alert when it does not.

---

## Stretch E: Runbook Quality Scoring (H)

Score runbooks mechanically: does every alert have a first question, a decision tree,
an owner, and a tested containment action?

---

## Stretch F: Toil Analysis (M)

Classify operational tasks by automation level; report the fraction that is
mechanical and could be automated next.