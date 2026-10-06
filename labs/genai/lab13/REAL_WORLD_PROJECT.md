# Lab 13: Context Window Management — Real-World Project

## Project: Long-Context Platform for Document and Conversation Workloads

Design and build the context management layer for a product handling long documents
and long conversations: retrieval and stuffing decisions, context assembly under a
budget, KV cache and memory architecture, position extension for a model trained on a
short window, multi-turn compaction, and the diagnostics that catch degradation before
users do.

## Context

"Context window management" is where long-context claims meet production reality. The
engineering work is deciding what goes in, keeping memory bounded, preserving
citations and policy, and knowing when long context is actively hurting accuracy.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: block-paged KV cache with
  near-zero waste and copy-on-write prefix sharing is what makes long-context serving
  fit at concurrency, which is the memory architecture this platform builds on.
- "RoFormer: Enhanced Transformer with Rotary Position Embedding" (Su et al., submitted
  24 Apr 2021; v4 30 May 2023) — https://arxiv.org/abs/2104.09864 — takeaway for this
  lab: rotary position embeddings encode relative position directly in the attention
  score and permit extrapolation beyond the trained window, which is the basis for the
  context-extension strategy applied to a model trained on a 4k window here.

## System Architecture

```
   REQUEST
  (query, retrieved chunks, conversation history, policy, schema)
        |
   +----v------------------------------------------------------------------+
   | INTAKE                                                                |
   |  classify: single-shot | multi-turn | document-review                  |
   |  strip/never-drop: system policy, schema, the question itself          |
   +----+------------------------------------------------------------------+
        |
   +----v------------------------------------------------------------------+
   | STRATEGY SELECTOR                                                     |
   |  one fact from a big corpus  -> RETRIEVE (short context)               |
   |  comparison across N docs    -> MAP-REDUCE (per-doc summary)           |
   |  long session               -> STATE + WINDOW (structured compaction)|
   |  genuinely long input       -> STUFF (window permitting)              |
   +----+------------------------------------------------------------------+
        |
   +----v------------------------------------------------------------------+
   | COMPRESSION                                                          |
   |  sentence-level inside chunks | hierarchical summaries | dedupe      |
   |  provenance preserved for citations                                        |
   +----+------------------------------------------------------------------+
        |
   +----v------------------------------------------------------------------+
   | ASSEMBLY                                                             |
   |  priority fill under budget | ordering: best evidence LAST           |
   |  drop reporting | invariant assertions                                    |
   +----+------------------------------------------------------------------+
        |
   +----v------------------------------------------------------------------+
   | MODEL RUNTIME                                                        |
   |  RoPE-scaled positions | GQA | sliding window + sinks | paged KV    |
   |  prefix sharing (COW) | KV cache quantization | long-context lane    |
   +----+------------------------------------------------------------------+
        |
   +----v------------------------------------------------------------------+
   | DIAGNOSTICS                                                          |
   |  attention entropy | citation validity | density | cost | TTFT      |
   |  long-context degradation detection -> alert + strategy switch         |
   +-----------------------------------------------------------------------+
```

## Component Specs

### 1. Intake and Classification
- Determine the request type (single-shot, multi-turn, document review, agent step).
- Protect a set of **never-drop** blocks: system policy, output schema, the current
  question, approval context, tool permissions. Asserted by test on every assembly.
- Reject or truncate at the edge: oversized single inputs get chunked before they
  reach the runtime.

### 2. Strategy Selector
A decision table, not a heuristic soup:

| Condition | Strategy |
|-----------|----------|
| Corpus > 100 chunks, single fact needed | Retrieve top-k (2-5 chunks) |
| >= 10 documents to compare or synthesize | Map-reduce over documents |
| Session exceeds 60% of window | Structured state + recent window |
| Question spans a long document | Chunked stuffing within a sub-window |
| Repeated entity mentions across turns | Retrieve from history + state |
| Legal/contract review over many docs | Map-reduce with per-doc citations |

Every strategy decision is logged with its reason; the log is what lets you discover
that a large class of requests is being mis-strategized.

### 3. Compression
- **Sentence-level** inside selected chunks; chunk ids and citations preserved.
- **Hierarchical** for multi-document: per-document extractive summary, then a
  synthesis stage over summaries.
- **Dedupe** near-identical chunks (syndicated policies, duplicated boilerplate).
- **Table/figure handling**: keep tables whole and add a text rendering; never
  summarize a table into prose and lose numbers.
- Metrics: tokens per request, compression ratio, citation validity rate, recall@k.
  Citation validity is a gate: compression that breaks citations does not ship.

### 4. Assembly Under Budget
- Priority: policy > instruction > question > top evidence > history state > filler.
- Emit evidence in ascending score order so the best chunk lands last, nearest the
  question; restate the operative instruction at the end.
- Keep the output schema adjacent to the instruction that references it.
- Report per-request: budget, used, dropped (by priority), and the utilization ratio.
- Never-drop invariants asserted in tests and re-checked at runtime (cheap assertion).

### 5. Position Extension for a Short-Trained Model
If the deployed model was trained to 4k and you need more:
- Choose RoPE scaling (interpolation / NTK-aware / per-dimension) and fine-tune on
  long sequences with interpolated positions.
- Validate with the perplexity table across 1x-8x and the task eval suite.
- Keep a **headroom cap**: do not ship beyond the length where your eval curve bends,
  even if the context window nominally allows it. Publish the validated length.
- Monitor attention entropy as a live diagnostic; collapse is the early signal that a
  request is past the model's usable range.

### 6. KV Cache Architecture
- GQA (or MQA) for the primary lever; sliding window with attention sinks for bounded
  memory; KV cache quantization for long-context sessions.
- Paged block allocation with copy-on-write prefix sharing for the stable prefix
  (system + policy + few-shot), which is a large fraction of real traffic.
- Report cache bytes per sequence, waste ratio, and prefix hit rate.
- Admission control based on projected cache bytes, not free memory.

### 7. Multi-Turn Compaction
- Structured state (facts, decisions, open items, slots) plus a verbatim recent
  window. Extraction is deterministic/pattern-based where possible; model-based
  extraction is validated against a labeled set before use.
- Compaction triggers on a threshold of window utilization, not at 100%.
- The system message is never compacted (Lab 10 policy).
- Track "early-fact recall": can the assistant still answer a question whose answer
  appeared 40 turns ago?

### 8. Diagnostics and Degradation Detection
Per request: attention entropy, evidence density (relevant tokens / total),
citation validity, tokens in/out, TTFT, cost.
Per aggregate:
- **long-context degradation curve**: accuracy vs stuffed-context length. Once the
  curve bends, the strategy selector switches from stuffing to retrieval for that
  request class automatically.
- alert when the average request starts stuffing where it previously retrieved.
- alert on early-fact recall regression after a compaction change.

### 9. Evaluation
- Task accuracy per strategy.
- Citation validity and citation support rate.
- Early-fact recall for multi-turn.
- Stuffed vs retrieved head-to-head on identical questions.
- Cost per request and TTFT per strategy.
- A long-context benchmark in CI so a model or config change that degrades
  long-context behaviour is caught before deploy.

### 10. Operations
- Config change (strategy table, window size, budget) is a reviewed, versioned change
  with an eval result attached.
- Per-request context trace retained (sampled) for debugging: what was included, what
  was dropped, in what order.
- Runbook for "answers got worse after the model upgrade" — check validated length,
  entropy trace, strategy logs.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Input tokens per request | Reduced >= 50% vs stuffing baseline |
| Citation validity | >= 0.98 |
| Recall@5 (retrieval strategy) | >= 0.90 |
| Early-fact recall (40 turns back) | >= 0.85 |
| Compression ratio | >= 2x with quality inside budget |
| Cache bytes per session | Within device plan |
| Prefix hit rate | > 60% |
| TTFT p95 | <= 3 s at p95 context length |
| Never-drop invariant violations | 0 |
| Stuffed-context accuracy | Never better than retrieval on the eval set |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Stuffed context degrades answers | Degradation curve | Strategy switch to retrieval |
| Citations break after compression | Citation validity metric | Sentence-level only; keep chunk ids |
| Table numbers lost in summarization | Table-handling test | Keep tables whole; add text rendering |
| KV cache OOM at long context | Cache bytes metric | GQA, window, KV quantization |
| Attention entropy collapse | Entropy monitoring | Cap at the validated length |
| Position extension degrades quality | Perplexity + eval table | Publish a validated-length cap |
| Compaction loses early facts | Early-fact recall metric | Structured state extraction |
| System policy compacted | Never-drop invariant test | Runtime assertion |
| Best evidence buried in the middle | Ordering A/B eval | Emit ascending, best last |
| Session prompt grows unbounded | Utilization alert | Trigger compaction at 60% |
| Prefix sharing corrupts output | Prefix hit rate + correctness | Copy-on-write verification |
| Strategy mis-selection | Strategy log analysis | Decision table plus review |
| Long-context latency spike | TTFT by length bucket | Long-context lane, chunked prefill |
| Cost regression | Cost per request by strategy | Strategy-level cost SLOs |

## Milestones

- **M1** — intake with never-drop invariants asserted at runtime.
- **M2** — strategy selector with a logged decision table.
- **M3** — compression with citation validity gated.
- **M4** — assembly with priority fill, ordering, and drop reporting.
- **M5** — position extension validated; published length cap.
- **M6** — KV cache architecture (GQA + window + quantization + prefix sharing).
- **M7** — multi-turn compaction with structured state; early-fact recall measured.
- **M8** — diagnostics: entropy, density, degradation curve, alerting.
- **M9** — long-context benchmark in CI.
- **M10** — game day: model upgrade past the validated length, verify degradation
      is detected before users report it.

## Deliverables

1. Strategy selector, compression, and assembly services.
2. Cache architecture configuration with a memory plan.
3. Long-context benchmark harness in CI.
4. `REPORT.md` — strategy comparison, degradation curve, validated length, cost.
5. `runbook.md` — triage for "answers got worse": length, entropy, strategy, ordering.

## Definition of Done

- [ ] Input tokens per request reduced >= 50% versus the stuffing baseline.
- [ ] Citation validity >= 0.98 after compression.
- [ ] Never-drop invariants never violated across 10,000 sampled requests.
- [ ] Early-fact recall >= 0.85 after compaction.
- [ ] Long-context degradation curve measured and used to drive a strategy switch.
- [ ] Degradation detected within one benchmark run of a model upgrade past the
      validated length.
- [ ] Stuffed context never wins on the eval set (verified, not assumed).