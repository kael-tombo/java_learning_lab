# Lab 13: Context Window Management — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Sinusoidal Positional Encoding (E)

Implement `double[][] sinusoidal(int maxLen, int d)` and verify:
- rows are unique,
- the relative-offset rotation identity `PE(pos+k) = R_k * PE(pos)` holds,
- values stay in `[-1, 1]`.

---

## Exercise 2: RoPE Application and Relative Property (M)

Implement `applyRoPE(double[] q, int pos, double base)` and verify that
`dot(applyRoPE(q, i), applyRoPE(k, j))` depends only on `i - j`.

**Verify**: the dot product for `(10, 12)` equals that for `(100, 102)`.

---

## Exercise 3: ALiBi Slopes and Bias (M)

Generate geometric head slopes (`m_h = 1 / 2^(8h/n)` family) and add the bias to
attention scores. Show that extrapolating to twice the trained length degrades less
than sinusoidal or learned positions.

---

## Exercise 4: Position Interpolation vs Extrapolation (M)

Implement linear scaling of positions by `s = 4` and compare perplexity against
unscaled positions on a synthetic long-range task.

**Expected**: scaled positions far better beyond the trained window; worse inside it.

---

## Exercise 5: Attention Entropy Collapse Demonstration (H)

Measure attention entropy as positions exceed the trained window, for sinusoidal,
ALiBi, RoPE, and interpolated RoPE.

**Expected**: entropy drops sharply for unscaled sinusoidal/RoPE; ALiBi degrades
gradually; interpolation holds it.

---

## Exercise 6: Sliding Window Attention (M)

Implement windowed attention with window `W` and verify:
- each query attends exactly `min(i+1, W)` keys,
- cost scales `O(N*W)` — measure operation counts for `W = 512` at `N = 8k`.

---

## Exercise 7: Attention Sinks (H)

Implement StreamingLLM-style handling: keep the first 4 tokens permanently visible.
Compare attention entropy and task accuracy against pure sliding window.

**Expected**: sinks prevent the collapse; a pure sliding window degrades sharply.

---

## Exercise 8: KV Cache Memory Calculator (E)

Compute cache bytes for a grid of (layers, kv heads, head dim, seq len, precision)
and find the configuration that fits 8/24/80 GB.

**Verify**: GQA at 8 KV heads is 4x smaller than MHA at 32.

---

## Exercise 9: Ring Buffer KV Cache (M)

Implement a ring buffer of size `W` with modular indexing. Verify cached positions
match a full cache exactly when `W` exceeds the sequence length.

---

## Exercise 10: KV Cache INT8 Quantization (H)

Quantize cached K and V per head with per-head scales; measure reconstruction error
and the memory saving.

---

## Exercise 11: Sentence-Level Context Compression (M)

Score sentences in retrieved chunks against the query, drop below-threshold
sentences, keep chunk provenance. Measure tokens saved and answer quality.

---

## Exercise 12: Hierarchical Summarization (M)

Build summary-of-summaries: per-chunk extractive summaries, then a document-level
summary over those. Compare against reading full text on a multi-document QA task.

---

## Exercise 13: Latent Compression (H)

Train a tiny autoencoder that compresses `k` token embeddings into 1 latent vector;
fine-tune the reader to use it. Measure compression ratio and quality.

**Expected**: large ratio, meaningful quality loss, full transparency required.

---

## Exercise 14: Context Ordering Ablation (M)

Run a QA task with evidence placed first, last, sorted ascending, and sorted
descending. Measure accuracy and the "lost in the middle" effect.

**Expected**: ascending (best last) wins; middle placement is worst.

---

## Exercise 15: History Compaction with Structured State (M)

Implement `State + RecentWindow`: extract typed facts (decisions, open items, ids)
from old turns and keep the last k verbatim. Measure recall of early facts.

---

## Exercise 16: Map-Reduce Over Documents (M)

Implement: summarize each document independently, then synthesize a final answer with
citations. Compare against stuffing all documents into one prompt.

**Expected**: better accuracy, similar or higher cost, more robust to length.

---

## Exercise 17: Per-Document Question Fan-Out (H)

Ask the specific question of each of 20 documents independently, then combine answers
with a vote/merge step. Measure accuracy and cost versus map-reduce.

---

## Exercise 18: Prefill Cost Model vs Measurement (M)

Instrument a synthetic model; measure prefill latency at 1k/4k/16k/64k and compare
with the `O(N^2)` attention model.

**Expected**: attention term dominates past ~4k; measured latency matches within 20%.

---

## Exercise 19: Long Context vs Retrieval (H)

Compare: (a) 50k tokens of stuffed context, (b) 2k tokens of retrieved context.
Measure accuracy and cost.

**Expected**: retrieval often wins on both — the headline result of this lab.

---

## Exercise 20: Budget-Aware Assembler (H)

Implement an assembler that fills a token budget by priority (system, question,
top evidence, history summary, filler) and drops the lowest priority first. Verify
schema and system message are never dropped.

---

## Stretch A: YaRN-Style Per-Dimension Scaling (H)

Apply NTK-aware scaling per frequency band plus attention temperature compensation.
Measure perplexity at 4x context versus linear interpolation.

---

## Stretch B: Cross-Request Prefix Sharing (H)

Share KV blocks across requests with identical prefixes using copy-on-write.
Measure memory saved and hit rate.

---

## Stretch C: Context Quality Degradation Curve (M)

Plot accuracy against context length for stuffed context, retrieval, and map-reduce.
Identify the length where stuffing becomes worse than retrieval.

---

## Stretch D: Adaptive Window Size (M)

Choose the window size per request from query type and evidence count. Compare
against a fixed window on cost and accuracy.

---

## Stretch E: Cache-Eviction Policies (H)

Implement LRU, LFU, and recency-based eviction for a bounded cache under a workload
with skewed prefix reuse. Report hit rate per policy.

---

## Stretch F: Position Interpolation Fine-Tuning (H)

Fine-tune with interpolated positions on long sequences; measure the recovery in
perplexity relative to unscaled fine-tuning at equal steps.