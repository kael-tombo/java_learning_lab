# Design: FIFO Core with Deque Extensions for a Request Pipeline

Objective. A request pipeline where inbound work waits FIFO, priority
lanes use a deque, and a bounded ring absorbs bursts. Everything below is
testable without threads first, then proven under two producers.

Shapes. RingFIFO for the hot lane (power-of-two mask, head/tail
monotonic counters), ArrayDeque lanes for stealable overflow, and a
scratch stack for payload validation. No unbounded queue exists anywhere.

Operation semantics. Enqueue is O(1) amortized; dequeue is O(1); peek
never mutates; drain-to crafts batches for workers. Sequence numbers
ride every item so loss, duplication, or reorder is detectable at the
sink without trusting the transport.

Backpressure. The ring is fixed at boot. Full means reject with a code,
never grow. Overflows increment a loss counter that the load test must
reconcile: enqueued equals dequeued plus dropped plus resident.

Ordering proof. A single-threaded script of 20k mixed ops runs against a
LinkedList oracle; orders must match exactly. Then a two-producer soak
checks sequence continuity at the sink and flags gaps.

Latency picture. Measure time-in-queue per item (enqueue stamp to dequeue
stamp), plus drain batch sizes under bursty arrivals. Report the wait
distribution at 1x and 4x producer speed, not just the average.

Snapshot story. Persist head/tail offsets plus resident items; reload
replays in original order and sequence validation passes. A torn file is
detected by a trailing checksum and refused.

Edge register. Dequeue on empty returns a typed empty signal. Full ring
under burst sheds with counters. Mixed deque ops (push-front during
drain) preserve FIFO order of the untouched suffix.

Done when. Oracle log clean, soak gap-free, snapshot round-trip byte
identical in order, and the report states the burst depth where shedding
starts. Weighting: ordering evidence 12, backpressure honesty 10,
snapshot plus edges 8.
