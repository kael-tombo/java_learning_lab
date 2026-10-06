# Lab 13: Context Window Management — Vision

## Positional Encoding Families

```
SINUSOIDAL
  PE(pos, 2i)     = sin(pos / 10000^(2i/d))
  PE(pos, 2i + 1) = cos(pos / 10000^(2i/d))

  +-- no learned parameters
  +-- PE(pos+k) = R_k PE(pos)  -> relative by construction
  - - extrapolation: poor, model never saw those frequencies

LEARNED ABSOLUTE
  table[pos] in R^d
  +-- simple
  - - NO extrapolation at all (no row for pos > trained_max)
  - - table grows with context

ALiBi
  score(i,j) = q.k/sqrt(d) - m_h * (i - j)
  m_h = 2^(-8h/H)   geometric across heads

  +-- no parameters, no added compute
  +-- only RELATIVE distance matters -> extrapolates well
  +-- soft multi-scale locality prior: sum_h exp(-m_h * dist)
  - - fixed bias, not learned

RoPE
  theta_{i,j} = pos * base^(-2j/d)
  q' = R(theta) q,   k' = R(theta) k
  -> score depends only on (i - j)

  +-- relative in the score, no table
  +-- high quality at trained length, good to ~2-4x with scaling
  - - base controls the range: 10k standard, 100k/1M for long context
```

## Extrapolation: Interpolation vs Not

```
perplexity relative to the trained-window baseline

  position      unscaled    interpolated(s=4)    NTK-scaled
  -------------------------------------------------------
  L  (4k)          1.00          1.02               1.01
  2L (8k)          2.10          1.15               1.06
  4L (16k)         8.40          1.35               1.12
  8L (32k)        31.0           4.20               2.40
  -------------------------------------------------------

  failure is a CLIFF, not a slope
  diagnostic: normalized attention entropy H / log K
      -> 0.3  = peaked, model cannot discriminate   (bad)
      -> 0.99 = flat, no selectivity                 (bad)
      -> 0.7  = healthy
```

## Sliding Window + Attention Sinks

```
without sinks, window W, sequence N:

  query i sees [max(0, i-W+1) .. i]
  the first W tokens of every window have < W predecessors
  total available attention mass is CONSTANT across the sequence
  -> no place to "dump" unavoidable attention
  -> softmax entropy collapses
  -> accuracy falls off sharply

with StreamingLLM sinks (first 4 positions always visible):

  +---------------------------------------------+
  | s0 s1 s2 s3 |<------ window W ------> | q_i  |
  +---------------------------------------------+
  sink tokens receive LARGE attention weights
  precisely because they absorb the pressure

  cost: full O(N^2)  vs  windowed O(N*W)
    N =  8W: 4.3x fewer score computations
    N = 32W: 16x fewer
```

## KV Cache Memory Levers Compound

```
32 layers, 32 query heads, d_head 128, S = 32768, batch 8, fp16 baseline

  MHA (32 kv heads)                  137 GB  =======================================
  + GQA (8 kv heads)          4.0x    34.3 GB  ============================
  + INT8 cache                 8.0x    17.2 GB  =======================
  + sliding W = 4096          64.0x     2.1 GB  ===
  + batch 2                 128.0x     0.5 GB  =

  at 32k context the fp16 cache is ~5x the weight memory
  => LONG CONTEXT IS A MEMORY PROBLEM BEFORE IT IS A COMPUTE PROBLEM

  levers compose multiplicatively: GQA x precision x window x batch
  every one of them is a quality trade except batch (which is a latency trade)
```

## Prefill Cost Crossover

```
per layer:
  attention   ~ 4 * S^2 * d
  FFN         ~ 16 * S * d^2

  attention : FFN  =  S / (4d)

    d = 4096  ->  crossover at S = 16384
    d = 8192  ->  crossover at S = 32768

  below the crossover, prefill is linear -> chunking works fine
  above it, prefill is quadratic -> long requests need their own lane

  measured TTFT (70B class):
     1k   ~ 0.3 s
     4k   ~ 0.9 s
    16k   ~ 5 s
    64k   ~ 70 s      <-- the quadratic term and memory pressure both bite
```

## Information Density: The Case for Retrieval

```
  50 documents stuffed, 1,000 tokens each:

    | d1 | d2 | d3 | ... | d50 |          S = 50,000 tokens
      ^                              ^
      the relevant one                the question

    signal_density = relevant_tokens / total_tokens
                    = 1,000 / 50,000 = 2%

  retrieval of 2 chunks:

    | c1 | c2 | question |                    S = 800 tokens
    signal_density ~ 100%

  TWO EFFECTS COMPOUND:
    62x fewer tokens        -> cost, TTFT, cache memory
    50x higher density      -> accuracy ("lost in the middle")

  => retrieval beats stuffing on BOTH axes simultaneously
     long windows are headroom for comparison tasks, not a substitute for retrieval
```

## Context Ordering

```
  layout A: [best evidence FIRST]              accuracy 0.71
  layout B: [worst ... best LAST]              accuracy 0.84   <-- best
  layout C: [evidence sorted by score, best in middle]   0.68
  layout D: [random order]                     accuracy 0.73

  because of primacy + recency effects ("lost in the middle")
  the END of context is the most valuable real estate you have

  recommended layout:
  +---------------------------------------------------------+
  | system + policy                              (trusted)  |
  | brief task restatement                        (primacy)  |
  +---------------------------------------------------------+
  | evidence, ascending score:  chunk 7 ... chunk 3           |
  |                                  chunk 2 ... chunk 1      |  (best last)
  +---------------------------------------------------------+
  | operative instruction restated                (recency)  |
  | question                                             ---->|
  +---------------------------------------------------------+

  also: keep the schema adjacent to the instruction that mentions it
```

## Map-Reduce vs Stuffing

```
STUFFING  (D docs x t tokens)
  stage 1: one pass over D*t tokens, attention O((D*t)^2 d)
  D=50, t=1000:  S=50,000  ->  S^2 = 2.5e9

MAP-REDUCE
  stage 1 (map):      each doc independently -> summary of s = t/10
                     D * t input tokens, but S^2 per call = (t)^2  (50 small passes)
  stage 2 (reduce):   D*s = 5,000 tokens  ->  S^2 = 2.5e7     <-- 100x smaller

  total input tokens comparable (D*1.1t vs D*t)
  but the QUADRATIC term, which dominates at length, shrinks by 100x

  + per-document grounding -> better citations
  + failure isolation -> one bad doc does not poison the whole context
  - two model passes -> more latency, more tokens out
```

## History Compaction: Three Strategies

```
multi-turn session, window exceeded

TRUNCATION
  keep: [system][system][user][assistant]...
  drop: everything old
  cheap, loses facts, breaks referents ("what about the second one?")

SUMMARY
  keep: [system][summary of old turns][last 3 verbatim]
  loses: detail inside old turns
  ok for: long casual chats

STRUCTURED STATE + WINDOW          <-- recommended
  keep: [system][FACTS: ...][DECISIONS: ...][OPEN ITEMS: ...][last 3 verbatim]
  extracts: ids, dates, amounts, commitments
  recovers: early facts a truncation would lose
  ok for: bookings, support threads, agent workflows

  state goes in a SYSTEM message (trusted channel)
  extraction is pattern-based, not model-based -> cannot hallucinate
  NEVER compact the system message itself
```

## Budget Assembly Priority

```
  budget = 2000 tokens

  PRIORITY          content            tokens   fate
  ------------------------------------------------------------------
  POLICY            system message      120     ALWAYS KEPT
  INSTRUCTION       task rules           180     KEPT
  QUESTION          the query             40     KEPT
  TOP_EVIDENCE      chunk 1 (best)       410     KEPT
                    chunk 2              390     KEPT
                    chunk 3              380     KEPT
                    chunk 4              390     DROPPED
  HISTORY           compacted state      210     KEPT
  FILLER            nice-to-have         300     DROPPED

  invariants asserted by test:
    schema present?          YES
    system message present?  YES
    question present?        YES
    top-scoring evidence present?  YES
```

## Choosing a Strategy

```
  question needs 1 fact from 1M tokens?   retrieval, 2k context
  comparison across 20 docs?               map-reduce
  session exceeds window?                  structured state + window
  model trained to 4k, need 128k?         GQA + RoPE scaling + fine-tune + window
  memory-bound at 32k?                     INT8 cache + paged attention
  quality drops with stuffing?             ordering + compression, NOT more tokens
  latency matters most?                    retrieval, not long windows
```

## Self-Check

- [ ] Position encoding family chosen and justified for the length.
- [ ] GQA plus cache precision plus window chosen together (they compound).
- [ ] Attention sinks present if a sliding window is used.
- [ ] Best evidence placed last, nearest the question.
- [ ] System message and schema protected from compaction.
- [ ] Retrieval preferred over stuffing for large corpora.