# Lab 10: AI Deployment & CI/CD — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Release Manifest and Hash (E)

Bundle model, prompt, index, tools, policy, generation, evaluator. Canonical
order-independent hash.

**Verify**: any single field change changes the hash; reordering does not.

---

## Exercise 2: Artifact Registry (M)

Immutable versions, content hashes, aliases, promote/rollback/deprecate. Verify no
overwrite.

---

## Exercise 3: Warm Previous Version (M)

Simulate a warm pool so rollback needs no cold start; measure rollback time with and
without.

---

## Exercise 4: Stable User Assignment (M)

Hash(userId, salt) to bucket; verify per-session stability and cross-experiment
randomization.

---

## Exercise 5: Canary Controller (H)

Ladder 1/5/25/100 with gates; auto rollback; missing metric = breach; minimum samples
per step.

**Verify**: a degraded candidate rolls back at the first step.

---

## Exercise 6: Shadow Deployment (M)

Mirror 100% of traffic to a candidate without serving it; score both; paired deltas at
zero user risk.

---

## Exercise 7: Rollback Drill (M)

Execute a rollback under simulated pressure; measure time-to-rollback and verify
in-flight requests behave.

---

## Exercise 8: Data Migration Expand/Contract (H)

Implement a schema change that old and new artifacts can both read; verify no
rollback-blocking migration exists.

---

## Exercise 9: Environment Parity Check (M)

Compare staging and production specs; report mismatches in model, prompt, index, and
config.

---

## Exercise 10: Capacity Model (M)

Replicas from measured service rate, peak rps, and target utilization; validate against
a simulated arrival process.

---

## Exercise 11: Autoscaling on Queue Depth (H)

Scale on queue depth with a cold-start guard; compare against utilization-based scaling
on a spike.

---

## Exercise 12: Admission Control (E)

Projected-KV admission with 429; verify clean refusal under 2x demand.

---

## Exercise 13: Model Routing and Health (M)

Logical names, capability and tier routing, health-aware, breaker, fallback without 4xx
retries.

---

## Exercise 14: Deprecation Pipeline (M)

Ladder off an old model version with gates; notices; auto-pin at the deadline.

---

## Exercise 15: Feature Flags and Kill Switches (M)

Independent switches for retrieval, tools, agents; verify each disables only its own
scope; flag expiry.

---

## Exercise 16: Deployment Gate (H)

Correctness, safety (zero tolerance), latency, cost, instrumentation coverage, missing
telemetry as a breach.

---

## Exercise 17: CI Pipeline Simulation (M)

Commit -> lint -> unit -> fast eval -> full eval -> build -> stage -> shadow -> canary.

---

## Exercise 18: Post-Deploy Monitoring (H)

Simulate a quality drop after promotion; verify detection via manifest diff and
rollback within target.

---

## Stretch A: Multi-Region Deployment (M)

Region pinning with data residency; verify a pinned request never leaves its region.

---

## Stretch B: Model Fleet Scheduling (H)

Schedule across several versions by cost and quality with headroom; simulate a
deprecation.

---

## Stretch C: Chaos Deployment (H)

Kill replicas, degrade the index, slow a tool mid-canary; verify the gate catches it and
rolls back.

---

## Stretch D: Rollback Latency Optimisation (H)

Reduce rollback time with pre-warmed pools and alias flips; report the before/after.

---

## Stretch E: Progressive Rollout Optimisation (M)

Adaptive dwell times based on observed variance; report the time-to-detection
improvement.

---

## Stretch F: Cost-Aware Canary (M)

Gates include cost per correct outcome; verify a cheap-but-worse candidate is rejected.