# MINI_PROJECT — Treaps (33)

2-week build: treap-backed ordered set with split/merge API and TreeSet benchmark.

## 1. Objective
Working Treap demo with invariant checker (BST on key, heap on priority), split/merge/insert/erase, plus benchmark vs TreeSet.

## 2. Requirements
1. Ops: insert, erase, member, split, merge, inorder, range [lo,hi].
2. CLI: seeded inserts + random erases.
3. ASCII tree printout with (key, priority).
4. Benchmark at n=1k/10k/100k.
5. README section: treap vs TreeSet trade-offs.

## 3. Two-week plan
Week 1: node + rotations + invariants + tests.
Week 2: split/merge API + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded inserts  2. split/merge  3. print tree
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | Treap (ns/op) | TreeSet (ns/op) | Notes |
|---|---|---|---|---|
| 1k | add |  |  |  |
| 10k | add |  |  |  |
| 100k | add |  |  |  |

## 6. Visualization idea
Print (key,priority) tree before/after a split at median.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; keyless (implicit) treap variant; JFR profile.
