# Lab 12: Cost Optimization for LLems — Vision

## Cost Breakdown of a Real RAG Request

```
one RAG request: 4,200 prompt tokens, 180 output tokens, 50 rerank inputs

  input tokens     4,200   x $3/M    = $0.0126   ================================  50%
  output tokens      180   x $15/M   = $0.0027   =====                            11%
  rerank inputs    10,000   x $1/M    = $0.0100   ==============================  40%
  query embedding  1,500   x $0.02/M = $0.00003  =                                0.1%
                                                  --------------------------
                                                   total $0.0253

  the intuitive lever ("shorter answers") is the SMALL line.
  the non-obvious lever (rerank k) is 40%.
  => measure before optimizing. always.
```

## Prefix Cache Ceiling

```
prompt = [stable system + few-shot  S ] [ retrieved docs  V ] [ question ]

savings = (S / (S+V)) * hit_rate * (1 - cached_price_fraction)

  S = 3000, V = 1200:
    prefix fraction = 3000/4200 = 0.71
    hit rate 0.8, cached price 10%:
    savings = 0.71 * 0.8 * 0.9 = 51% of input cost

  same hit rate, but the prompt is mostly per-request docs (S=800, V=3400):
    prefix fraction = 0.19
    savings = 0.19 * 0.8 * 0.9 = 14%

  => PREFIX CACHING HAS A CEILING SET BY THE PREFIX FRACTION.
     in doc-heavy RAG, reducing V beats any caching trick.
```

```
prompt layout:
  +---------------------------------------------------------+
  | system prompt (static)                                   |  <- cacheable
  | few-shot examples (static)                               |  <- cacheable
  +---------------------------------------------------------+
  | retrieved chunk 1 ... 8  (changes every query)            |  <- NOT cacheable
  +---------------------------------------------------------+
  | user question (changes every query)                      |  <- NOT cacheable
  +---------------------------------------------------------+

  ONE timestamp placed at the top:
    prefix hash changes EVERY call
    hit rate -> 0
    cost per request returns to baseline instantly

  lesson: volatile content goes to the tail, always
```

## Semantic Cache: A Quality Dial, Not a Free Win

```
hit rate h, quality delta on hits delta_q

  cost saving   ~ h                 (a cache lookup is ~free)
  quality cost  = h * delta_q      (those requests skip fresh generation)

  40% hit rate on paraphrased questions
    -> 40% of traffic answered from cache
    -> 40% of traffic carrying whatever the cache's delta is

  +--------------------------------------------------+
  | MEASURE delta_q ON THE EVAL SET BEFORE ENABLING   |
  | BROADLY. it is a product decision, not an         |
  | engineering fact.                                  |
  +--------------------------------------------------+

  cache key MUST include:
    model | prompt version | corpus version | tenant | authz scope | TTL

  omit tenant/authz  -> cross-user answer leak (security incident)
  omit corpus version-> stale RAG answers nobody notices
```

## Cascade Economics

```
  cheap model  $0.0005/req        frontier  $0.010/req      (20x)

  escalation p | blended cost (x cheap) | quality note
  ------------------------------------------------------------------
     0.05      |        1.95x          | usually the best trade
     0.10      |        2.90x          |
     0.20      |        4.80x          |
     0.35      |        7.65x          | ~equal quality to frontier
     0.50      |       10.50x          | why bother with a cheap model

  blended_cost = (1-p)*c_cheap + p*c_frontier

  WHY A CASCADE BEATS A STATIC ROUTER:
    static router  -> p is a CLASSIFIER's precision, guessed up front
    cascade        -> p converges to the cheap model's ACTUAL error rate
    escalation on outcome (schema invalid, low self-consistency, verifier
    disagrees) is a self-correcting signal; a confidence threshold is not.
```

## Context Reduction: The Big RAG Lever

```
  instruction text:        ~300 tokens   <- compressing this is pointless
  retrieved context:     ~4,000 tokens   <- THIS is the cost
  schema + safety:        ~200 tokens   <- never touch

  extractive compression: keep only sentences scoring above a threshold
  across the already-selected chunks

  4,000 -> 1,200 tokens   (70% cut)      with a small, measured recall delta

  granularity matters:
    drop WHOLE chunks      -> recall collapses
    filter SENTENCES       -> provenance kept, tokens cut, quality holds

  keep citations valid: citations point at chunk ids, and the chunk is still
  in the prompt even if only some of its sentences are quoted
```

## Batching Is the Biggest GPU Lever

```
cost per token = t(b)/b = max( 2P/FLOPS , (2P/b + C)/BW )

  P = 7e9,  C = 1.07 GB (2048-token cache),  FLOPS=1e15, BW=3.3e12

   b     2P/b term    C term        bound      cost/token
  -----------------------------------------------------
   1     4.24 ms      0.32 ms       memory     4.24 ms
   4     1.06 ms      0.32 ms       memory     1.38 ms
  12     0.35 ms      0.32 ms       memory     0.67 ms
  32     0.13 ms      0.32 ms       memory     0.45 ms
  64     0.07 ms      0.32 ms       memory     0.39 ms
  128    0.03 ms      0.32 ms       memory     0.35 ms
  -----------------------------------------------------
    6.3x cost reduction from b=1 to b=32

  and the REAL ceiling is memory, not compute:
    max_batch = (80 GB - 14 GB weights) / 1.07 GB = 61 sequences
  => capacity planning is a CACHE problem.
     reduce C (GQA, INT8 cache, shorter context) and the batch ceiling rises
     multiplicatively. reduce weights and it barely moves.
```

## Speculative Decoding Flow

```
  prompt        : "The capital of France is"
  draft (small) :  Paris -> . -> France -> .          4 tokens proposed

  target (large) scores ALL 4 positions in ONE forward pass
                  P(Paris)  = 0.98
                  P(.)      = 0.99   / draft 0.85  -> ratio 1.00  ACCEPT
                  P(France) = 0.72   / draft 0.60  -> ratio 1.00  ACCEPT
                  P(.)      = 0.55   / draft 0.50  -> ratio 1.00  ACCEPT
                  all 4 accepted -> 4 tokens from ONE target pass

  on rejection:
    draft: the -> . -> Paris -> .
    target P(the)=0.10 / draft 0.40 -> ratio 0.25
    U=0.30 < 0.25? no -> REJECT, resample from the TARGET's distribution
    -> 1 token, and everything after is discarded

  E[accepted] = (1 - alpha^(k+1)) / (1 - alpha)
    alpha=0.8, k=5 -> 3.69      alpha=0.6, k=5 -> 2.38

  LOSSLESS: the accepted token is verified against the TARGET's probability,
  and on rejection we resample from the TARGET. the output distribution
  is exactly the target's. no quality change, only speed.
```

## Quantization Cost Effect

```
  cost/token while memory bound ~ 1 / bytes_moved

   weights   bytes       cost/token    7B model
  ------------------------------------------------------
   fp16     2P = 14 GB      1.00x       14.0 GB
   int8      P =  7 GB      2.00x        7.0 GB
   int4    0.5P =  3.5 GB   4.00x        3.7 GB (with scales)

  SECONDARY effect that people miss:
    max_batch = (device_mem - weights) / C
      fp16: (80 - 14)/1.07 = 61 sequences
      int4: (80 -  3.7)/1.07 = 71 sequences   (+16%)

  at 2048-token context the CACHE dominates memory, so weight savings give
  little batch headroom. at 512-token context they give a lot.
  => compute this per workload. do not assume.
```

## Cumulative Optimization Sequence

```
config                                  $/req     $/month(2M)   quality delta
------------------------------------------------------------------------------------
baseline                                  0.0253     50,600         -
+ prefix cache (71% prefix, 80% hit)      0.0237     47,400         ~0
+ rerank k 50 -> 25                       0.0187     37,400         ~0
+ context reduction 4200 -> 1200          0.0079     15,800         -0.4 pt
+ cascade (p=0.2, 20x price gap)          0.0053     10,600         -0.3 pt
+ semantic cache (h=0.35)                  0.0035      7,000         -1.1 pt
+ int8 weights                             0.0033      6,600         -0.3 pt
------------------------------------------------------------------------------------
                                                                             7.7x cheaper

  top three levers:  context reduction, cascade, rerank reduction
  NOT "use a smaller model" -- that is a lever too, but it caps quality outright

  every row must be validated against the eval suite. a 7.7x cost cut with a
  2-point quality drop is a trade someone has to accept explicitly.
```

## What to Optimize First

```
  measured cost share?          optimize this
  ------------------------------------------------------------------
  input tokens 80%+             retrieval-side context reduction
  output tokens dominant        length tiers + concise prompting
  rerank calls high             lower k, smaller reranker, cache
  embedding calls high          dedupe + embed cache + fewer corpora
  GPU seconds dominant          batching, then precision
  repetitive traffic            semantic cache
  mixed difficulty              cascade routing

  ORDER (lever size):
    1. remove waste (dedupe, unused calls)
    2. prompt layout for prefix caching      FREE
    3. batching + precision                   3-10x on GPU cost
    4. routing / cascade                      2-5x blended
    5. semantic cache                         large on repetitive traffic
    6. retrieval-side context reduction       10x on RAG input tokens
    7. speculative decoding                   1.5-3x, lossless
    8. output length control                  needs quality measurement
```

## Utilization and Backpressure

```
  service rate mu, arrival lambda, rho = lambda/mu

  rho    mean wait W          consequence
  ------------------------------------------------------
  0.5    2/mu                 comfortable
  0.7    3.3/mu               fine
  0.9    10/mu                tail latency explodes
  1.0+   UNSTABLE             queue grows without bound

  => target rho <= 0.6
  => prefer 429 backpressure to accepting work you cannot serve
  => load shedding is a feature, not an admission of defeat
```

## Self-Check

- [ ] Cost breakdown measured before any optimization.
- [ ] Volatile content at the tail of the prompt.
- [ ] Semantic cache keyed by tenant, authz scope, corpus version.
- [ ] Cascade escalates on outcome, not on predicted confidence.
- [ ] Context compressed sentence-wise, keeping chunk provenance.
- [ ] Batch size capped by cache memory, not free memory.
- [ ] Quality gate applied to every optimization.