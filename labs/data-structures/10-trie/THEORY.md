# THEORY — Trie (Prefix Tree)

*Prefix search, autocomplete, IP routing.*

## 1. Definition
A trie stores strings by sharing common prefixes: each edge is a character and each node marks end-of-word plus subtree counts.

Why it exists: it beats the naive alternative (linear scan / full rebuild / coarse locking) by structuring state so the hot path stays sublinear or constant.

## 2. Mental picture
Draw the structure on paper before coding: nodes and links for pointer structures, intervals for range structures, registers for sketches.
Label the hot path (lookup/query) and the maintenance path (rebalance/split/propagate).

## 3. Operations and contracts

| Operation | Contract | Cost |
|---|---|---|
| `insert(word)` | add a word, creating nodes as needed | O(L) |
| `search(word)` | exact match incl. end-of-word flag | O(L) |
| `startsWith(prefix)` | prefix existence check | O(P) |
| `countWordsWithPrefix(p)` | subtree word count | O(P) |
| `delete(word)` | unmark + prune dead nodes | O(L) |
| `autocomplete(p,k)` | DFS top-k under prefix node | O(P + k*Sigma) |

## 4. Invariants (must never break)
1. Every root-to-node path spells a prefix of some inserted key
2. endOfWord flag distinguishes 'car' from prefix of 'cart'
3. passCount/subtree counts stay consistent after insert/delete
4. alphabet mapping (array vs HashMap) is fixed per implementation

## 5. Complexity summary
State best/average/worst separately. Randomized structures report expectations; amortized ones report the potential argument; sketches report error bounds.
Compare against the baseline: sorted array, hash table, balanced tree, or brute force — and name the workload where this structure wins.

## 6. Design trade-offs
- Memory vs speed: auxiliary tables/registers buy query speed.
- Static vs dynamic: preprocessed structures query fast but rebuild on update.
- Exact vs approximate: sketches trade error for orders-of-magnitude less memory.
- Simple vs concurrent: lock-free variants cost complexity for scalability.

## 7. Failure modes
- Broken invariant after update (counts, tags, parents stale).
- Degenerate input (adversarial keys, sorted inserts, hash collisions).
- Off-by-one in index math (1-based trees, half-open intervals).
- Overflow / precision loss in aggregates and hash narrowing.

## 8. Trace it by hand (do this now)
1. Take a 7-element example and run two operations step by step.
2. Write the array/tree state after each step.
3. Verify every invariant holds at each checkpoint.
4. Predict the exact return value before running code.

## 9. When to use / when to avoid
Use for: search-engine autocomplete + IP longest-prefix match.
Avoid when: the workload is tiny, fully static-simple, or already served by `java.util` with no measured bottleneck — complexity must be earned.

## 10. Interview framing (30 seconds)
Say: 'Trie (Prefix Tree) keeps prefix search, autocomplete, ip routing fast by maintaining every root-to-node path spells a prefix of some inserted key; the hot path costs O(L).'

## 11. Checklist
- [ ] Can draw it
- [ ] Can state all invariants
- [ ] Can derive each complexity
- [ ] Knows two production users
