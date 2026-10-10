# Quiz: ConcurrentHashMap

## Q1. What does putVal do with a null key or value?
<details><summary>Answer</summary>
Throws <code>NullPointerException</code> immediately. <code>get(k) == null</code>
must mean "absent", so nullable values would break putIfAbsent/compute/merge.
</details>

## Q2. What is locked during put, and what stays lock-free?
<details><summary>Answer</summary>
Only the bucket head: <code>synchronized (f)</code> on the first node. Empty-bin
inserts use pure CAS (<code>casTabAt</code>); reads use volatile
<code>tabAt</code> with no lock at all.
</details>

## Q3. A reader meets a bucket whose head hash is MOVED. What happens?
<details><summary>Answer</summary>
It follows the ForwardingNode to the new table (old table stays readable during
transfer). A writer instead calls <code>helpTransfer</code> and joins the resize.
</details>

## Q4. How is size computed, and why is it approximate?
<details><summary>Answer</summary>
<code>sumCount() = baseCount + sum(counterCells)</code>. Under contention some
cell CAS may be in flight, so the sum is a snapshot that can be stale instantly;
it is clamped to <code>[0, Integer.MAX_VALUE]</code>.
</details>

## Q5. What does spread() do and why?
<details><summary>Answer</summary>
Masks the hash with HASH_BITS (<code>0x7fffffff</code>) so it is non-negative
while dispersing high bits; index is then <code>(n-1) &amp; hash</code>, valid
because capacity is always a power of two.
</details>

## Q6. When does a bin treeify, and what locks it then?
<details><summary>Answer</summary>
At 8 entries with table capacity >= 64 (untreeify at 6 on resize-split). The
TreeBin root is locked instead of the list head; readers may spin-retry briefly.
</details>
