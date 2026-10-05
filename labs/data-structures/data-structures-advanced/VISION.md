# VISION — Data Structures Advanced

Vision: a small, deliberate toolbox for range queries, connectivity, filters, proofs, and pattern search — each picked by workload, not habit.

## Mental models
- Prefix-sum structures are "running totals with fast point updates" (Fenwick, segment tree).
- Skip lists are "binary search over linked levels."
- DSU is "two operations: find which set, union two sets."
- Bloom is "a bitset that only gives a positive maybe."
- Merkle is "a hash tree that proves one leaf with O(log n) siblings."
- Suffix array is "sorted suffixes you binary-search."

## Decision table
| Workload | Pick |
|---|---|
| Prefix sums | Fenwick |
| Range add + range query | Segment tree (lazy) |
| Concurrent ordered map | Skip list |
| Connectivity / offline MST | DSU |
| Membership, no false negatives | Bloom |
| Integrity proofs | Merkle |
| Pattern search | Suffix array |

## Career path
- Shows up in: streaming, databases, distributed systems, interviews.
- Tell the story: "I picked this structure because of its SLO; I know its one-sided error."

## Done when
- [ ] State each bound (time + space)
- [ ] Explain Bloom FPR and trade of k
- [ ] Mini + real-world projects shipped
