# Quiz: HashMap Internals

## Q1. Position rule
State spreader `h ^ (h >>> 16)` folds high bits down and compute the position of a key with spread hash
`0x0002_0001` in a 16-slot table.
<details><summary>Answer</summary>
Index = <code>0x0002_0001 &amp; 15 = 1</code>. The mask uses only the low
log2(n) bits, which is why the spread folds high bits down.
</details>

## Q2. Thresholds
What does TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 imply for a bucket that just hit 9 colliding entries
in a 128-slot table?
<details><summary>Answer</summary>
It treeifies (8 exceeded, table ≥ 64): worst case drops from O(n) to O(log n).
</details>

## Q3. Growth
Explain resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0 in one paragraph.
<details><summary>Answer</summary>
Capacity doubles (power of two preserved); each entry is re-decided by one
bit so the move is a single pass, amortized O(1) per insert — or the
structure-local equivalent (rotation/splice) for non-array variants.
</details>

## Q4. Nulls
What happens on the null-key/null-element probe, and why?
<details><summary>Answer</summary>
null key allowed once, hash 0, bucket 0 — the rule keeps "absent" distinguishable under the class's
ordering/concurrency contract.
</details>

## Q5. Views and fail-fast
What does `entrySet().iterator() EntryIterator` observe, and when does iteration throw?
<details><summary>Answer</summary>
Live-store views observe later writes. fail-fast via modCount, ConcurrentModificationException.
</details>

## Q6. Sizing default
State default capacity 16, load factor 0.75 and when the first backing allocation happens.
<details><summary>Answer</summary>
Lazily on first insert (array variants: 16 hash / 10 list); concurrent and
sorted variants size via their own controller/root on first write.
</details>
