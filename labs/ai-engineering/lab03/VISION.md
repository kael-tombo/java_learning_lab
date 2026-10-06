# Lab 03: RAG System Architecture — Vision

## End-to-End Pipeline

```
  OFFLINE (batch)                                ONLINE (per query)
  ---------------                                -------------------
  [PDF/HTML/Wiki]                                user question
       |                                              |
   parse & structure                                  v
       |                                     query rewrite
   chunk (300-800 tok, overlap)                     |
       |                                       embed (SAME model+version)
   attach metadata (doc, path, page)                 |
       |                                     +------v------+
   contextual prefix                                | namespace |
   "[Doc: X | Sec: Y]"                              | (tenant,  |
       |                                            |  corpusV, |
   dedupe near-identical                            |  embedV)  |
       |                                          +---+---+---+
   embed chunks                                       |       |
       |                                       dense ANN | BM25
   upsert index                                 pre-filter  pre-filter
       |                                       +-----+------+
   eval set from gold QA                           |          |
       |                                        RRF fusion  |
   freshness metric                               +-----+-----+
                                                       v
                                                  rerank 50->5
                                                       |
                                              budget + pack (best last)
                                                       |
                                              prompt + INSUFFICIENT_CONTEXT
                                                       |
                                              generate -> cite -> verify
                                                       |
                              answer | reject | abstain
```

## Chunking Choices Visualized

```
  Original section:
    "Refund Policy v4. Refunds are available within 30 days of purchase
     for enterprise accounts created after 2023. Contact support."

  FIXED 400 chars:
    |Refund Policy v4. Refunds are available within 30| days of pur...
     -> the chunk has a subject but no audience; "who gets 30 days?"

  SENTENCE-AWARE:
    |Refund Policy v4. Refunds are available within 30 days of purchase for|
    |enterprise accounts created after 2023. Contact support.            |
     -> better, still over budget -> split into 2

  HEADING-AWARE + PREFIX (what you should embed):
    [Document: Acme Policy | Section: Refund Policy v4 | Updated: 2026-10-01]
    |Refunds are available within 30 days of purchase for enterprise      |
    |accounts created after 2023.                                          |
     -> "how long do enterprise accounts have to return something?"
        now retrieves this chunk. the PREFIX is what makes it work.

  citations still point at the display text, not the prefix.
```

## Hybrid Search: Why Both

```
  query: "fix ERR-4021 on the gateway"

  DENSE:  embeddings are a smooth function of MEANING.
          "ERR-4021" is near-unique, so its vector lands in an
          arbitrary direction with few close neighbours.
          -> the right chunk may not be in the top 1000

  BM25:   exact token match on "ERR-4021" -> hits immediately

  RRF(d) = 1/(60 + rank_dense(d)) + 1/(60 + rank_bm25(d))
          rank_bm25 = 0    -> 1/60  = 0.0167
          rank_dense = 90  -> 1/150 = 0.0067
          total = 0.0233, which beats a doc ranked 20th by dense alone
          (1/80 = 0.0125).

  no score calibration needed: cosine in [-1,1], BM25 in [0,20],
  and ranks are already commensurable.
```

## The Rerank Ceiling

```
  ANN top-10 recall = 0.93

  END-TO-END ANSWER QUALITY <= 0.93
  the gold chunk was never retrieved. no prompt fixes it.

  over-fetch to top-50: p_50 = 0.99
  rerank 50 -> 5 with a strong cross-encoder
  -> end-to-end ceiling 0.99

  cost: rerank is ~90 ms for 50 pairs, ~9 ms for 5.
  the ENTIRE latency budget of a RAG system is the rerank stage.
```

## Recall vs Faithfulness

```
  recall@5
     ^
     |          ___________
     |      ___/
     |   __/
     |  /
     +-------------------> k (chunks)

  faithfulness
     ^
     |    ___
     |   /   \____________        <- peaks, then declines
     |  /                    \___
     +-------------------> k

  why it declines: more context dilutes attention and the model
  attributes claims to the WRONG chunk.

  => optimizing recall alone produces a system that retrieves more
     and answers worse. optimize the END-TO-END metric with
     faithfulness as a guardrail.
```

## Context Assembly and Ordering

```
  budget = 8192 - 200(system) - 40(query) - 400(maxNew) - 120(schema) = 7432

  packed (emitted in this order):
    [1] chunk 7   score 0.61
    [2] chunk 5   score 0.74
    [3] chunk 3   score 0.83
    [4] chunk 9   score 0.88   <- HIGHEST score, LAST, nearest the question
    dropped: chunk 1 (does not fit), chunk 2 (does not fit)

  recency matters: models weight the END of context most strongly.
  ascending emission order puts the best evidence in the strongest position.
```

## Failure Triage

```
  answer wrong?
     |
     +-- is the gold chunk in top-50?      NO -> chunking / embedding / index
     |                                            check the model+version match FIRST
     YES
     |
     +-- did the rerank demote it?          YES -> rerank k / reranker quality
     |
     NO
     |
     +-- finish_reason == length?           YES -> budget / chunk size
     |
     NO
     |
     +-- citation id out of range?          YES -> checker/prompt ordering bug
     |
     NO
     |
     +-- claim not in the context?          YES -> grounding prompt too weak;
     |                                            add CoV / self-consistency
     |
     +-- index_age_hours stale?             YES -> freshness problem, not a
     |                                            quality problem
```

## Cost Breakdown of One Query

```
  embed query          1 x 1500 tok   @ $0.02/M  =  $0.00003
  dense search                           ~2 ms    =  (compute, negligible)
  lexical search                         ~3 ms    =  (compute, negligible)
  rerank 50 pairs                        ~90 ms   =  $0.0040
  generate 1600 ctx + 200 out  @ $3/$15/M       =  $0.0078
  -------------------------------------------------------------
  total                                          ~ $0.0118

  the GENERATION is 66% of the cost, and 1,600 of the 1,800
  tokens are retrieved context.

  => chunk selection is a COST lever, not only a quality lever.
     k=8 -> 4: saves $0.0120 (a third of the bill)
     chunk 400 -> 250: saves $0.0090
```

## Abstention Frontier

```
  coverage
    ^
 1.0|  oooooooooooooooooooooooooo
    |     accuracy 0.78
    |             oooooooooooo
    |                accuracy 0.88
    |                    oooooo
    |                       ooo
 0.6|                          oo       <- chosen operating point
    |                            o       accuracy 0.95
    +------------------------------------> retrieval-score threshold

  E[correct] = coverage * accuracy
    1.00 * 0.78 = 0.78
    0.60 * 0.95 = 0.57
    0.80 * 0.88 = 0.70

  the abstaining system is worth MORE despite "failing" 40% of queries.
  product teams prefer coverage until they see this arithmetic.
  pick the operating point explicitly and write down the trade.
```

## Self-Check

- [ ] Contextual prefix on embedded text; display text unchanged.
- [ ] Hybrid search with RRF by default.
- [ ] Over-fetch before rerank; rerank `k` at the quality knee.
- [ ] Best chunk emitted last.
- [ ] Schema and question never truncated.
- [ ] Citation ids validated against the supplied set.
- [ ] Abstention threshold chosen from `E[correct]`.
- [ ] recall@k measured before any prompt work.
- [ ] Namespace includes corpus and embedding versions.
- [ ] Ingest idempotent; freshness alerted.