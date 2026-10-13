# Theory: Two-Pointer Scans and Their Invariants
> Linear scans where the invariant between two positions does all the work.

## Problem statement
- Two pointers traverse a structure (array ends, read/write slots, fast/slow runners).
- Each pattern rests on an invariant relating the pointers; the code is the invariant made executable.
- Sortedness, partition regions, or cycle structure supplies the invariant's premise.

## Sorted two-sum
- Pointers lo = 0, hi = n-1 on ascending a; target T.
- If a[lo] + a[hi] == T done; if smaller, lo++ (no solution uses a[lo] with any index <= hi).
- If larger, hi-- symmetrically. Each step discards one index forever: O(n) time, O(1) space.
- Correctness is the discard argument: the moved pointer's current value cannot pair with anything left.

## In-place dedup
- Read pointer r scans; write pointer w marks the unique prefix a[0..w].
- Invariant: a[0..w] holds distinct values in order from a[0..r-1].
- On a[r] != a[w]: w++, copy. Sortedness makes adjacent comparison sufficient.
- O(n) time, O(1) extra space; returns w+1 as the new length.

## Dutch national flag
- Three regions: [0..lo) zeros, [lo..mid) ones, (hi..end] twos; [mid..hi] unknown.
- On 0 at mid: swap to lo, both advance. On 1: mid advances. On 2: swap to hi, hi retreats.
- Each step shrinks the unknown region: O(n) time, O(1) space, one pass.
- Invariant check at exit: unknown region empty means fully partitioned.

## Cycle detection (tortoise and hare)
- Phase 1: fast (2x) meets slow (1x) iff a cycle exists; meeting is guaranteed by relative speed 1.
- Phase 2: restart one at head, advance both 1x; they meet at the cycle start.
- Proof uses the cycle-length modularity: distance claims reduce to multiples of the cycle length.
- O(n) time, O(1) space; also yields cycle length by one more lap.

## Complexity derivation
- Every pattern moves pointers monotonically across n positions: at most 2n visits total.
- Per-step work O(1) gives Theta(n) time; extra space O(1) in all four patterns.
- Sorted two-sum needs sorted input: add O(n log n) sort if it is not.
- Counters on visits turn the bound into a measured check (see the mini project).

## Variants
- Closest-to-target pair with the same scan and a best-tracking variable.
- Middle-finding and kth-from-end with gap-maintained pointer pairs.
- Partition variants (odd/even, negative/positive) on the Dutch-flag skeleton.

## Pitfalls
- Applying two-sum pointers to unsorted arrays.
- Moving only one pointer after a pair hit, double-counting pairs.
- Letting the write pointer overtake the read pointer in dedup variants.
- Off-by-one on the unknown-region bounds in three-way partition.

## Interview signal
- State the discard argument for sorted two-sum before coding.
- Write the three-region invariant for Dutch flag from memory.
- Explain phase 2 of cycle detection with the modular-distance reason.
