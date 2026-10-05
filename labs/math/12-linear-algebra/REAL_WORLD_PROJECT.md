# REAL_WORLD_PROJECT — Linear Algebra in Production: Embedding Search Service
> Production use-case: nearest-neighbor retrieval over document embeddings.

## 1. Scenario
- Service: semantic search compares query embedding to 1M doc embeddings.
- Constraint: p99 < 100ms; results must be explainable (top cosine scores shown).
- Choice: brute-force dot products on normalized vectors (cosine), L2 distance on normalized = monotonic.
- Data: `Embedding{docId, vector[768]}`; query vector per request.

## 2. Architecture
```
query → embed → normalize → matrix-vector scores → top-k (argpartition) → explain scores
```
- Vectors stored as float[] blocks; SIMD-friendly layout.
- Score transparency: return cosine score + distance for every hit.

## 3. War-Story (plausible, representative)
- Incident: search quality "randomly" dropped after a model retrain.
- Symptom: top results were on-topic in one index, garbage in another.
- Root cause: new embeddings weren't normalized; dot product favored longer (stale) vectors.
- Fix: normalize at write time; add a length-histogram check in the pipeline.
- Lesson: the same vector means different things under different metrics — pin the metric.

## 4. Metrics (before → after, 4 weeks)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| p99 query latency | 180ms | 85ms | −53% |
| top-5 precision (labeled set) | 0.61 | 0.83 | +22pp |
| length-histogram anomalies | weekly | 0 | −100% |
| score explainability | none | cosine per hit | new |

## 5. Prevention Checklist
- [ ] Embeddings normalized at ingest; metric documented.
- [ ] Golden query set with expected top-k in CI.
- [ ] Vector length histogram + drift alarm.
- [ ] Top-k scores always returned for debugging.
- [ ] Brute-force vs ANN cross-check on a 1% sample.
- [ ] Model version stamped on every embedding row.
- [ ] Cold-start path when index is empty (return trending).
- [ ] Dashboard: latency, precision@5, drift alarms, QPS.

## 6. What "Good" Looks Like
- Search relevance stable across model swaps; every miss explainable by a score.

## 7. Stretch
- Graduate to ANN (HNSW) and PCA dimensionality reduction.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Cosine similarity: https://en.wikipedia.org/wiki/Cosine_similarity
- Principal component analysis: https://en.wikipedia.org/wiki/Principal_component_analysis
