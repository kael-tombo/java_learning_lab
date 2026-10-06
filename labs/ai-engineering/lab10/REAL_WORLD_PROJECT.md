# Lab 10: AI Deployment & CI/CD — Real-World Project

## Project: Release Platform for a Multi-Model LLM Product

Design and build the release platform behind a production LLM product serving several
models: artifact and manifest registry, evaluation gates, progressive delivery,
multi-version routing, capacity management, parity enforcement, and the operational
loop that runs after every release.

## Context

An AI product's release artifact is a bundle of seven versioned things. Six of them can
cause an incident independently, and none of them is covered by the deploy pipeline the
rest of the company already uses. This platform is what makes releasing an LLM change as
routine — and as reversible — as shipping a Java service.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Llama 3 Herd of Models" (Dubey et al., submitted 25 Apr 2024; v2 23 Jul 2024) —
  https://arxiv.org/abs/2407.21783 — takeaway for this lab: a production model release is
  documented as a pipeline with distinct evaluation stages and per-category results
  (safety, quality, cost, latency) rather than a single score, which is exactly the gate
  structure this platform encodes; it also reports post-training data mix and inference-time
  configuration as part of the release record, the same treatment given to weights.
- "vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention" (Kwon et al., submitted
  23 Jun 2023; v2 18 Sep 2023) — https://arxiv.org/abs/2309.06180 — takeaway for this
  lab: serving capacity is governed by KV-cache management under a memory budget rather
  than by a fixed concurrency number, which is why this platform's autoscaler treats
  resident sequences and cache pressure as first-class signals and why warm pools matter
  for rollback latency.

## System Architecture

```
   developer            control plane                      data plane
   ---------            -------------                      -----------
   prompt edit --->  manifest builder ---> artifact store ---> serving fleet
   model swap          (canonical hash)     (write-once)      (routers + replicas)
   index rebuild       |                       |                  |
   tool schema         v                       v                  v
   gen-config    eval service            provenance         health signals
                   (quality/safety/          sidecar             |
                    latency/cost)                                v
                        |                                   autoscaler
                        v                                   (queue depth)
                   gate engine  <----- metrics store ---------'
                        |
                 canary controller  -> cohort assignment (stable per user)
                        |
              promote / hold / rollback  ->  alias pointer
                        |
                   post-release: continuous eval, drift watch, incident drills
```

## Component Specs

### 1. Manifest Registry
- Every releasable unit is a `ReleaseManifest`: model id and version (content hash of
  weights and tokenizer), prompt id and version, index version, tool registry version,
  policy version, generation config, evaluator version.
- Canonical serialization with fixed field order; SHA-256 over the canonical form.
- The hash is attached to every response, every trace span, and every evaluation record.
- Manifests are immutable; a change is a new manifest. No in-place edits.
- Aliases (`production`, `canary`, `staging`, per-tenant pins) point at hashes, never at
  content. Every alias write is an audited event with actor and reason.

### 2. Artifact Store and Provenance
- Content-addressed, write-once, deduplicated. Publishing an existing hash is a no-op,
  not a mutation.
- Provenance sidecar per artifact: base model commit SHA, adapter checksum, tokenizer
  hash, dataset hashes for fine-tuned artifacts, build toolchain versions, build
  timestamp, and the pipeline definition that produced it.
- **CI verifies provenance**: a base model referenced by a floating tag fails the build.
- Retention: keep every artifact reachable from an alias plus the previous `N` per alias,
  so rollback never requires a rebuild. A retention sweep that would break rollback is
  refused.
- Cold storage for artifacts older than the window, with a measured restore time that
  is published next to the retention policy.

### 3. Evaluation Service and Gates
- Four gate families, each with a baseline, a tolerance, a minimum sample size, and a
  severity:
  - **Correctness**: task success, retrieval ground-truth accuracy, golden-trace diff.
    Tolerance per category; any category over tolerance blocks.
  - **Safety**: policy violation rate, refusal appropriateness, injection success.
    Zero tolerance; any regression blocks.
  - **Performance**: p50/p95/p99 latency per stage, time to first token, tokens/second,
    queue depth, error and timeout rates.
  - **Cost**: spend per request and **cost per successful request**.
- Gates run at the **served batch size and precision**, because numerics differ from
  offline evaluation; a quantization-aware gate is required before promoting a quantized
  artifact.
- Every gate declares a minimum sample size. A gate with insufficient data returns
  `WAIT`, not `PASS`.
- Missing telemetry is a `BREACH`, never a pass. An absent metric disables the gate
  silently otherwise.
- Golden traces are diffed with review: a changed golden trace is a deliberate act with
  an approval record, not an incidental diff.

### 4. Progressive Delivery
- Strategies: shadow (mirrored, not served, no side effects), canary ladder, blue-green
  (instant flip, config-only releases), A/B (50/50 by user, for a stated decision).
- Ladder `1 / 5 / 25 / 100` percent with per-step minimum samples and maximum wait.
- Cohort assignment by `hash(userId + salt)`, stable across replicas and requests, with
  a bounded local cache and no coordination store.
- Automatic rollback, no human decision under pressure. Rollback is always available and
  always the same cost.
- Exposure is computed and published per release: traffic share times requests before
  detection.

### 5. Routing and Multi-Version Fleets
- Logical names (`chat-quality`, `chat-fast`, `summarize`) decouple product code from
  model versions.
- Per-version capacity accounting so a shared fleet cannot be oversubscribed by a
  migration.
- Health-aware routing with circuit breakers per version. **4xx never trips a breaker
  and never triggers a retry** — the request is invalid, not unlucky.
- Fallback chains with a documented order and a bounded total retry budget.
- Deprecation ladder: notices in-product, telemetry on remaining callers, auto-pin to the
  successor at a stated deadline, drain before decommission, artifact retained for the
  rollback window.

### 6. Capacity and Autoscaling
- Queue depth is the primary signal (leading, and it already encodes arrival rate and
  service time by Little's law); resident sequences and KV-cache pressure are secondary.
- Boot-time lookahead in the desired-replica computation, because GPU cold start is
  tens of seconds.
- Warm pools per model version, held above baseline, so a rollback serves immediately.
- Target utilization 0.6 or below, justified by a per-stage latency budget.
- Admission control with explicit 429 over unbounded queueing; queue depth capped.
- Spare capacity sized against a measured recovery-time objective, not by instinct.

### 7. Environment Parity
- Enforced dimensions: model artifact hash, prompt version, index version, generation
  config, evaluation fixtures, and instrumentation.
- Hard-fail on model, prompt, and index divergence; weighted score for the rest, with
  secrets explicitly excluded because they are meant to differ.
- Staging is exercised against **production-shaped traffic in shadow mode** so parity
  bugs surface before promotion rather than after it.
- Shadow comparators are side-effect free by construction and tested for it.

### 8. Feature Flags and Kill Switches
- Independent kill switches for retrieval, tools, agents, and individual models.
- Scoped by tenant and product; blast radius bounded by scope.
- Owner, expiry, and reason required at creation. Expired-but-referenced flags are
  counted and alerted on — stale flags are debt with a clock.
- Disabling a guardrail requires an approval record; without one the flag is inactive
  **and** a page fires.
- Safe mode: strict policy, tools off, no retrieval, previous manifest pinned, still
  answering.

### 9. Rollback Design
- Alias repoint, effective on the next request. Previous artifact present and warm.
- Rollback duration is a tracked metric with a 5-minute objective and an alert on
  breach.
- In-flight requests complete under the manifest they were admitted with; the count is
  reported, so contamination is bounded by in-flight volume rather than rollout size.
- Data migrations use **expand/contract**: an old artifact can always read a new schema.
  Contract phases are gated on the rollback window closing.
- Irreversible actions get idempotency keys, dry-run mode, approval gates, and a
  compensating-action path — release rollback alone cannot undo them.

### 10. Post-Release Operations
- Continuous eval on sampled production traffic, joined against manifest hashes so
  regressions are attributed to a release rather than to a hypothesis.
- Drift watch with sequential tests (CUSUM) rather than 50 independent alarms, which
  would fire constantly.
- Every incident adds a golden case and a red-team test, and the release is not closed
  until the test exists.
- Quarterly game days: kill a canary replica mid-ladder, force a rollback, trigger a
  bad flag, and measure time-to-detect and time-to-contain.
- Post-mortem within a week; the write-up is the deliverable, not the ceremony.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Rollback time | < 5 min p95 (measured by drill) |
| Rollback implementation cost | 1 config write, no rebuild, no artifact download |
| Canary step exposure vs direct | <= 25% of direct-release exposure |
| Gate data sufficiency | 100% of gated steps carry a minimum sample size |
| Missing telemetry | Blocks release, never passes |
| Safety regression tolerance | 0 |
| Correctness regression tolerance | Per category, published |
| p95 latency | Within budget; target utilization <= 0.6 |
| Cost per successful request | Tracked; regression beyond delta blocks |
| Provenance verification | Fails build on moved tag |
| Artifact retention | Every rollback window satisfied; zero rebuild rollbacks |
| Time to detect (drill) | <= 15 min |
| Time to contain (drill) | <= 30 min |
| Parity hard-fail coverage | model, prompt, index |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Prompt change regresses quality | Per-category gate with delta | Canary ladder; automatic rollback |
| Model swapped under a tag | Provenance check in CI | Pin by content hash |
| Quantized artifact behaves differently | Gate at served precision and batch size | Quantization-aware evaluation stage |
| Canary promotes on noise | Minimum sample size per gate | Step gates carry `n` |
| Missing metric passes the gate | `present()` instead of defaulting | Missing telemetry is a breach |
| Gate harness exception | Catch-and-fail in stage runner | Exception fails the stage |
| Rollback needs a rebuild | Rollback instrumentation | Retention + warm pool; no cold restore in path |
| In-flight responses mix versions | Manifest hash on every response | Trace attribution; bounded by in-flight count |
| Old artifact cannot read new schema | Migration compatibility test | Expand/contract migrations |
| Irreversible action double-executed | Idempotency key violation | Gate before dispatch; state check on retry |
| Cohort flips within a session | Session-consistency test | Assign by user hash |
| Breaker opens on client errors | Breaker state metric | Exclude 4xx from failures and retries |
| Autoscale reacts after the spike | Shed-request counter | Queue-depth signal with boot lookahead |
| Utilization pushed to 0.95 | p95 alert | Utilization ceiling from the latency budget |
| Shadow path caused a duplicate action | Side-effect audit | Comparators pure by construction |
| Staging green, prod red | Shadow against production-shaped traffic | Parity hard-fails |
| Stale flag disables a feature | Stale-flag counter | Mandatory expiry; alert on reference |
| Guardrail flag on without approval | Approval check | Inactive plus page |
| Index rebuild drifts silently | Index version diffing | Index in the manifest and in parity |
| Router fallback amplifies a bad model | Retry budget metric | Breakers; bounded chains |

## Milestones

- **M1** — manifest registry with canonical hashing; response-level hash attribution.
- **M2** — content-addressed artifact store with provenance and CI verification.
- **M3** — evaluation service: four gate families, baselines, tolerances, sample sizes.
- **M4** — missing-telemetry breach path and the golden-trace review workflow.
- **M5** — cohort assignment with cross-replica stability proven.
- **M6** — canary controller: four outcomes, per-step gates, automatic rollback.
- **M7** — rollback as an alias write; duration metric and drill.
- **M8** — routing with logical names, breakers, 4xx exclusion, fallback budget.
- **M9** — capacity: autoscaler, warm pools, admission control, spike simulation.
- **M10** — parity enforcement with hard-fails and shadow mode.
- **M11** — feature flags with scope, expiry, approval, and safe mode.
- **M12** — continuous eval and drift watch on production traffic.
- **M13** — deprecation ladder with auto-pin and drain.
- **M14** — first game day: mid-ladder kill, forced rollback, bad flag.

## Deliverables

1. Manifest registry and artifact store with provenance and CI checks.
2. Evaluation service with the four gate families and published baselines/tolerances.
3. Canary controller, routing, autoscaler, flags, and parity enforcement.
4. Runbooks for rollback, kill-switch use, and deprecation, each with a drill report.
5. `REPORT.md` — the release-safety posture: detected-before-detection rates, exposure
   per strategy, measured rollback time, and residual risks accepted with reasons.

## Definition of Done

- [ ] Every response and trace carries a manifest hash; error rates are attributable to
      a release.
- [ ] Rollback measured under 5 minutes p95 in a drill, with no rebuild and no cold
      artifact fetch.
- [ ] Canary exposure at or below 25% of a direct release for the same failure.
- [ ] A gate with missing telemetry blocks the release.
- [ ] Safety regression of any size blocks the release.
- [ ] A moved model tag fails CI provenance verification.
- [ ] An artifact rollback works after the retention window boundary is crossed.
- [ ] An old artifact reads a new-schema index, proving expand/contract.
- [ ] A 400 response never trips a breaker and never triggers a retry.
- [ ] Time-to-detect and time-to-contain measured in a game day.
- [ ] Stale flag count reported; an expired flag self-disables.
