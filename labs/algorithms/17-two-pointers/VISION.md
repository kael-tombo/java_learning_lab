# Vision: Two Pointers
> Linear scans with an invariant between two positions - sorted arrays and linked lists.

## Where this leads
- Pair-sum, dedup, partitioning, and Dutch-flag style in-place rearrangements.
- Cycle detection (tortoise and hare) and middle-finding in one pass.
- The invariant habit: stating what each pointer guarantees at every step.
## What mastering it unlocks
- Solve sorted two-sum in O(n) time and O(1) space with a moving-bounds argument.
- Remove duplicates in place and explain why the write pointer never overtakes correctness.
- Partition three values in one pass with the three-region invariant.
- Detect a cycle and find its start, justifying each phase of the algorithm.
- State the loop invariant for every two-pointer loop written.
## What it does not cover
- Variable-length window optimization criteria (that is the sliding-window lab).
- Pointer manipulation in balanced trees or pointer-jumping structures.
- External-memory or streaming adaptations beyond one pass.
## Core questions you will answer
- Why does moving the smaller side in sorted two-sum preserve a possible solution?
- What invariant relates the read and write pointers in dedup?
- Why can the hare never skip over the tortoise without meeting in a cycle?
- When do the pointers need sorting first, and what does that cost?
## How to judge progress
- Write any of these scans with the invariant stated up front.
- Trace pointer positions on adversarial inputs (all equal, empty, single element).
- Reduce a new Arrange-in-place task to a known pointer pattern.
## Common misuse
- Moving pointers without an invariant, then debugging by staring at traces.
- Applying two-sum pointers to unsorted arrays and hoping.
## After this lab
- 18-sliding-window for windows with content-dependent bounds.
- 03-searching for binary search when the array is sorted but pairs are not the goal.
One-line self-test: State the invariant of sorted two-sum before writing its loop.
