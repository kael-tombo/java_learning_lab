# Jitter Buffer and Telemetry Ring on Fixed Rings

Brief. Audio playback stutters when packets arrive unevenly; the
telemetry service drops history when its log grows unbounded. Both get
fixed-capacity rings: overwrite-oldest for audio continuity, backpressure
for telemetry with a drop counter. No allocation on the steady path.

Ring mechanics. Power-of-two capacity with index masking, monotonic
head/tail sequence counters (never bare indices) so full vs empty is
exact and wrap bugs are detectable. Push/pop O(1); batch drain for the
consumer side. SPSC first, then an MPSC variant with CAS tail - the two
are separate classes with separate tests.

Audio caller. Jitter buffer holding 200 ms of frames; late packets count
as lost, underruns increment a gap counter, overruns overwrite oldest
with an overrun counter. A scripted jitter trace (recorded interarrival
distribution) must yield identical gap/overrun counts across runs.

Telemetry caller. Sensor ring of 64k samples with snapshot reads for
the dashboard; readers never block writers, torn reads prevented by
sequence fencing. Snapshot contents verified against a locked model on
10k randomized interleavings.

Pipeline caller. Disruptor-style SPSC event pipe chaining two stages;
end-to-end order must equal input order on 100k events with zero drops
at 1x speed, and drops reconciled exactly at 4x overspeed.

Failure cards. Reader outruns writer (empty signal, not stale data),
writer laps reader in overwrite mode (overrun counted, newest intact),
torn snapshot attempt (sequence retry, counted), capacity not power of
two (constructor rejects).

Evidence. Trace replays, interleave logs, overspeed reconciliation,
fencing proof. Scoring: ring exactness 12, caller replay fidelity 10,
hazard coverage 8.
## Trace library
- Jitter trace A: mild wander.
- Jitter trace B: storm burst.
- Overspeed 4x case recorded.
- Interleave seed list kept.
- Gap counts must reproduce exactly.
