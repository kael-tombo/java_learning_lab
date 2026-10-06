# Lab 13: Context Window Management — Mini Project

## Project: Context Budget Manager with Long-Context Diagnostics

Build the context management stack in Java 21 — positional encodings, windowed
attention with sinks, a ring KV cache, compression, priority assembly, and map-reduce
— and produce the measurements that justify each choice.

## Goal

A manager that takes a request (query, retrieved chunks, history, policy), assembles
the optimal context within a token budget, and reports exactly what was dropped, what
it cost, and what the diagnostics say about long-context health.

## Requirements

### Phase 1: Positional Encodings
- [ ] Sinusoidal encoder with the relative-offset identity verified numerically.
- [ ] RoPE with position scaling (none / interpolation / NTK); relative property tested.
- [ ] ALiBi with geometric slopes; verify extrapolation behaviour.
- [ ] Base sweep for RoPE (1e4, 1e5, 1e6) on a synthetic long-range task.
- [ ] Report perplexity at 1x, 2x, 4x, 8x the trained length for each method.

### Phase 2: Attention Entropy Diagnostic
- [ ] `EntropyMonitor` computing normalized entropy `H/log K` per query.
- [ ] Run under all three position encodings past the trained window.
- [ ] Produce the collapse signature and a per-step entropy trace.

### Phase 3: Sliding Window with Sinks
- [ ] Windowed attention with configurable `W` and sink count.
- [ ] Verify each query attends exactly `min(i+1, W + sinks)` keys.
- [ ] Ablation: sinks 0, 2, 4, 8 on the long-range task.
- [ ] Operation-count comparison vs full attention.

### Phase 4: Ring KV Cache
- [ ] `KvCacheRing` with modular indexing; verify parity with a full cache when
      `W > seq_len`.
- [ ] Eviction verification: evicted positions return `-1`, never stale data.
- [ ] `CacheCalculator` grid: which configs fit 8/24/80 GB.

### Phase 5: KV Cache Quantization
- [ ] INT8 per-head quantization of cached K and V; reconstruction error reported.
- [ ] Memory saving measured against fp16 and INT4.

### Phase 6: Compression
- [ ] Sentence-level compressor inside selected chunks; provenance preserved.
- [ ] Hierarchical map-reduce summarizer over 50 documents.
- [ ] Compression ratio vs quality delta curve.

### Phase 7: Context Ordering
- [ ] Assemble the same evidence in four orderings; measure accuracy.
- [ ] Demonstrate the "lost in the middle" effect on the synthetic corpus.

### Phase 8: History Compaction
- [ ] `StructuredState + RecentWindow` compactor with pattern-based extraction.
- [ ] Compare truncation-only, summary, and structured state on early-fact recall.

### Phase 9: Priority Budget Assembler
- [ ] Budget fill with priority ordering and drop reporting.
- [ ] Invariant tests: schema, system message, and question always survive.
- [ ] Report `used`, `dropped`, and utilization.

### Phase 10: Long Context vs Retrieval
- [ ] Compare 50k stuffed context vs 800-token retrieved context on cost, latency,
      and accuracy.

## Directory Layout

```
lab13/
  src/com/genai/lab13/{pos,attn,cache,compress,order}/
  corpus/docs/*.txt        (50 documents)
  out/reports/positions.csv
  out/reports/entropy.csv
  out/reports/compression.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — three position encodings; relative properties verified.
2. **M2** — perplexity table at 1x-8x trained length produced.
3. **M3** — entropy monitor shows collapse for unscaled, stability for interpolated.
4. **M4** — sliding window verified; sinks ablation run.
5. **M5** — ring cache parity with full cache; eviction verified.
6. **M6** — cache calculator produces a "what fits" plan list.
7. **M7** — compression ratio vs quality curve; provenance preserved.
8. **M8** — ordering ablation reproduces the primacy/recency effect.
9. **M9** — history compaction: structured state beats truncation on early facts.
10. **M10** — stuffed vs retrieved comparison; assembly invariants asserted.

## Acceptance Criteria

- [ ] Sinusoidal relative identity holds to 1e-9.
- [ ] RoPE score depends only on `i - j` to 1e-9.
- [ ] Interpolation reduces 8x-length perplexity by at least 3x versus unscaled.
- [ ] Sliding-window key counts exactly match `min(i+1, W + sinks)`.
- [ ] Ring cache output matches a full cache when `W > seq_len`.
- [ ] Evicted positions never return stale data.
- [ ] Compression cuts tokens >= 50% with quality delta inside budget.
- [ ] Best-evidence-last ordering beats best-evidence-first by a measurable margin.
- [ ] Assembly invariants hold for every budget.
- [ ] Stuffed context is shown to be worse than retrieval on the same corpus.

## Stretch Goals

- [ ] YaRN-style per-dimension scaling and a perplexity comparison.
- [ ] Cross-request prefix sharing with copy-on-write block tables.
- [ ] Latent compression via a trained token autoencoder.
- [ ] Adaptive window size per request type.
- [ ] Token-dropping compressor with fine-tuning to tolerate drops.
- [ ] Attention-sink token identification (which tokens become sinks).
- [ ] Cache eviction policy comparison (LRU vs LFU vs LRU+TTL).
- [ ] Per-document question fan-out vs map-reduce.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| RoPE score depends on absolute position | Wrong frequency table or pairing |
| Interpolation worse inside the window | No fine-tuning; resolution loss |
| Sliding window collapses | No attention sinks |
| Ring cache reads stale entries | `slotFor` not returning `-1` for evicted |
| Entropy pinned at 0 or 1 | Score scaling bug, or genuine collapse |
| Compression kills recall | Dropping whole chunks instead of sentences |
| Citations break after compression | Chunk id dropped |
| History compactor eats policy | Compaction applied to index 0 |
| Ordering change has no effect | Corpus too small or task too easy |
| Prefill model wrong | FFN term omitted |

## Definition of Done

`REPORT.md` contains: the position-encoding comparison table across 1x-8x lengths,
the entropy traces showing collapse and recovery, the sinks ablation, the cache
memory plan for 8/24/80 GB, the compression ratio/quality curve, the ordering
ablation results, the history-compaction comparison, the assembly worked example with
drop reporting, the stuffed-vs-retrieved result, and a "what we would configure in
production and why" section.