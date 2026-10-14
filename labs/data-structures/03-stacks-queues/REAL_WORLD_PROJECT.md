# Runbook: Bounded Job Queue with Overflow Policy

Service: worker-pool job queue fronted by a bounded FIFO, with a LIFO
scratch stack for expression/bracket checks in job payloads. This page is
the operator-facing contract: what the queue guarantees, what it drops,
and how to tell which happened.

Normal operation. Producers enqueue jobs; workers dequeue FIFO. Depth,
enqueue rate, dequeue rate, and overflow drops export as counters each
second. A depth watermark at 80 percent pages before the ceiling bites.

Policies. Three overflow modes ship behind a flag: block with timeout,
drop-newest with a counter, drop-oldest with a counter. The default is
drop-newest; mode changes require a restart and are logged at boot.

Stack sidecar. Payloads carrying bracketed expressions pass through an
ArrayStack validator; invalid payloads park in a quarantine file with the
failure offset. The queue never blocks on validation longer than its
per-job budget; overruns count as validation timeouts.

Alerts. Fire when p99 wait-in-queue crosses the posted threshold for five
minutes, when drops exceed 0.1 percent of enqueues, or when the
validator quarantine grows faster than drains.

Failure table. Worker stall: depth climbs, watermark pages, oldest jobs
age out per retention. Producer flood: drops increment, no OOM because
the bound holds. Restart mid-drain: snapshot of pending ids reloads and
requeues; in-flight jobs are redelivered at most once per worker lease.

Recovery drills. Kill a worker mid-batch and confirm redelivery. Flood
with 5x producers for 60 seconds and confirm the drop counter matches
enqueues minus dequeues minus depth delta. Corrupt the snapshot and
confirm boot refuses with a named error instead of partial state.

Release proof. Attach the counters log from the flood drill, quarantine
samples from the bracket suite, and a restart log showing restored depth.
Mark: queue semantics under flood 12, validator quarantine quality 10,
restart fidelity 8.
