# Lab 02: Vector Database Integration — Quiz

**Q1.** If embeddings are L2-normalized, cosine similarity equals...
- a) Squared L2 distance
- b) The dot product
- c) Euclidean distance
- d) Manhattan distance

**Q2.** For unit vectors, `|a-b|^2 =` ...
- a) `2 - 2cos(a,b)`
- b) `1 - cos(a,b)`
- c) `cos(a,b)`
- d) `2 + 2cos(a,b)`

**Q3.** A flat index is often the right choice at moderate scale because...
- a) It is always fastest
- b) It is exact and competitive up to ~1M vectors, with no tuning
- c) It uses less memory
- d) It supports filtering better

**Q4.** IVF search probes `nprobe` cells because...
- a) They contain the most vectors
- b) The nearest vectors are likely in the nearest centroids
- c) It is required by the format
- d) It improves recall monotonically

**Q5.** In HNSW, `efSearch` controls...
- a) Memory usage
- b) The candidate list size during search, trading latency for recall
- c) The number of layers
- d) Vector dimension

**Q6.** More HNSW layers with lower `M` typically means...
- a) Faster search, worse recall
- b) Better recall, more memory
- c) Less memory, worse recall
- d) No change

**Q7.** IVF-PQ reduces memory by...
- a) Storing fewer vectors
- b) Replacing subvectors with codebook indices
- c) Using smaller dimensions
- d) Compressing ids

**Q8.** Metadata filters should generally be applied...
- a) After scoring
- b) Before scoring (pre-filter) when selectivity is low
- c) Never
- d) Only on the top 1 result

**Q9.** Post-filtering fails to return k results when...
- a) The corpus is large
- b) The filter is selective, so fewer than k survive
- c) Vectors are normalized
- d) The index is HNSW

**Q10.** A namespace should include the embedding model version because...
- a) It speeds up search
- b) Vectors from different models are not comparable
- c) It reduces memory
- d) Providers require it

**Q11.** The source of truth for a vector index is...
- a) The index files
- b) The chunk store the index is rebuildable from
- c) The backups
- d) The embedding cache

**Q12.** Deletions should be handled as tombstones plus compaction because...
- a) Physical removal is slow
- b) Otherwise storage grows monotonically and reads stay slow
- c) Tombstones improve recall
- d) Providers forbid deletes

**Q13.** The main reason to rerank after ANN search is...
- a) It is faster
- b) Cross-encoders are more accurate than bi-encoder dot products
- c) It reduces memory
- d) It filters results

**Q14.** Rerank `k` should be chosen at the knee because...
- a) Larger k is always better
- b) Quality flattens while latency keeps rising
- c) Smaller k causes OOM
- d) k does not affect latency

**Q15.** High-filter-selectivity on HNSW degrades recall when using...
- a) Pre-filtering
- b) Post-filtering that discards most graph nodes
- c) Normalized vectors
- d) Small k

**Q16.** A duplicate near the top of results usually means...
- a) The index is broken
- b) Near-duplicate chunks were ingested
- c) Vectors are unnormalized
- d) The corpus is too large

**Q17.** Cross-tenant leakage in a shared index is prevented by...
- a) An API-level ACL only
- b) A mandatory tenant filter enforced inside the query
- c) Separate databases
- d) Larger `efSearch`

**Q18.** For 50M vectors with a memory limit, the appropriate index is...
- a) Flat
- b) IVF-PQ or a quantized index, with reranking
- c) HNSW with default parameters
- d) A Bloom filter

**Q19.** Scalar int8 quantization gives...
- a) Better recall than fp32
- b) ~4x less memory with a small recall loss
- c) Exact search only
- d) Faster HNSW graph traversal

**Q20.** Recall@k for a set of queries with gold ids is...
- a) The fraction whose gold id appears in the top k
- b) The average similarity score
- c) The fraction of vectors scanned
- d) The index build time

---

## Answers

1. **b** — `cos = dot/(|a||b|) = dot` when both are unit norm.
2. **a** — expanding `|a-b|^2` with unit norms gives `2 - 2dot`.
3. **b** — exactness plus zero tuning is worth a lot at that scale.
4. **b** — clusters are spatially coherent, so nearest cells contain nearest vectors.
5. **b** — a bigger candidate list finds more true neighbours at higher cost.
6. **b** — more layers mean more edges to store per node.
7. **b** — each subvector becomes a small index into a codebook.
8. **b** — pre-filtering keeps unauthorized vectors out of the ranking entirely.
9. **b** — post-filtering only sees what the search already returned.
10. **b** — mixing spaces produces meaningless similarities with no error.
11. **b** — the index is a derived artifact and must be rebuildable.
12. **b** — uncompacted tombstones degrade reads and grow storage.
13. **b** — it sees query and document together.
14. **b** — the marginal chunk adds latency but not quality.
15. **b** — the graph becomes disconnected.
16. **b** — dedup at ingest.
17. **b** — the filter is the boundary, not the API.
18. **b** — memory forces compression; rerank recovers accuracy.
19. **b** — 4x storage reduction, small error.
20. **a** — set recall over gold ids.

## Score Guide

18-20: ready for labs 03 and 06.
14-17: redo Exercises 5, 10, 14.
0-13: reread THEORY sections 2-8.