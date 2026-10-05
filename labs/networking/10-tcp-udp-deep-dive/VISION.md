# VISION — TCP/UDP Deep Dive: Where the Latency Actually Lives
> Where this lab takes you: from using sockets to simulating congestion control and explaining a throughput plateau from first principles.

## The Arc
1. **TCP mechanics** — header fields, the state machine, and sequence/acknowledgement arithmetic.
2. **Congestion control** — slow start, congestion avoidance, fast recovery, and CUBIC/BBR.
3. **Flow control** — the receiver window, zero-window conditions, and window scaling.
4. **Latency traps** — Nagle, delayed ACK, bufferbloat, and `TCP_NODELAY` trade-offs.
5. **Real transport design** — reliable UDP, QUIC's changes, and when tuning beats redesigning.

## Milestones (checkable)
- [ ] M1: compute a TCP sequence/ack number by hand from a captured handshake.
- [ ] M2: simulate slow start and congestion avoidance and predict cwnd at a given RTT.
- [ ] M3: explain a 40 ms stall as Nagle plus delayed ACK, then eliminate it.
- [ ] M4: implement congestion control in a simulator and compare Reno against CUBIC.
- [ ] M5: measure bufferbloat and explain why bigger buffers made latency worse.

## Core Competencies
- TCP header semantics, window scaling, and the state machine.
- Congestion control algorithms, their signals, and their failure modes.
- Latency attribution: which layer introduced the delay you can feel.
- Simulation-driven reasoning about throughput, RTT, and loss.

## Anti-Goals
- Tuning `rcvbuf`/`sndbuf` without understanding which side is the constraint.
- Assuming congestion control is the only reason throughput stops scaling.
- Comparing algorithms without controlling for RTT, loss, and buffer size.

## Interview Lens
- "Why does throughput plateau at a specific window size?"
- "Explain bufferbloat and why a bigger buffer is worse."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: packet analysis, state machine, window arithmetic.
- Wk2 QUIZ/FLASHCARDS to 90%+; congestion control simulation.
- Wk3 MINI_PROJECT: congestion simulator plus reliable UDP.
- Wk4 REAL_WORLD_PROJECT: a high-throughput data pipeline with measured tuning.

## Done = You Can
- Take a throughput or latency number, attribute it to a specific TCP mechanism, and
  prove the attribution with a controlled experiment.
