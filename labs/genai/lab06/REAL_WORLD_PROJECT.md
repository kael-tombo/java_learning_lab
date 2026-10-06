# Lab 06: Fine-Tuning with LoRA/QLoRA — Real-World Project

## Project: Multi-Tenant LoRA Fine-Tuning Platform

Design and build the platform a team uses to produce, evaluate, version, and serve
LoRA/QLoRA adapters for many tasks and many tenants — including dataset management,
training orchestration on rented GPUs, quality gates, and adapter serving.

## Context

Fine-tuning is now a routine product surface. The hard work is not the training
loop — it is everything around it: datasets that are versioned and consented,
experiments that are comparable, gates that block bad adapters from production, and
serving many adapters without duplicating base weights.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., submitted 16 Jun
  2021; v2 16 Feb 2022) — https://arxiv.org/abs/2106.09685 — takeaway for this lab:
  the low-rank hypothesis plus the `alpha/r` scaling and zero-init of `B` are the
  core design decisions; the paper's inference-throughput claim is why the serving
  design merges adapters for single-model deployments and uses a shared base.
- "QLoRA: Efficient Finetuning of Quantized LLMs" (Dettmers et al., submitted 28 May
  2023; v2 17 Sep 2023) — https://arxiv.org/abs/2305.14314 — takeaway for this lab:
  NF4 + double quantization + paged optimizers are what make single-GPU fine-tuning of
  large models practical, justifying the 4-bit base weights, quantized scale tensors,
  and the memory planner in this platform.

## System Architecture

```
                     dataset sources
              (curated, consented, licensed)
                          |
                 +--------v---------+
                 | Dataset Registry |
                 |  versioned rows  |
                 |  provenance      |
                 |  PII scan        |
                 +--------+---------+
                          |
   +----------------------v-----------------------+
   |  Experiment Spec (dataset version, base model |
   |  hash, rank, alpha, targets, LR, masking)   |
   +----------------------+-----------------------+
                          |
                 +--------v---------+
                 | Experiment Queue|  priority, quota, GPU lease
                 +--------+---------+
                          |
        +-----------------v------------------+
        |  Training Worker (one per GPU)     |
        |  load base (4-bit NF4)             |
        |  inject LoRA into target modules   |
        |  train with masked loss, clip,    |
        |  cosine schedule, checkpointing   |
        |  emit: adapter, metrics, log      |
        +-----------------+------------------+
                          |
                 +--------v---------+
                 | Evaluation Gate  |  task metrics + safety + regression
                 |  pass -> registry|  fail -> quarantine, no publish
                 +--------+---------+
                          |
                 +--------v---------+
                 | Adapter Registry |  (tenant, task) -> version, metrics
                 +--------+---------+
                          |
        +-----------------v------------------+
        |  Serving Plane                     |
        |  one base model weight set          |
        |  adapter loaded per request/tenant |
        |  merged cache per (base, adapter)  |
        +-----------------+------------------+
                          |
        +-----------------v------------------+
        |  Observability: quality, cost,     |
        |  GPU utilization, adapter drift,   |
        |  serving latency, rollback log     |
        +------------------------------------+
```

## Component Specs

### 1. Dataset Registry
- Every row carries: `datasetId`, `version`, `provenance`, `license`, `consent`,
  `contentHash`, `createdAt`.
- PII/secret scanning at ingest; quarantine on hit, never silently drop.
- Snapshot immutability: a training run pins `(datasetId, version)`. Post-hoc edits
  create a new version so results stay reproducible.
- Prompt masking applied and recorded per dataset (which roles are trained).

### 2. Experiment Spec and Reproducibility
```yaml
baseModel: hf:meta-llama/Llama-3.1-8B@<commit-sha>
baseFormat: nf4
targets: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
rank: 16
alpha: 32
dropout: 0.05
lr: 2e-4
schedule: cosine, warmupRatio: 0.03
epochs: 2
batch: 16, gradAccum: 2
maxSeqLen: 2048
seed: 12345
dataset: {id: support-tickets, version: v7}
masking: {trainOnUser: false}
```
The base model is pinned by **commit SHA**, not by a floating tag. Otherwise
"reproducing last quarter's adapter" is impossible.

### 3. Training Worker
- Load base in 4-bit NF4 with double quantization; inject adapters into the
  declared target modules only.
- Assert `B == 0` at init and log the initial loss (must be <= base loss).
- Gradient checkpointing, bf16 compute, flash attention if available.
- Global-norm clipping; log pre-clip norm so saturated clipping is visible.
- Checkpoint adapters every N steps; on crash, resume from the adapter checkpoint.
- Emit structured metrics per step; write `adapter.bin` + `metrics.json`.
- Emit a hardware/env manifest (GPU, driver, library versions) for the run.

### 4. Evaluation Gate
Blocked publish unless all pass:
- Target-task metric (exact match / F1 / rubric score) beats the **base model**
  with a stated margin, not beats zero.
- Held-out formatting validity >= 99%.
- General-capability regression within an agreed delta on a fixed probe set.
- Safety probes: no policy violations on the red-team set (Lab 10).
- Leakage check: no memorized canary string from a public benchmark.
- Report includes cost (GPU-hours) so cheap wins are preferred.

### 5. Adapter Registry and Versioning
- Key: `(tenant, task) -> version`. `promote`, `rollback`, `deprecate`.
- Never overwrite a published version; every promotion is an append.
- Keep at most N active adapters per base model (stale adapter GC).
- Aliases (`production`, `canary`) point at versions so serving config is stable.

### 6. Serving
- One base weight set per base model; adapters loaded on demand from a local cache.
- Two deployment modes: runtime adapter path (fast swap, ~2-5% overhead) and
  merged weights (fastest inference, slow swap). Choose by tenant count and
  adapter churn.
- Per-(base, adapter) merged-weight cache with an LRU and a memory budget.
- Warm the cache before shifting traffic; never merge on the request path.
- Rollback = alias repoint, effective on the next request, no redeploy.

### 7. Observability and Cost
- Per-experiment: GPU hours, peak memory, throughput, final/eval loss, gate verdict.
- Per-serving-request: adapter id+version, tokens, latency, cache hit.
- Alert on: GPU idle while queue is non-empty; OOM events; gate failure rate spike;
  adapter cache hit rate drop; quality drift for a promoted adapter.

### 8. Multi-Tenant Isolation
- Per-tenant quotas on experiments and GPU minutes.
- Adapter namespacing by tenant; serving enforces the tenant before loading.
- Training data segregated by tenant; a leak test asserts no adapter was trained
  on another tenant's rows.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Base model fidelity | quantized-base loss delta < 2% vs bf16 |
| Adapter eval determinism | same spec + same seed -> identical metrics |
| Peak memory (8B, 4-bit, r=16, seq 2048, batch 4) | fits 24 GB with headroom |
| Training throughput | > 3,000 tokens/s per A10G with checkpointing |
| Adapter size | < 1% of base parameters |
| Serving p95 latency overhead (runtime path) | < 5% |
| Rollback time | < 60 s, config change only |
| Gate false-negative rate | monitored; every failure triaged |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Silent base model drift | Adapter eval drops vs history | Pin base by commit SHA; canary re-eval |
| Adapter published with no eval improvement | Gate margin check | Gate blocks; report shows base-vs-adapter |
| OOM at long sequences | Peak memory metric | Reduce batch, enable checkpointing, cap `maxSeqLen` |
| Loss diverges | Loss/grad-norm curve alarm | Lower LR, verify `B=0` init, enable clipping |
| Degenerate outputs (repetition) | Repetition probe in gate | Add diversity metric; quarantine adapter |
| Prompt masking wrong | Formatting validity metric | Dataset spec records masking config |
| Adapter cache thrashing | Cache hit rate drop | Pin hot adapters; pre-warm; raise cache budget |
| Cross-tenant data leak | Isolation test | Per-tenant dataset segregation + leak test |
| Training crash mid-run | Job status | Adapter checkpoint + resume |
| Rollback too slow | Rollback time metric | Alias repoint, no rebuild |

## Milestones

- **M1** — dataset registry with versions, provenance, PII quarantine.
- **M2** — experiment spec + reproducible run manifest.
- **M3** — training worker on 4-bit NF4 with init-loss assertion.
- **M4** — evaluation gate with base-relative margin and regression probes.
- **M5** — adapter registry with promote/rollback/deprecate and GC.
- **M6** — serving: runtime path + merged cache with pre-warm.
- **M7** — observability: quality, cost, GPU utilization, drift.
- **M8** — multi-tenant isolation tests.
- **M9** — game day: kill the base model download path and verify rollback.

## Deliverables

1. Registry, queue, training worker, gate, serving adapters.
2. `EvalHarness` with the gate criteria and the regression probe set.
3. `REPORT.md` — quality vs cost table across rank/alpha/quantization configs.
4. `runbook.md` — gate failure triage and rollback procedure.
5. `EXPERIMENTS.md` — how to reproduce any published adapter by spec.

## Definition of Done

- [ ] Any published adapter is reproducible from its spec alone.
- [ ] Gate blocks every deliberately degraded adapter in the test matrix.
- [ ] Multi-tenant isolation tests pass for 1000 randomized cross-tenant requests.
- [ ] Rollback to the previous adapter completes in under 60 s with no rebuild.
- [ ] Serving p95 overhead of the adapter path under the stated target.
- [ ] An engineer unfamiliar with the project can run a training job from `EXPERIMENTS.md`.