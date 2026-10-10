# Reflection: PriorityQueue

## What surprised you?

Most learners expect "priority queue" to mean "sorted container". The heap
violates that exactly once — iteration — and everywhere else behaves. Write
down the moment you internalized that only the root has a contract.

## Check your model

1. Without running code: insert 4, 1, 3, 2, 16, 9, 10, 14, 8, 7 into an
   empty heap on paper. What is index 1? (Answer: 2 — work the sifts.)
2. Why does `poll()` move the *last* element rather than shifting?
   What would shifting cost?
3. Why can `removeAt` need `siftUp` after trying `siftDown`? Construct the
   case: remove a large element whose replacement (last slot) is small.

## Connect

- Where have you used sort-then-take-first where a heap fits (task
  runners, expiry sweeps, merge loops)?
- What breaks in your code if iteration order changes between JDK
  releases? Heaps make no order promise — would you notice?

## The one-line takeaway

A heap maintains the minimum with minimum disturbance: one path per op,
nothing else moves. If your summary needs more than that sentence plus the
three formulas (parent, growth, heapify start), it is not finished.
## One more probe

4. Growth: starting from capacity 11, list the next three capacities and
   state which rule produced each (+2 vs 1.5x). At which insertion count
   does the kink at 64 first bite?
5. `contains` is O(n) — sketch a workload (e.g. scheduler with cancel)
   where that row dominates, and name the companion structure that fixes
   it. What must be kept in sync between the two, and what breaks if they
   drift?

Revisit your one-line takeaway after answering: it should now mention the
growth kink by name.
