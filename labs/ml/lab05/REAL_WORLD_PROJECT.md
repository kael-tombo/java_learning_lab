# REAL_WORLD_PROJECT — Similar-Item Recommendations for a Retail Catalogue

**Track:** ml  |  **Lab:** lab05  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Scenario

A grocery retailer with 400k SKUs needs 'customers who bought this also bought' inside 120 ms for a page render, for 12M sessions a day. The catalogue changes hourly and cold items have no history.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Catalogue | ~400k active SKUs, ~1.8M orders/day, ~55M order lines/day |
| Traffic | 12M sessions/day, peak 4,500 rec slots/s across all placements |
| Latency budget | p99 < 120 ms per slot, including retrieval and ranking |
| Freshness | similarity lists refreshed hourly; new SKUs served within 1 hour |
| Business metric | incremental units per session, measured by a holdout |

## 3. Target Architecture

```text
 order stream --> line-item store (Kafka) --> hourly similarity job
                                                        |
                                          item-item ANN index (in-memory + warm cache)
                                                        |
  page render --> rec service --> slot budget / dedupe / exclusion lists --> page
        |                                                     |
        |                                            impression + order events
        |                                                     |
        +------------------> holdout measurement <-----------+
                                    |
                          hourly index rebuild + drift checks
```

## 4. Component Responsibilities

### 4.1 Similarity computation

- Co-purchase counts in fixed time windows with a decay factor
- Normalised item-item similarity (cosine-style) with a minimum-support filter
- Top-N neighbours stored per item; the full matrix is never materialised
- Warm-start from the previous index so partial rebuilds stay available

### 4.2 Index and serving

- In-memory ANN index over item embeddings plus an exact-lookup fallback for hot items
- L1 cache of the top 10k most-requested items' neighbour lists
- Slot budgets, seen-item exclusion and category diversity applied per placement
- p99 under 120 ms enforced by a timeout with a popularity fallback

### 4.3 Freshness and cold start

- Incremental hourly updates rather than full nightly rebuilds
- Brand-new SKUs served from attribute-only similarity until co-purchase data accrues
- Zero-result detection routed to category popularity, logged as a quality signal
- Index version pinned in every response so a stale slot is identifiable

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship a co-purchase baseline with popularity fallback and full impression logging |
| Week 2 | Hourly similarity job with warm start; verify a rebuild never serves an empty index |
| Week 3 | ANN index plus cache; measure p99 and the accuracy/cost trade-off |
| Week 4 | Cold-start path for new SKUs; holdout measurement framework running |
| Week 5 | Diversity and slot-budget rules tuned against the holdout; runbook published |

## 6. Runbook (copy-paste)

```bash
# Index health and freshness
curl -s localhost:8080/admin/index | jq '{version,builtAt,items,zeroResultRate}'

# Latency by placement
curl -s 'localhost:8080/admin/latency?window=15m' | jq '.p50,.p95,.p99'

# Fall back to category popularity for every slot
curl -XPOST localhost:8080/admin/mode -d '{"mode":"POPULARITY_ONLY"}'

# Force a partial index rebuild (top 10k hot items only)
curl -XPOST localhost:8080/admin/rebuild -d '{"scope":"hot"}'

# Verify a known SKU returns neighbours (regression check)
curl -s 'localhost:8080/similar?sku=SKU-0048212' | jq '.neighbours|length'
```

## 7. Observability and SLOs

- SLO: p99 slot latency < 120 ms; index freshness < 70 min; availability 99.95%.
- Business: incremental units per session against a 5% holdout, reported with confidence intervals.
- Quality: click-through on recommendations, and zero-result rate by category.
- Freshness: share of SKUs served from cold-start similarity, and its CTR delta.
- Cost: memory per index version and rebuild duration, tracked against the hourly budget.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Index rebuild fails and the hot set goes stale | OOM during the full similarity job | Keep the previous version live, rebuild the hot subset, page; never delete the last good index |
| p99 slot latency breaches 120 ms | cache miss storm after a catalogue drop | Serve popularity fallback for overflow slots and log the substitution |
| Zero-result rate spikes on new categories | attribute-only similarity is too coarse | Route to category popularity, alert the merchandising owner |
| Recommendation CTR drops 20% | seasonal demand shift not in the index | Trigger an out-of-band rebuild, verify the holdout before concluding the model failed |
| Two slots on a page return the same SKU | dedupe logic lost in a config change | Slot-level dedupe is enforced in code and covered by a test, not configuration |

## 9. Prevention Backlog

- Incremental similarity updates per partition instead of full hourly rebuilds.
- Embedding-based co-visitation so long-tail items get neighbours before co-purchase data exists.
- Holdout-based incremental evaluation wired into the rebuild job's exit criteria.
- Documented index rollback to the previous version, timed drill each quarter.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **scikit-learn — Linear Models user guide**: https://scikit-learn.org/stable/modules/linear_model.html
  Canonical OLS/ridge/lasso derivation and the least-squares objective; the reference for what a closed-form solution actually guarantees.
- **NumPy — linalg module reference**: https://numpy.org/doc/stable/reference/routines.linalg.html
  `linalg.solve`, `lstsq`, `pinv`, SVD — how practitioners avoid forming XᵀX explicitly and what conditioning means in practice.

> The deliverable is a 120 ms slot with a fallback, a versioned index and a holdout measurement — a recommender nobody can hold to a number is just a random assortment.
