# Why Bloom Filters Exist

Exact membership costs one stored key per element — pointers, headers,
table overhead (~100 bytes/string in a HashSet). When the set is huge,
remote, or shipped to clients, that price is disqualifying — yet most
queries are answered "no" (absent URLs, unseen IDs, non-member keys), and
a "no" needs no evidence beyond one zero bit.

The filter buys the exact contract these workloads need:

- ~10 bits/element instead of ~100 bytes (100× compression at 1% FPR);
- "definitely absent" answered locally, saving the expensive path (disk
  seek, network fetch, full scan) for the rare "possibly present";
- mergeable by OR across nodes without moving elements.

Alternatives lose somewhere: shipping the full set costs bandwidth/memory;
caching negatives in a HashSet grows unboundedly with distinct misses;
server-side-only checks pay latency per query. The filter sits in the gap:
a compact, composable "probably-not" oracle whose errors land only on the
side (false positives) that falls back to the exact check anyway.
## The gate-and-fallback economics

Let fallback cost C per check and filter FPR p over Q queries: expected
fallback spend = p·Q·C plus filter memory m(p) fixed. Exact-set cost is
Q·C' (C' often ≥ C with worse locality) plus full-set memory. The filter
wins exactly when p·Q·C + m(p) << Q·C' — i.e. mostly-negative workloads
with costly confirmations. Size p from that inequality, not from habit:
p = 5% with a 1ms fallback beats p = 0.1% with megabytes of bits, and the
formulas price both options in one line each. Rerun the inequality whenever
C or Q changes by an order of magnitude — the right p moves with them.
