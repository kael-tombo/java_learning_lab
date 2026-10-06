# Lab 11: Model Quantization & Deployment — Real-World Project

## Project: Model Serving Platform with Quantization, Batching, and Capacity Planning

Design and build the serving tier for an LLM product: model quantization with
validated accuracy, kernel and runtime configuration, continuous batching, KV cache
management, capacity planning, deployment pipelines, and a rollback story when
throughput or quality regresses.

## Context

Serving an LLM is a capacity-planning problem wearing an ML costume. The questions
are concrete: which precision, which batch size, how much cache, what headroom, what
happens at 3x traffic, and what is the accuracy cost of each decision. This platform
answers them with measurements.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: non-contiguous,
  block-paged KV cache management with near-zero waste and copy-on-write prefix
  sharing is what makes high concurrency feasible on limited memory, which is the
  cache design in this platform.
- Text Generation Inference documentation —
  https://huggingface.co/docs/text-generation-inference/index — takeaway for this
  lab: at scale, throughput is dominated by KV cache capacity and batching policy
  rather than raw FLOPs, which is why the capacity model and the continuous-batching
  scheduler are the centerpiece of this platform rather than kernel micro-optimization.

## System Architecture

```
   +--------------------- MODEL PIPELINE ---------------------+
   |  base checkpoint -> precision selection -> quantization    |
   |  -> calibration -> accuracy gate -> artifact registry      |
   +-------------------------+---------------------------------+
                             |
   +-------------------------v---------------------------------+
   |  ARTIFACT REGISTRY                                        |
   |  model@version@precision@quant_method@calib_hash          |
   +-------------------------+---------------------------------+
                             |
   +-------------------------v---------------------------------+
   |  RUNTIME                                                  |
   |  +--------------------------------------------------+     |
   |  | Engine: graph opt -> kernel autotune -> warmup   |     |
   |  |  continuous batching | paged KV cache (block 16)  |     |
   |  |  prefix sharing | preemption | admission control  |     |
   |  +------------------------+-------------------------+     |
   |                           |                              |
   |   +-------------------+---v--------------------+        |
   |   | SCHEDULER: prefill/decode lanes, priority,  |        |
   |   | slot allocation, cache budget, batch sizing  |        |
   |   +--------------------+----------------------+        |
   +------------------------+------------------------------+
                            |
   +------------------------v-------------------------------+
   |  API: routing, auth, quota, streaming, SSE              |
   +------------------------+-------------------------------+
                            |
   +------------------------v-------------------------------+
   |  CAPACITY & OBSERVABILITY                               |
   |  TTFT | TPOT | throughput | cache waste | preemption   |
   |  batch size dist | utilization | cost per 1k tokens      |
   |  quality (Lab 09 eval) at every config change            |
   +--------------------------------------------------------+
```

## Component Specs

### 1. Model Pipeline and Precision Selection
Decision record per model, not per deployment:
```
precision:      INT8 weight-only, FP16 KV cache  (or INT4 for the largest model)
method:         RTN / AWQ / GPTQ / SmoothQuant + RTN
group size:     64
clip ratio:     searched on calibration data
excluded:       attention Q/K, LayerNorm, LM head, embeddings
calibration:    512 samples from deployment-representative traffic
```
- Accuracy gate: perplexity and task metrics must be within the agreed delta of
  fp16 on the calibration-matched eval set. A precision that fails the gate does not
  ship, regardless of the capacity win.
- Artifact identity includes the calibration hash — otherwise two artifacts with the
  same nominal precision are not comparable.

### 2. Calibration Data Management
- Sampled from real traffic, PII-scrubbed, stratified by intent and language.
- Versioned with a content hash; stored with the artifact.
- **Drift alerting**: monitor the input distribution (length, language, intent mix).
  If drift exceeds a threshold, re-calibrate before deploying the next version.
- Documented known failure: calibration/evaluation mismatch produces perplexity that
  looks fine in testing and behaves badly in production. Treat any unexplained
  production complaint about "weird outputs" as a calibration suspect.

### 3. Artifact Registry
- Key: `(base_model_hash, quantization_method, precision, group, calib_hash, runtime_version)`.
- Stores the model file, tokenizer, config, quantization metadata, calibration hash,
  accuracy report, and the measured performance profile for at least two GPU types.
- Promote/rollback/deprecate semantics identical to Lab 07.
- Never overwrite a published artifact.

### 4. Runtime Configuration
- Graph optimization passes; constant folding; operator fusion where the runtime
  supports it.
- Kernel selection and autotuning, with **tuning results cached per (GPU, shape,
  runtime version)** and shipped to the fleet — never autotuned in production.
- Warmup before the instance reports ready. Measure warmup and expose it in the
  readiness contract, or your p99 includes it.
- Unsupported-operator check in CI: an export that emits an unsupported op must fail
  the build, not the launch.

### 5. Paged KV Cache
- Block size 16 tokens; free list; per-request block tables.
- **Copy-on-write prefix sharing**: requests with a shared prefix (system prompt, few-
  shot examples) share blocks; on divergence, copy the block.
- Report `cache_waste = 1 - used_tokens/reserved_tokens` and
  `prefix_hit_rate = shared_reads/total_reads`.
- Cache eviction: preempt the request with the lowest
  `generated/generatedTotal` ratio; support recompute-on-resume, or fail fast if the
  caller opted out.

### 6. Continuous Batching and Scheduling
- Slots fill as requests arrive; finished sequences release immediately. No waiting
  for a whole batch to drain.
- **Prefill/decode lanes**: long prefills must not block decode. Chunked prefill
  interleaves prefill chunks with decode steps.
- Priority classes: interactive first, batch jobs drain in idle windows.
- Batch size chosen against cache budget, not against free memory:
  `cache_bytes_per_seq = 2 * layers * kvHeads * headDim * expectedLen * bytes`.
- Admission control: refuse (429) rather than accept and collapse.

### 7. Capacity Planning
Model, not guesswork:
```
service_rate_per_replica(mu) = f(precision, gpu, cache_bytes, batch policy)
target_utilization rho <= 0.6
replicas = ceil(peak_rps / (mu * rho))
```
- Validate the model against measurements at every deployment; a 20% error is a
  planning error that shows up as an outage.
- Headroom drivers: model size, context length distribution, output length
  distribution, traffic shape.
- Document the cost per 1k tokens at each configuration; tie it to the product's
  unit economics.

### 8. Quality Under Load
- Run the Lab 09 evaluation suite against the served configuration, not just the
  offline model file. Serving changes outputs: batching can change numerics, cache
  handling can change padding, quantization changes logits.
- Re-run after every precision, runtime, or scheduling change.
- Canary on both latency **and** quality; a fast model that answers worse is a
  regression.

### 9. Deployment and Rollback
- Blue-green across GPU pools; canary at 1% / 10% / 50% / 100% with automated gates
  on TTFT, TPOT, throughput, error rate, and quality.
- Automatic rollback on any gate breach; rollback must not require a redeploy (the
  previous artifact is already warm on the old pool).
- Pre-warm new artifacts on a canary pool before shifting traffic.
- Model version in every response header so any complaint can be attributed.

### 10. Observability
Per request: model version, precision, batch size at each step, TTFT, TPOT, total
latency, prompt/completion tokens, cache blocks used, preempted flag.
Aggregates: throughput, batch size distribution, cache waste, prefix hit rate,
preemption count, GPU utilization, memory high-water mark, cost per 1k tokens,
quality metrics (sampled).
Alerts: TTFT p95 breach, preemption spike, cache waste increase, prefix hit rate
drop, utilization saturation, quality regression.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Quality vs fp16 baseline | Within agreed delta on the eval suite |
| TTFT p50 | < 400 ms (interactive tier) |
| TTFT p99 | < 2.5 s |
| TPOT p50 | < 40 ms |
| Throughput per replica | 2,500 tok/s (target config) |
| Cache waste | < 5% |
| Prefix hit rate | > 60% (system-prompt-heavy traffic) |
| Preemption rate | < 1% of requests |
| Utilization target | <= 0.6 |
| Availability | 99.9% |
| Rollback time | < 5 min |
| Cost per 1k tokens | tracked and reported per config |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Quantization accuracy loss | Eval gate | Exclude sensitive tensors; clip search; higher precision |
| Calibration mismatch | Input drift alert | Re-calibrate on deployment traffic |
| Cache OOM at high batch | Memory high-water mark | Lower batch; GQA/INT8 cache; shorter outputs |
| Prefill blocks decode | TTFT spike with long prompts | Prefill lane; chunked prefill |
| Preemption thrash | Preemption counter | Admission control; fail fast for opted-out callers |
| Prefix sharing bug | Prefix hit rate anomaly | Copy-on-write tests; block-table verification |
| Autotune in production | Warmup time metric | Ship cached tuning results |
| Unsupported operator | Launch failure | CI graph check fails the build |
| Fleet heterogeneity | Per-GPU-type profile | Profile stored in the registry; schedule accordingly |
| Queue collapse at peak | Utilization saturation | Scale ahead of the curve; 429 backpressure |
| Numerics change under batching | Quality vs offline delta | Quality canary; fixed batch-invariant kernels |
| Cost surprise | Cost per 1k tokens alert | Config review gate |
| Rollback slow | Rollback time metric | Keep previous pool warm |

## Milestones

- **M1** — precision decision record with accuracy gate; artifact registry.
- **M2** — calibration pipeline with versioning and drift alerting.
- **M3** — runtime config, cached autotuning, warmup contract.
- **M4** — paged KV cache with copy-on-write prefix sharing.
- **M5** — continuous batching with prefill/decode lanes.
- **M6** — admission control and capacity model validated against measurements.
- **M7** — quality-under-load evaluation integrated with the Lab 09 gate.
- **M8** — canary deployment with automatic rollback.
- **M9** — full observability and cost attribution.
- **M10** — game day: 3x traffic spike with a degraded cache budget.

## Deliverables

1. Serving runtime configuration, scheduler, cache manager.
2. Artifact registry with accuracy reports and performance profiles.
3. Capacity model validated against measurements.
4. `REPORT.md` — precision/latency/cost trade with the shipped decision and the
   measured accuracy delta.
5. `runbook.md` — triage for TTFT regression, cache exhaustion, throughput drop,
   and rollback.

## Definition of Done

- [ ] Quality within the agreed delta of fp16 on the eval suite, measured on the
      served configuration.
- [ ] Throughput model within 20% of measurement at the target config.
- [ ] Cache waste below 5% and prefix hit rate above 60% in steady state.
- [ ] Rollback completes in under 5 minutes with no rebuild.
- [ ] Load test at 3x mean traffic without OOM or unbounded queueing.
- [ ] Cost per 1k tokens published per configuration.
- [ ] A deliberately bad precision configuration is blocked by the accuracy gate.