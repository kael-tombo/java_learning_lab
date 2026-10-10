# Quiz: TreeMap / TreeSet

## Q1. What are RED and BLACK in the source, literally?
<details><summary>Answer</summary>
<code>RED = false; BLACK = true</code> — plain booleans on each Entry, not an
enum. New inserts are red; the root is forced black.
</details>

## Q2. Is `"a"` already in a case-insensitive TreeSet containing `"A"`?
<details><summary>Answer</summary>
Yes — identity is <code>compareTo/compare == 0</code>, not
<code>equals()</code>. Adding <code>"a"</code> is a silent no-op returning
false; <code>equals</code> disagrees with the set here by design.
</details>

## Q3. What null check runs on an EMPTY map, and why?
<details><summary>Answer</summary>
<code>addEntryToEmptyMap</code> calls <code>compare(key, key)</code> first —
forcing the ClassCastException/NPE for bad keys before anything is inserted,
so a doomed put fails atomically on size 0 too.
</details>

## Q4. What does subMap return — and what happens when you write through it?
<details><summary>Answer</summary>
A live bounded view (NavigableSubMap), not a copy. Writes go into the backing
tree (range-checked against the parent's bounds); tree writes show in the view.
</details>

## Q5. How does iteration walk without a sorted array copy?
<details><summary>Answer</summary>
Via on-the-fly <code>successor()</code> links: O(n) total, O(log n) worst per
first next-step, fail-fast on modCount drift like other collections.
</details>

## Q6. Bound the height of a 1M-entry tree and the rotations per insert.
<details><summary>Answer</summary>
Height &lt;= 2*log2(n+1) ~= 40. At most 2 rotations per insert (3 per delete);
recoloring does the rest — balancing is O(1) rotations after an O(log n) find.
</details>
