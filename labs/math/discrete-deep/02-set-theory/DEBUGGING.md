# Debugging: Set Theory Code

## Symptom: Duplicates Appear in a HashSet

A `HashSet` decides identity with `hashCode()` first, `equals()` second. If two distinct objects represent the same element (say two `Point(2,3)` instances built without a shared `equals`/`hashCode`), the set keeps both. Fix: override both methods together, or store a canonical representation (a `record Point(int x, int y)` in Java derives both automatically).

Debug recipe:

1. Print `set.size()` after each insertion — if it grows when it should not, identity is broken.
2. `set.stream().map(Object::hashCode).forEach(System.out::println)` — equal elements must share a hash.
3. Verify `a.equals(b) && b.equals(a)` for any pair your domain considers identical.

## Symptom: An Element Added Before Mutation Disappears

`HashSet` caches the hash of the key at insertion time. Mutating a field used by `hashCode()` after `add()` strands the object: `contains()` looks in the wrong bucket and misses it, yet `iterator()` still yields it. Never mutate a set element's hash-relevant fields while it lives in a `HashSet`; copy-remove-mutate-add instead.

## Symptom: ConcurrentModificationException During Iteration

Java's `HashSet` iterators are fail-fast. Removing through the collection (`set.remove(x)`) while an enhanced-for loop runs throws `ConcurrentModificationException` on the next `next()`. Correct removals: iterate over an `Iterator` and call `it.remove()`, or use `set.removeIf(pred)`.

## Symptom: Floating-Point Elements Vanish

`new HashSet<>(List.of(0.1 + 0.2))` behaves differently from `List.of(0.30000000000000004)`: `Double.hashCode` and `Double.equals` treat NaN as equal to itself (unlike `==`) but distinguish `0.0` from `-0.0`. If your "set" of doubles loses values, you are comparing bit patterns rather than mathematical reals; quantize (e.g., store `Math.round(x * 1e6)`) before insertion.

## Symptom: Set Algebra Result Is Off by the Overlap

Given `union = new HashSet<>(a); union.addAll(b);` and `inter = new HashSet<>(a); inter.retainAll(b);`, a buggy `difference` often does `a.addAll(b)` then `removeAll(inter)` — that computes A Δ B, not A − B. A − B is `new HashSet<>(a); diff.removeAll(b);` and must satisfy `diff.size() == a.size() - inter.size()`; assert that invariant in tests.

## Symptom: Power Set Contains the Wrong Number of Elements

Enumerating subsets by an integer mask from 0 to (1 << n) − 1 yields exactly 2^n lists. If you skip mask 0 you lose ∅; if you use `<=` you generate 2^n + 1 (and an out-of-range mask). Check `List.of(subsets).size() == 1 << n` in a test with n = 3 → 8.

## Symptom: Set Membership Test Is Slow in a Loop

`List.contains` inside a loop gives O(n·m). Convert once to a `HashSet` and each probe becomes O(1) amortized. If profiling shows `List.contains` hot in a deduplication pass, that conversion is the fix.
