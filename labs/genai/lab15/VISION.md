# Lab 15: Building a GenAI Platform — Vision

## Platform Layers

```
L6  CONSUMPTION       SDK | REST/gRPC | chat UI | playground | docs
    ------------------------------------------------------------------
L5  PRODUCT SERVICES  RAG-as-a-service | agents-as-a-service
                      prompt registry | eval-as-a-service
    ------------------------------------------------------------------
L4  PLATFORM SERVICES routing | batching | caching | guardrails
                      tool registry | secrets | quotas
    ------------------------------------------------------------------
L3  MODEL SERVICES    inference runtime | training | quantization
                      embedding | rerank | fine-tune
    ------------------------------------------------------------------
L2  DATA SERVICES     corpora | vector index | feature store | lineage
    ------------------------------------------------------------------
L1  INFRASTRUCTURE    GPUs | network | storage | observability

DEPENDENCIES POINT DOWNWARD ONLY.
a lower layer importing a higher one is a build failure, not a style note.
reason: otherwise one product's bug becomes the model layer's bug.
```

## Logical Model Names

```
  product code                     platform registry
  -----------                      ------------------
  chat("summarize this")  ---->    "chat-quality"
                                       |
                            +----------+----------+
                            |                     |
                    Llama-3.1-70B@abc      GPT-4-class@xyz
                    (v1)                   (fallback)

  swap the model under "chat-quality"
     -> zero product code changes
     -> one canary, one rollback
     -> SLOs and cost known for the LOGICAL name

  the highest-value abstraction in the whole platform.
  it is also the cheapest to build.
```

## Routing Dimensions

```
  request needs: vision? tools? json mode? region? tier? budget?

  | dimension      | type            | example                  |
  |----------------|-----------------|--------------------------|
  | capability     | FUNCTIONAL      | vision, function calling |
  | quality tier   | policy          | cheap vs frontier        |
  | latency tier   | SLO             | interactive vs batch     |
  | region         | COMPLIANCE      | data residency           |
  | health         | resilience      | breaker open             |
  | cost ceiling   | finops          | per-request budget       |

  BUG ALERT: using contains() instead of containsAll() lets a text-only request
  land on a vision-only deployment. capability is a SUPERSET requirement.
```

## Fallback and Circuit Breaking

```
  primary: model A
  |
  |-- timeout / 5xx / 429 --> retry once (backoff) --> breaker counter++
  |-- 400 / 401 / 403 / 404 / 422 --> DO NOT RETRY, move on
  |                                   (malformed input fails identically;
  |                                    retrying burns the whole chain's budget)
  |
  breaker: CLOSED --(>=50% failures over >=20 calls)--> OPEN
           OPEN --(openDuration elapsed)--> HALF_OPEN
           HALF_OPEN --(3 successes)--> CLOSED
           HALF_OPEN --(1 failure)--> OPEN

  without minCalls=20: 3 failures in a quiet window trip a healthy model.
  with 50 models x 12 windows/min: ~36 spurious trips/hour. minCalls is mandatory.

  FALLBACK SIZING:
    full capacity      -> survives total primary loss, 112 replicas
    degraded (40% cap) -> 79 replicas, 40% of peak at reduced quality
    pick explicitly and MEASURE the quality drop, do not assume it
```

## Capacity Math

```
  replicas = ceil( peak_rps / (service_rate_per_replica * 0.6) )
    peak 400 rps, 12 rps/replica  ->  56 replicas

  why 0.6 and not 0.9:
    rho    mean wait      replicas   p95 impact
    0.4   1.7/mu          84         comfortable
    0.6   2.5/mu          56         TARGET
    0.8   5/mu            42         p95 ~2x
    0.9   10/mu           38         p95 ~5x
    1.0   infinite        34         unstable

    1.5x the replicas buys 4x the tail-latency headroom.
    under-provisioning is the most common platform self-inflicted outage.
```

## Prompt Registry

```
  prompt_id: "support.reply"  v3
    template: "...{customer_tier} ... {issue_summary} ..."
    variables (typed): {customer_tier: ENUM, issue_summary: STRING<2000>}
    owner: support-eng@          <-- required
    risk tier: MEDIUM            <-- required
    evals: PASS (suite: support-intents-v7)
    rollout: 100% since 2026-10-01
    hash: sha256:...

  lifecycle:
    draft -> eval -> canary (0/5/25/100) -> active -> deprecated

  two invariants enforced in code:
    1. assertNoUnfilled()  -- {{var}} must never reach the model (Lab 03)
    2. promote() refuses a version whose gate failed

  => "every prompt change is a release" stops being a policy statement
     and becomes something the API will not let you violate.
```

## Guardrails as a Monotone Service

```
  platform default: {harmful, PII, injection, jailbreak} @ threshold 0.5

  product requests: {+off_policy} @ 0.4          ALLOWED  (tighter)
  product requests: {-injection}                  REJECTED (needs approval)

  tighten() is monotone by construction:
     enabled  = union(base, requested)
     threshold = min(base, requested)

  you can only ADD categories or LOWER thresholds.
  removing a guardrail is not something the API can grant.
```

## Tenancy and Isolation

```
  shared cache WITHOUT tenant in the key:
     tenant A caches "SECRET-A" under hash("shared")
     tenant B requests hash("shared")     ->  gets A's answer      <-- INCIDENT

  namespaced key:
     tenantId | authzScope | prefixHash
     the leak test is shipped WITH the class, because this bug is
     invisible in review and only appears as a security incident

  retrieval isolation:  PRE-FILTER inside the index query
     post-filtering can leak through ranking scores and is
     impossible to reason about at a review table

  isolation per component:
     routing/quota     logical, per-request attribution
     KV cache/adapters namespaced keys
     retrieval         index namespace + pre-filter
     logs/traces        tenant-tagged, retention policy, PII scrubbed
     training          per-tenant datasets + isolation tests
```

## Evaluation Gate

```
  every change runs:
    PLATFORM SUITES          PRODUCT SUITES
    ------------------------  ------------------------
    generic capability       intent-specific
    safety (Lab 10)          product rubric
    cost / latency
    multilingual

  report carries the manifest hash:
    report.manifestHash = sha256(model+prompt+index+tools+policy+gen+eval)

  gate blocks on:
    correctness delta outside budget   (any category)
    safety regression                  (zero tolerance)
    latency p95 / cost per request     (over budget)
    golden trace change                (needs review)
    MISSING TELEMETRY                  (treated as failure)

  eval cost: 1000 items x 3 passes x $0.02 = $60/release.
  $60 is not a reason to skip the gate.
```

## Adoption Funnel — The SLI Teams Forget

```
  teams requesting access        N       100%
  completed quickstart           N1   ->  conversion?
  passed first eval              N2   ->  conversion?
  shipped to production          N3   ->  conversion?
  still shipping at 90 days      N4   ->  retention?

  the stage with the biggest drop is where to invest
  median time-to-first-success is the platform's product metric

  a platform nobody uses is not a platform.
  teams that route around it take its guardrails with them.

  ADOPTION ANTI-PATTERNS:
    - onboarding slower than building bespoke
    - no playground (teams cannot self-evaluate)
    - silent breaking changes
    - support burden entirely on the platform team
    - over-gating production without a fast path for low risk
```

## Build Order

```
  phase 0   ONE model, ONE route, TELEMETRY FROM DAY ONE
  phase 1   logical model names + routing        <- highest value per line
  phase 2   prompt registry with owners
  phase 3   guardrails as a service
  phase 4   eval as a service + the gate
  phase 5   cost attribution + quotas
  phase 6   tool registry
  phase 7   multi-model fleet, canary, self-service
  phase 8   SDK + templates (adoption)
  phase 9   governance + compliance

  DO NOT BUILD FIRST:
    a vector database       (products need retrieval, not your database)
    a developer portal      (presentation, not capability)
    a multi-model fleet     (before you know which logical names matter)

  capability + gate first. the portal is a detail.
```

## Anti-Pattern Map

```
  anti-pattern                       consequence                  instead
  ---------------------------------  ---------------------------  ----------------------
  raw model endpoints only           30 unsafe safety impls      capability services
  one giant prompt per use case      unreviewable, unversioned   prompt registry
  no evaluation gate                 regressions ship silently   platform gate blocks
  shared cache, no tenant scoping    cross-tenant leak           namespaced keys + tests
  platform owns all reliability      bottleneck + burnout        tiered SLOs per route
  no cost attribution                nobody optimizes            per-team metering d1
  silent breaking changes            teams bypass                deprecation policy
  over-gating                        teams route around          fast path for low risk
  golden path only                   unusual needs fork it       documented extensions
  platform as a monolith             one outage takes all        loose coupling
  building infra before capability   6 months, no users          phase 0 first
```

## Self-Check

- [ ] Logical model names with SLOs and cost attached.
- [ ] Routing treats capability as a superset requirement.
- [ ] Retries skip 4xx; breakers have a `minCalls` guard.
- [ ] Fallback sized for primary failure, or degraded share measured.
- [ ] Prompt registry blocks promotion of a failing version.
- [ ] Guardrails tightenable only.
- [ ] Tenant in cache keys, pre-filter isolation for retrieval.
- [ ] Cost attributed per team from day one.
- [ ] Adoption funnel tracked as an SLI.