# CODE_DEEP_DIVE — Data Structures Advanced

## Fenwick tree in Java
```java
class Fenwick {
    long[] t; int n;
    Fenwick(int n){ t = new long[n+1]; this.n=n; }
    void add(int i, long v){ for(i++; i<=n; i+=i&-i) t[i]+=v; }
    long sum(int i){ long s=0; for(i++; i>0; i-=i&-i) s+=t[i]; return s; }
    long range(int l,int r){ return sum(r) - sum(l-1); }
}
```
1-indexed by convention; parent trick walks set bits.

## Segment tree with lazy
- Node stores sum and pending add.
- push() applies pending to children before descending.
- Update is O(log n) if the lazy is applied at most once per visited node.
Pitfall: forgetting to push before reading children.

## Skip list in Java
- Thread-safe option: `ConcurrentSkipListMap`.
- Custom one: use a level int and `head[]` of forward pointers; promotion with `ThreadLocalRandom.nextInt()`.
Pitfall: level can exceed dangerously; cap at ~32.

## DSU
- parent[i] = i; rank or size.
- find: iteratively compress or recursively `parent[x]=find(parent[x])`.
- union by size/rank merges smaller into larger.
Pitfall: union by size with path compression is the right combo; growing tall chains otherwise.

## Bloom filter
- guava: `BloomFilter<T>` with expected insertions + fpp.
- Custom: m bits, k hashes via `Objects.hash` and double hashing: h_i(x) = h1(x) + i·h2(x).
Pitfall: k ≠ optimum inflates FPR badly.

## Merkle tree
- Leaf = hash(data); parent = hash(left‖right).
- Proof = list of sibling hashes; verify by recomputing root.
Pitfall: odd leaf count — duplicate last leaf or use arity handling.

## Suffix array
- Implement prefix doubling with counting-sort ranks for simplicity.
Pitfall: O(n log n) memory if you keep all rank arrays — reuse two arrays.

## Treap / Trie
See advanced-trees-deep.

## When to choose
- Fenwick beats segment tree on constants for additive prefix queries.
- Segment tree for non-commutative or lazy range writes.
- Skip list when you want a concurrent ordered map with simple code.
