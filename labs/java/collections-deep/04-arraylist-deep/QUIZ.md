# Quiz: ArrayList Deep Dive

## Q1. What capacities follow 10 under 1.5x growth?
<details><summary>Answer</summary>
10 -> 15 -> 22 -> 33 (each <code>oldCap + (oldCap &gt;&gt; 1)</code>, computed
in <code>ArraysSupport.newLength</code> with min-growth and max-size clamps).
</details>

## Q2. What allocates on `new ArrayList<>()` vs `new ArrayList<>(0)`?
<details><summary>Answer</summary>
Neither allocates. The no-arg ctor uses <code>DEFAULTCAPACITY_EMPTY_ELEMENTDATA</code>
(first add -> 10); the zero-arg uses <code>EMPTY_ELEMENTDATA</code> (grows to
exactly what is needed). Two sentinels, two first-grow behaviors.
</details>

## Q3. What does fastRemove do with the freed slot, and why?
<details><summary>Answer</summary>
Sets <code>elementData[--size] = null</code>: without it the array would pin a
logically-removed object and leak memory until overwritten.
</details>

## Q4. Which method does NOT bump modCount, and what breaks because of it?
<details><summary>Answer</summary>
<code>set(i, e)</code> — value replacement is not structural. An iterator will
not detect a concurrent <code>set</code>; only add/remove/grow trip fail-fast.
</details>

## Q5. How many moves do 1M unsized appends cost vs presized?
<details><summary>Answer</summary>
~3M word moves unsized (geometric series at 1.5x) vs exactly 1M presized —
same O(n), 3x constant. That gap is the entire case for
<code>ensureCapacity</code>.
</details>

## Q6. Why is ArrayList still thread-unsafe under synchronizedList for iteration?
<details><summary>Answer</summary>
The wrapper syncs each method, but iteration spans many calls — you must still
hold <code>synchronized (list)</code> around the loop, or use
CopyOnWriteArrayList (copy-on-write, snapshot iterators).
</details>
