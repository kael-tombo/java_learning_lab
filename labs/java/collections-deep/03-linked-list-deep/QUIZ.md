# Quiz: LinkedList Deep Dive

## Q1. Which end does node(75000) walk from in a 100000-element list?
<details><summary>Answer</summary>
From <code>last</code> backward: <code>75000 &lt; 50000</code> is false, so it
walks <code>99999 - 75000 = 25000</code> hops backward instead of 75000 forward.
</details>

## Q2. Why does every mutation branch on first == null?
<details><summary>Answer</summary>
There is no sentinel node: empty means <code>first == last == null</code>, so
linkFirst/linkLast must handle the empty case explicitly on every path.
</details>

## Q3. How big is one element's overhead, exactly?
<details><summary>Answer</summary>
24 bytes per Node (12-byte header + 3 compressed refs) plus the element object
itself — versus 4 bytes per slot in ArrayList's array.
</details>

## Q4. What survives in ArrayDeque vs LinkedList regarding nulls?
<details><summary>Answer</summary>
LinkedList (Deque) permits null elements; ArrayDeque rejects them. Need nulls
or indexed access -> LinkedList; pure queue/stack speed -> ArrayDeque.
</details>

## Q5. When is mutation through an iterator legal vs fail-fast?
<details><summary>Answer</summary>
<code>ListIterator.set/remove/add</code> update expectedModCount — legal.
<code>list.remove()</code> during iteration drifts modCount — next
<code>next()</code> throws ConcurrentModificationException.
</details>

## Q6. Name the two private choke points of all structural change.
<details><summary>Answer</summary>
<code>link*</code> (linkFirst/linkLast/linkBefore) and <code>unlink*</code>:
every add/remove flows through them, updating size and modCount together.
</details>
