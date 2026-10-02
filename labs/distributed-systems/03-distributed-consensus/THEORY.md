# Distributed Consensus: Theory

## Problem Definition
Multiple processes must agree on a single value despite failures (crash, network, Byzantine).

## Properties
- **Agreement**: All non-faulty processes decide on the same value
- **Validity**: If all processes propose the same value v, then any decided value is v
- **Termination**: All non-faulty processes eventually decide
- **Integrity**: No process decides more than once

## FLP Impossibility
In an asynchronous system, no deterministic consensus algorithm can guarantee termination with even one crash failure. Real systems use:
- Failure detectors (unreliable but practical)
- Randomized algorithms
- Partial synchrony assumptions

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "In Search of an Understandable Consensus Algorithm" (Ongaro & Ousterhout, USENIX ATC '14, Jun 2014) — https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro — Raft decomposes consensus into leader election, log replication, and safety; apply this split when implementing the lab's leader-election exercise instead of mixing concerns.
- "In Search of an Understandable Consensus Algorithm" (Ongaro & Ousterhout, USENIX ATC '14, Jun 2014) — https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro — Strong-leader log replication (entries flow only leader→followers) is the model for the lab's replication exercise; use randomized election timers to avoid split votes.
- "In Search of an Understandable Consensus Algorithm" (Ongaro & Ousterhout, USENIX ATC '14, Jun 2014) — https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro — Joint-consensus membership change with overlapping majorities keeps the cluster available; mirror this in the lab's membership-change exercise rather than swapping configs atomically.
- "In Search of an Understandable Consensus Algorithm" (Ongaro & Ousterhout, USENIX ATC '14, Jun 2014) — https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro — User study (43 students, 33 answered Raft better than Paxos) supports the lab's understandability framing; cite the ATC paper, not secondary summaries, when comparing Raft vs Paxos in lab write-ups.
