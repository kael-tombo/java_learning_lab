# Lab 10: AI Deployment & CI/CD — Theory

## 1. Deploy vs Release

- **Deploy** is mechanical: move an artifact into an environment.
- **Release** is a decision: expose it to users.

Most AI incidents are bad releases, not bad deploys. The artifact is a **bundle** —
model, prompt, index, tool registry, policy, generation config — and every component
can cause the incident.

```
ReleaseManifest {
  modelId@version, promptId@version, indexVersion,
  toolRegistryVersion, policyVersion, generationConfig, evaluatorVersion
}
manifestHash = sha256(canonical(manifest))
```

The hash appears in every response and trace. It turns "was this the old prompt?" from
an investigation into a log filter.

## 2. Artifact Management

- Immutable artifacts with content hashes; never overwrite a published version.
- Promote/rollback/deprecate semantics; aliases (`production`, `canary`) point at
  versions so serving config is stable.
- Provenance: base model SHA, adapter checksum, dataset hash, build metadata.
- Retention of old artifacts so rollback is instant, not a rebuild.
- Model warm pools: the previous version stays warm so rollback needs no cold start.

## 3. Progressive Delivery Strategies

| Strategy | Traffic | Rollback | Use when |
|----------|---------|----------|----------|
| Shadow | 100% mirrored, not served | n/a | Measuring at zero user risk |
| Canary | 1 / 5 / 25 / 100 | traffic flip | Most releases |
| Blue-green | 0 or 100 | instant flip | Config-only, needs instant revert |
| A/B | 50/50 by user | flip | Comparing two versions for a decision |

Rules:
- **Assign by user**, not by request, so nobody sees two versions in a session.
- Gate every step on automated metrics; a **missing metric is a breach**.
- Minimum sample size per step; do not decide on 40 requests.
- Automatic rollback, no human decision under pressure.

## 4. CI/CD for AI

```
  commit      lint (prompts, schemas) | unit tests | fast eval      ~2 min
  merge       full eval | safety suite | cost/latency budget       ~30 min
  build       immutable artifact + provenance + model card
  stage       deploy to staging | shadow against production traffic
  canary      1% -> 5% -> 25% -> 100% with automated gates
  release     alias flip | monitor | rollback path open
  post        continuous eval | drift watch | incident drills
```

Model-specific additions: the artifact is huge, so artifacts are content-addressed and
cached; the "build" includes quantization and adapter merging; evaluation must run at
the **served batch size**, because numerics differ.

## 5. Rollback Design

Rollback must be a **config flip**, not a rebuild. Requirements:

- Previous artifact present and warm.
- Alias repoint effective on the next request.
- Rollback time is a tracked metric (< 5 minutes).
- Data migrations must be backward compatible so an old artifact can read a new
  schema; prefer expand/contract migrations.
- Rollback cannot un-send an email or an irreversible tool call — hence approval gates
  and idempotency at the action level, not only at the release level.

## 6. Capacity and Autoscaling

```
replicas = ceil( peak_rps / (service_rate_per_replica * target_utilization) )
```

Target utilization `<= 0.6`; tail latency degrades sharply near saturation. Scale on
**queue depth** (leading), not GPU utilization (lagging). Respect GPU cold-start delay.
Warm pools for interactive tiers. Admission control with 429 rather than unbounded
queueing.

## 7. Model Routing and Multi-Version Fleets

- Logical names (`chat-quality`) decouple products from models.
- Health-aware routing with circuit breakers; fallback chains that never retry 4xx.
- Deprecation: ladder off an old version with gates, notices, auto-pin at the deadline.
- Capacity per model version; drain before decommission.

## 8. Environment Parity

| Dimension | Requirement |
|-----------|-------------|
| Model | Same artifact hash, not a floating tag |
| Prompt | Same version id |
| Index | Same version, or a documented staging rebuild |
| Config | Same generation params; secrets differ |
| Data | Synthetic fixtures; no production PII |
| Observability | Same instrumentation, same dashboards |

Parity bugs are the ones that only appear after promotion, so test the staging build
against **production-shaped traffic in shadow mode**.

## 9. Feature Flags and Kill Switches

- Independent kill switches for retrieval, tools, agents, and specific models.
- Blast radius bounded by flag scope.
- Flags owned centrally with expiry; stale flags are debt.
- A flag that disables a guardrail requires an approval record.

## 10. Deployment Gates

Block on:
- Correctness regression beyond tolerance **in any category**.
- Safety regression of any size (zero tolerance).
- p95 latency or cost per request beyond budget.
- Golden-trace change requiring review.
- Instrumentation gaps (missing spans).
- **Missing telemetry**.

Warn (do not block):
- Quality deltas whose CI includes zero.
- Over-refusal within the agreed delta.

## 11. Post-Deployment

- Monitor quality, safety, latency, cost, and drift continuously.
- Continuous eval on sampled production traffic.
- Every incident adds a golden case and a red-team test.
- Post-mortem within a week; the write-up is the prevention.
- Quarterly game days for rollback and containment.

## Key Equations

```
replicas = ceil(peak_rps / (service_rate * target_utilization))
ladder_requests = n * sum_i (1/f_i)
rollback_blast = fraction of traffic on the bad version
release_risk = blast_radius * impact * detection_delay
```