# O(1)-Splice Playlist Service on a Doubly-Linked List

Stage 1 - intent. A playlist/task-queue server where blocks of songs or
jobs move between queues by relinking nodes, never by copying arrays.
A companion undo chain reuses the same node type with a bounded depth.

Stage 2 - operations. The list exposes push-front, push-back, detach
(node handle), splice-after, splice-range, and in-place reversal of a
segment. Detach plus splice-after give O(1) block moves once the handles
are known; indexed access is deliberately absent from the API.

Stage 3 - handles. Iterators act as stable cursors into the queue. Move
operations consume handles, and using a detached handle after its move
fails loudly instead of corrupting the chain.

Stage 4 - undo. Every mutation pushes an inverse record (relink pair)
onto a bounded undo chain; depth 64 by default. Popping undo replays the
inverse and drops the redo tail, so memory cannot grow with history.

Stage 5 - persistence. Queues serialize as ordered id sequences with
cursor bookmarks; reload rebuilds nodes and revalidates count parity.

Stage 6 - verification. A scripted workload (enqueue 20k, 5k splices,
2k reversals, undo bursts) runs against an ArrayDeque oracle that models
the same queue order; any divergence prints the op index and both orders.

Stage 7 - numbers worth quoting. Time a 10k-node block move against the
equivalent ArrayList remove/add pair, count allocations per splice, and
record undo memory at full depth.

Stage 8 - breakage rehearsal. Splice a range onto itself, detach the head
and tail in one batch, undo past the first record, reload a snapshot with
a missing id; each must end in a clean error, never a silent cycle.

Stage 9 - ship list. Implementation, workload script, oracle log showing
zero order mismatches, snapshot round-trip proof, one-page writeup naming
the workload where splicing beats array shifting and where it loses.

Stage 10 - review bar. Splice correctness under Randomized trials: 12.
Undo boundedness plus snapshot fidelity: 10. Honest splice-vs-shift
comparison with measured times: 8.
