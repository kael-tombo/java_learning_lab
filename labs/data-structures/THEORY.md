# Data Structures Track — Theory

## 1. What this track covers
Foundations (labs 01-08): arrays, linked lists, stacks/queues, trees, graphs,
hash tables, heaps, tries. Intermediate (09-20): AVL/red-black/B-trees,
Bloom filters, union-find, segment trees, Fenwick trees, skip lists, LRU cache,
concurrent structures, spatial indexes, circular buffers, sparse-table RMQ,
persistent structures. Advanced (21-35): cuckoo/Robin Hood hashing, Merkle trees,
rollback DSU, XOR/unrolled lists, space-filling curves, HyperLogLog,
Count-Min sketch, MinHash/SimHash, van Emde Boas, cache-oblivious layouts,
ropes, dancing links, treaps, persistent segment trees, link-cut trees.

## 2. Complexity facts used across labs
- Array/heap operations: binary heap push/pop O(log n), heapify O(n).
- BST family: AVL, red-black, treap, splay-backed LCT give O(log n)
  (treap expected; LCT amortized); vEB gives O(log log U) on universe U.
- Range structures: segment tree O(log n) update/query; Fenwick O(log n)
  prefix sums; sparse table O(n log n) build with O(1) idempotent queries.
- Hashing family: chained/open addressing expected O(1); cuckoo worst-case O(1)
  lookup; Bloom FPR = (1 - e^(-kn/m))^k with optimal k = (m/n) ln 2.
- Sketches: HyperLogLog ~1.04/sqrt(m) error; Count-Min overestimates only;
  MinHash estimates Jaccard; SimHash flags near-dups by Hamming distance.
- Union-find with path compression + union by rank runs in near-alpha(n);
  the rollback variant drops compression to stay undoable at O(log n).

## 3. How to study a lab
Read the MOCK_INTERVIEW.md first: each of the 3 questions states a problem,
the key insight, the complexity, and a runnable Java snippet. Compile and run
every snippet with `javac --release 21` before reading the explanation twice.
Then complete the REAL_WORLD_PROJECT.md service slice with measured SLOs.

## 4. Common pitfalls
- Quoting O(1) hash ops without naming the adversarial case (hash flooding,
  degenerate clustering, cuckoo load ceilings near 0.5 for two hashes).
- Using a sparse table on changing data (rebuild is O(n log n)).
- Forgetting full/empty disambiguation in ring buffers (keep a size field).
- Treating sketches as exact (HLL/CMS/MinHash all carry stated error).
- Compressing paths in a DSU that must roll back (log sizes instead).

## 5. Exit bar
Explain any structure's core invariant, give its operation costs, write the
key routine from memory, and size a production use-case (SLOs, memory, risks).
