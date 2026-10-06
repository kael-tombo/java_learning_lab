# Lab 02: Vector Database Integration — Vision

## The Search Stack

```
  query text
      |
      v
  [embed]  same model + version as the indexed docs   <-- silent-failure point
      |
      v
  [namespace]  (tenant, corpusVersion, embedVersion)   <-- required, not optional
      |
      v
  +---v-----------------------------+
  | ANN SEARCH (fast, recall ~0.95)  |  flat | IVF | HNSW | IVF-PQ
  | pre-filter on tenant/ACL FIRST   |
  +---+-----------------------------+
      |  top 50
      v
  [RERANK]  cross-encoder, scores (query, chunk) jointly     90 ms
      |  top 5
      v
  [dedupe / assemble context]  -> generator
```

## Distance Identities

```
|a - b|^2 = |a|^2 + |b|^2 - 2 a.b

  unit vectors:  |a - b|^2 = 2 - 2cos(a,b)
      -> L2 ranking == cosine ranking
      -> a DB storing L2 returns correct cosine ORDER for normalized data

  UNNORMALIZED:  a = 10 * u ,  b = 0.1 * u   (same direction u)
      cos(a,b) = 1.00        -> "identical direction, very relevant"
      |a-b|^2  = 98.01      -> "far apart, irrelevant"

      => metric choice is only safe if normalization is guaranteed AT WRITE TIME.
         verify it; do not assume it.
```

## Flat vs ANN — Cost Reality

```
  brute force is limited by READING every vector, not by arithmetic.

  1M vectors x 768 dims x 4 bytes = 3.07 GB read per query
     at 50 GB/s            -> 61 ms      memory bound
     at 200 GB/s (4ch DDR5)-> 15 ms
     int8 (0.77 GB)        -> 15 ms / 4  -> 3.8 ms
     fp16 (1.5 GB)         -> 30 ms / 2  -> 7.7 ms

  HNSW reads ~5,000 distances instead of 1,000,000   -> 200x less work

  but at 100k vectors, flat is 6 ms and EXACT.
     and at 100k, exactness may be worth more than speed.

  => index choice is a SCALE decision, not a preference.
```

## IVF Recall vs nprobe

```
  recall(nprobe) ~ 1 - exp(-nprobe / rho),  rho ~ 5 for typical text embeddings

  nprobe      recall@10
  1            0.18      <- unusable
  2            0.33
  4            0.55
  8            0.80
  16           0.96
  32           0.998

  the curve is STEEP. nprobe=1 is not a speed optimization, it is a bug.
  latency is exactly linear in nprobe.

  k-means++ seeding matters: random init gives unbalanced cells,
  and one hot cell with 10% of the corpus destroys the latency win.
```

## HNSW Anatomy

```
  layer 2   [  A ---- F ---- K ]            sparse: long-range navigation
                                     ~M nodes have a node here
            |
  layer 1   [ A-B-C  F-G-H  K-L-M-N ]     medium
            |
  layer 0   [ A-B-C-D-E F-G-H-I J-K-L-M-N-O ]   dense: every node here
            full graph, M neighbors each

  search:
    start at a single entry point in layer 2
    greedy walk to the best node in layer 2
    drop to layer 1, repeat
    drop to layer 0, search with efSearch candidates (bounded max-heap)
    return top-k

  layer assignment:  level = floor(-ln(U) * mL)
    fraction above layer 0 = 1/(M-1) = 6.7% for M=16
    -> the top layers stay small, which is what makes descent fast

  cost: hops ~ log_M(n);  ~ efSearch * M * log_M(n) distance computations
    n=1e6, M=16, ef=64  ->  hops ~5  ->  ~5,120 distance computations
    vs 1,000,000 for flat
```

## Memory: Vectors Dominate, Not the Graph

```
  bytes/vector = dim*4  +  M * layers * 4

  dim=768, M=16, n=1e6 (layers ~5):
     vector data     3072 B  ===============================
     graph links      320 B  ==
     total           3392 B     graph is 10% overhead

  so the graph is CHEAP. quantizing the vectors is the 4x lever:
     int8 vectors  ->  768 B + 320 B = 1088 B   (3.1x total reduction)
     PQ-64         ->   48 B + 320 B =  368 B   (9.2x)

  and the decomposition matters for the design:
  you can quantize vectors WITHOUT touching the graph.
```

## Pre vs Post Filtering

```
  post-filter, selectivity s=0.01, k=10:
     search returns 10 hits
     1% survive  ->  expected 0.1 results
     you asked for 10, you got 0.

  post-filter with over-fetch (k/s = 1000):
     scans the SAME vectors as pre-filter (no saving)
     and still recalls worse than pre-filter
     -> the worst of both worlds

  pre-filter, s=0.01:
     scans 1% of the corpus
     returns 10 real results

  HNSW + selective filter:
     each node has ~M random long edges
     P(edge survives) = s^2
     s=0.10  ->  0.01    graph nearly disconnected
     s=0.30  ->  0.09    degrading
     s=0.50  ->  0.25    usable

  => pre-filter below ~10% selectivity, post-filter above ~50%, measure between.
     the hard rule: tenant isolation MUST be a pre-filter inside the query.
```

## Two-Stage Recall: The Ceiling Effect

```
  ANN recall@10 = 0.95

  end-to-end recall CANNOT exceed 0.95, no matter how good the reranker is.
  the gold chunk was simply never retrieved.

  over-fetch fixes it:
     ANN top-50  with gold present 99% of the time
     rerank to top-5 with a near-perfect cross-encoder
     -> final recall can be 0.99

  pipeline:  ANN(0.95) -> +rerank over top-50 -> 0.99

  cost comparison, 10M vectors, 768 dims:
  ---------------------------------------------------------------------
  index            memory    recall@10   p50      notes
  flat             30.7 GB   1.00        61 ms    exact, too slow
  HNSW M=16        33.9 GB   0.97        1.2 ms
  HNSW + int8      10.9 GB   0.94        0.9 ms
  IVF-PQ 64x6bit    1.6 GB   0.85        0.6 ms
  IVF-PQ + rerank   1.6 GB   0.95        55 ms   <-- practical choice

  the memory-efficient index plus a reranker beats the exact index on BOTH
  memory (19x) and latency (1.1x) while giving up 5 points.
  the PIPELINE is the design, not the index.
```

## Index Selection Matrix

```
  vectors    exactness needed   memory limit   filters        -> INDEX
  ---------------------------------------------------------------------
  < 1M       no                 generous       rare           flat
  < 1M       no                 tight          selective      flat int8
  1M-50M     no                 generous       rare           HNSW
  1M-50M     no                 tight          rare           HNSW + int8
  1M-50M     no                 tight          selective      IVF + pre-filter
  > 50M      no                 very tight     rare           IVF-PQ + rerank
  any        YES                any            any            flat (no ANN)
  any        no                 any            very selective pre-filter + flat
```

## Failure Modes

```
  symptom                      | cause                              | fix
  -----------------------------+------------------------------------+---------------
  all results irrelevant        | embed model version mismatch       | namespace pin + test
  fewer than k results          | post-filter at low selectivity     | pre-filter
  recall collapses with filters | HNSW graph fragmented by filtering | pre-filter
  latency spikes at low traffic | cold index / cold cache            | warmup
  storage grows forever         | no compaction after tombstones     | compact in maintenance
  duplicates at the top         | near-duplicate chunks ingested     | dedupe at ingest
  p99 explodes after adding RRF | rerank k too large                 | lower k, batch
  wrong tenant's content        | tenant filter optional in the API | make it required
  recall fine, answers wrong    | retrieval is not the bottleneck    | check the generator
```

## Self-Check

- [ ] Vectors normalized at write time; metric verified against training.
- [ ] Namespace includes tenant, corpus version, and embedding model version.
- [ ] Tenant filter is a required pre-filter argument.
- [ ] `nprobe`/`efSearch` tuned from a recall/latency sweep, not guessed.
- [ ] Rerank `k` chosen at the quality knee.
- [ ] Tombstones compacted; index rebuildable from the chunk store.
- [ ] Duplicate suppression at ingest.
- [ ] Recall@k tracked per index configuration as a health metric.