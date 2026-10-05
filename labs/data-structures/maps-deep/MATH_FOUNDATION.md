# MATH_FOUNDATION — Maps Deep

## HashMap load factor
Let n items, m buckets. Expected bucket size n/m. Keep it ≤ α (0.75) to keep chain length ≤ 1 on average → expected O(1) get/put. Resize when n > α·m; doubling makes amortized cost O(1) per insert.

## Resize amortization
Copying m elements into 2m: cost Θ(m) at each doubling. Across k doublings: 1+2+4+...+m ≈ 2m total copies for m insertions → amortized O(1).

## TreeMap height
Red-black height ≤ 2 log(n+1) → put/get/remove O(log n).

## Bloom filter FPR
Already in data-structures-advanced. Rehash: with k hash functions, P(bit remains 0) ≈ e^(−kn/m).

## LinkedHashMap LRU
Each access moves node to tail (O(1)); evict from head (O(1)). Each op constant regardless of n.

## ConcurrentHashMap
Amortized O(1) ops because each bucket CAS rarely retries; resize transfers buckets incrementally with helping by other threads.

## Sorted views
TreeMap.subMap(k1,k2) iterates O(s) over the s in-range keys; locating k1/k2 costs O(log n) each.

## Checklist
- [ ] Derive load factor/chain length bound
- [ ] Derive resize amortization
- [ ] State Bloom FPR
- [ ] State TreeMap height bound
