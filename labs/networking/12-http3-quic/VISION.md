# VISION — HTTP/3 & QUIC: Fixing the Transport We Inherited
> Where this lab takes you: from "HTTP/3 is HTTP over TLS" to implementing per-stream flow control and stream migration.

## The Arc
1. **Why QUIC** — the head-of-line blocking and handshake problems QUIC actually solves.
2. **QUIC foundations** — connection ID, streams, and why transport is split from TLS.
3. **Cryptography** — TLS 1.3 in QUIC, 0-RTT, and what it costs you in replay risk.
4. **Multiplexing** — independent streams, per-stream flow control, and congestion control.
5. **Migration & resilience** — connection migration, path validation, and loss recovery.

## Milestones (checkable)
- [ ] M1: explain head-of-line blocking in HTTP/1.1 and HTTP/2, and how QUIC removes it.
- [ ] M2: identify a QUIC packet's header fields and why there is no separate TCP header.
- [ ] M3: implement per-stream flow control and show one stream cannot block another.
- [ ] M4: explain 0-RTT replay risk and the mitigations available.
- [ ] M5: describe what a Connection ID enables that a 4-tuple cannot.

## Core Competencies
- QUIC packet structure: long/short headers, packet number encoding, frame types.
- Streams, flow control credit, and per-stream versus per-connection limits.
- TLS 1.3 integration, session resumption, and 0-RTT semantics.
- Loss detection differences: packet thresholds, ACK ranges, and PTO.

## Anti-Goals
- Treating HTTP/3 as a version bump rather than a transport change.
- Assuming 0-RTT is free because it saves a round trip.
- Ignoring the fact that a QUIC connection is not a TCP connection to your metrics.

## Anti-Goals note
QUIC moves complexity from the kernel into the protocol. Understanding *where* it moved
is the point of the lab.

## Interview Lens
- "Explain head-of-line blocking and how HTTP/2 only moved part of it."
- "Your QUIC server leaks memory per connection. Where would you look?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: packet structure, stream semantics, 0-RTT.
- Wk2 QUIZ/FLASHCARDS to 90%+; flow control and loss experiments.
- Wk3 MINI_PROJECT with stream multiplexed transfer and a flow control test.
- Wk4 REAL_WORLD_PROJECT: HTTP/3 rollout for a real traffic profile.

## Done = You Can
- Explain what QUIC changes, implement its flow control, and make an evidence-based
  argument for or against an HTTP/3 rollout.
