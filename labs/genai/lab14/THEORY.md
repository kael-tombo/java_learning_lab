# Lab 14: LLMOps (LLM Operations) — Theory

## 1. LLMOps vs MLOps

MLOps assumes a model is a file you train, validate, and deploy. LLM systems differ:

| | Classical ML | LLM systems |
|---|-------------|-------------|
| Artifact | Model + features | Model + prompt + retrieval + tools + policy |
| Determinism | High | Low; nondeterministic decoding |
| Output space | Fixed labels | Free-form text |
| "Correct" | Defined | Contested; needs rubric |
| Change surface | Code, data, model | All of the above, per prompt |
| Cost per request | Near zero | Material, variable by input |
| Failure modes | Metrics drop | Silent quality drift, injection, cost spike |
| Iteration | Hours | Minutes (prompt), weeks (model) |
| Eval | Held-out accuracy | Multi-dimensional, partly judge-based |

The practical consequence: **your production system is the prompt plus the
retrieval index plus the tools plus the policy, not the model file**. Most incidents
trace to one of those four.

## 2. The LLMOps Lifecycle

```
  +---------------------------------------------------------------+
  | 1. DATA            prompts, documents, feedback, conversations |
  +---------------------------------------------------------------+
                              |
  +---------------------------------------------------------------+
  | 2. EVALUATE        offline suite, regression gate, red team    |
  +---------------------------------------------------------------+
                              |
  +---------------------------------------------------------------+
  | 3. PROMPT/CONFIG   versioning, experiments, A/B, rollback     |
  +---------------------------------------------------------------+
                              |
  +---------------------------------------------------------------+
  | 4. SERVE           gateway, routing, batching, guardrails     |
  +---------------------------------------------------------------+
                              |
  +---------------------------------------------------------------+
  | 5. OBSERVE         metrics, traces, drift, cost, quality      |
  +---------------------------------------------------------------+
                              |
                 +------------+-------------+
                 |                          |
       feedback to (1) and (2)      incident -> safe mode
```

The loop closes through feedback. Without labeled feedback from production, step 2
degrades into guessing.

## 3. What to Version

The release unit is a bundle, and the bundle hash must appear in every response:

```
ReleaseManifest {
  modelId, modelVersion
  promptTemplateId, promptVersion
  indexVersion (corpus + embedding model)
  toolRegistryVersion          // schemas + permissions
  policyVersion                // safety policy, constitution
  generationConfig             // temperature, top_p, max_tokens, stop
  evaluatorVersion             // which judge, which metrics
}
```

Version anything whose change can alter a response. A prompt edit is a release. A
retrieval index rebuild is a release. A guardrail change is a release. This is the
single most important operational habit, because it makes "was this the old prompt?"
answerable in seconds instead of hours.

## 4. Golden / Canary / Blue-Green

| Strategy | Traffic split | Rollback | Use when |
|----------|--------------|----------|----------|
| Shadow | 100% mirrored, not served | n/a | Measuring a new config with zero user impact |
| Canary | 1% -> 10% -> 50% -> 100% | traffic flip | Most releases |
| Blue-green | 0% or 100% | instant flip | Config-only changes needing instant revert |
| A/B | 50/50 by user | flip | Comparing two versions for a decision |

Rules that matter:
- Gate every step on **automated** metrics (quality, safety, latency, cost).
- Assign by **user**, not by request, so a user does not see two versions in a session.
- Require a minimum sample size per step; do not decide on 50 requests.
- Automatic rollback on breach, not a human decision under pressure.

## 5. Metrics That Matter

### Serving / infrastructure
```
TTFT p50/p95/p99, TPOT p50/p95
throughput (tokens/s, requests/s)
error rate by class, timeout rate, retry rate
queue depth, batch size distribution, preemption rate
```

### Cost
```
cost per request, per feature, per tenant
input/output token split
cache hit rate (prefix + semantic)
cost per successful outcome       <-- the metric finance cares about
```

### Quality (sampled, since full scoring is expensive)
```
task correctness per intent
faithfulness / citation validity
abstention rate and false-decline rate
refusal + over-refusal on the safety suite
win rate vs the previous release
```

### Drift
```
intent mix, query length, language mix
retrieval hit-rate distribution, top-score distribution
refusal rate, escalation rate
user re-ask rate, copy rate, abandonment
```

## 6. Sampling Strategy for Online Evaluation

You cannot score every production response with a judge. Sample:

```
score everything:  cheap signals only (schema valid, refusal, length, PII)
sample for judging:
  - stratified random (unbiased quality estimate)
  - all errors and all escalations (fix the worst)
  - all high-value users (protect the revenue)
  - all responses where signals disagree (schema valid but weird)
```

Report the random sample as the quality metric; the targeted samples drive the fix
queue. Mixing them biases the metric.

## 7. Tracing

A trace must reconstruct the whole response:

```
trace_id
  request { query, user, tenant, features }
  retrieval { index_version, chunk_ids, scores, rerank_margins }
  prompt { template_id, version, rendered_hash, token_count }
  generation { model_version, params, ttft, tpot, tokens }
  guardrails { input_findings, output_verdict, stage_attribution }
  tools { calls, args_hash, results_hash, approvals }
  cost { breakdown }
  outcome { citations_valid, abstained, user_signal }
```

Hash long payloads instead of inlining them; store a pointer. A trace that logs full
prompts containing PII is a liability (Lab 10).

## 8. Drift Detection

Distribution shift is the failure that produces no alert, because every individual
response looks fine.

Inputs to watch: intent mix, prompt length, language, retrieval top-score, refusal
rate. Method: compare a rolling window against a reference window.

```
PSI = sum_i (p_i - q_i) * ln(p_i / q_i)          Population Stability Index
PSI < 0.1  stable
PSI > 0.25 significant shift -> investigate
```

On a shift, do three things: freeze the release process, sample and hand-inspect
responses in the shifted segment, and re-evaluate whether the eval set still
represents traffic.

## 9. Feedback Loops

```
thumbs up/down         -> preference pairs (Lab 07)
regenerate clicks      -> implicit negative on the first response
copy/paste             -> partial positive
abandonment            -> negative
escalation to human    -> high-value labeled item
support tickets        -> real user pain, gold answers from the human agent
implicit corrections   -> the user fixing your answer is a labeled pair
```

Turn these into a prioritized review queue (by user value x error severity), label
with the Lab 09 schema, and feed the results into the eval suite. This is how an eval
set stays representative.

## 10. Incident Response for LLM Systems

Alert classes and the first question for each:

| Alert | First question | Common cause |
|-------|----------------|--------------|
| Latency spike | Did traffic or context length change? | Prefill, cache eviction, retries |
| Error spike | Which error class? | Upstream, guardrail fail-closed, OOM |
| Quality drop | Did any of the 5 versioned components change? | Prompt or index, usually |
| Refusal spike | Was there a policy or guardrail change? | Threshold tuning |
| Cost spike | Which cost line? | Cache miss, context growth, retry loop |
| Injection alerts | Which channel? | New data source, new tool |

Containment: safe mode (Lab 10), disable a tool, disable retrieval, pin the previous
prompt version, roll back the model, shed load.

The single most useful runbook entry is the **component version diff**, because most
quality incidents are a prompt or index change.

## 11. Safe Operations Practices

- **Freeze during incidents.** No releases while investigating.
- **Reproduce from the trace.** The trace is the reproduction.
- **One change at a time.** Otherwise attribution is impossible.
- **Rollback must be config, not a rebuild.** If rollback takes 20 minutes, you will
  make bad decisions under pressure.
- **Everything is a release.** No unversioned prompt tweaks.
- **Blast-radius limits.** Any single release touches a bounded slice; feature flags
  with independent kill switches.
- **Practice the drill.** Untested runbooks are fiction.

## 12. Cost as a First-Class Signal

Most teams monitor cost as a finance report. In LLMOps it is an engineering signal:
a sudden cost increase is usually a **quality or safety regression** (retry loops,
cache misses, longer outputs, more refusals, runaway agent steps). Alert on cost per
request with the same urgency as latency.

## Key Equations

```
PSI = sum (p_i - q_i) ln(p_i/q_i)
sample_rate_for_quality = budget / (judge_cost_per_item)
deployment_ladder = [1%, 10%, 50%, 100%] with per-step min sample size
blast_radius = fraction of traffic a release can affect
release_hash = sha256(manifest fields)
```