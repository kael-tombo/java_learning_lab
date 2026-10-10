# Exercises: CopyOnWriteArrayList

## 1. Snapshot proof

```java
var list = new java.util.concurrent.CopyOnWriteArrayList<>(java.util.List.of("A","B"));
var it = list.iterator();
list.add("C"); list.remove("A");
var seen = new java.util.ArrayList<String>(); it.forEachRemaining(seen::add);
System.out.println(seen);   // [A, B] — construction state, exactly
System.out.println(list);   // [B, C]
```

## 2. No-CME under concurrent mutation

Start an iterator; concurrently add/remove 10k elements from another
thread; assert the iterator completes with its pinned contents and never
throws. Contrast with ArrayList (CME expected).

## 3. UOE probe

Assert `iterator().remove()`, plus list-iterator `set`/`add`, all throw
`UnsupportedOperationException`.

## 4. addIfAbsent atomicity

N threads race `addIfAbsent(same)`; assert exactly one true and final size
+1. Repeat check-then-act (`contains`+`add`) to show duplicates without
the atomic method.

## 5. Copy-cost benchmark

Time 1k `add`s on COW vs `synchronizedList(ArrayList)` at n = 1k and
n = 100k. Plot the O(n)-per-write divergence; record allocation rate
(JFR or `-Xlog:gc`) for the COW run.

## 6. Retention demo

Hold an iterator, perform 500 writes of 10k-element lists, heap-dump:
count live `Object[]` versions pinned by the iterator. Then scope the
iterator tightly and show versions collectible.
