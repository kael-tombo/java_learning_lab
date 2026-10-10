# Exercises: Open-Addressing HashMap

## 1. Minimal put/get/probe

Implement table n=8, `put`/`get` with spread + linear probe. Insert keys
with colliding low bits; assert `get` finds each and counts probe steps.

## 2. Tombstone correctness proof

Insert A, B colliding; `remove(A)`; assert `get(B)` still hits. Then null
a slot instead (deliberate bug build) and show `get(B)` falsely misses —
the before/after pair is the lesson.

## 3. Tombstone reuse

Delete A, insert D hashing to the same index; assert slot reuse (capacity
unchanged, tombstone count decremented) and all keys retrievable.

## 4. Measure the probe knee

Fill to α = 0.5, 0.7, 0.9 with uniform keys; measure mean miss-probe
length. Compare against 2.5 / 6 / 50 theory. Repeat with unspread hashes
varying only in high bits; watch the knee arrive early.

## 5. Resize rebuild

Force growth; assert: only live entries rehashed, `size` recounted,
tombstones zeroed, every pre-resize key still gets. Diff key sets across
5 consecutive resizes in a loop to 10k entries.

## 6. Fuzz against java.util.HashMap

Randomized put/get/remove/size streams (seeded), diffing your map vs
HashMap after every 100 ops. Include null-key policy and iteration
contents (order-insensitive) in the diff.
