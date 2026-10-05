# VISION — TCP & UDP: Two Transports, Two Contracts
> Where this lab takes you: from `new Socket(host, port)` to explaining why your app's latency profile comes from Nagle's algorithm.

## The Arc
1. **TCP** — connection-oriented, reliable, ordered, byte-stream; what that costs you.
2. **UDP** — datagrams, no guarantees, and the applications that want exactly that.
3. **Sockets in Java** — blocking `Socket`, NIO channels, selectors, and non-blocking I/O.
4. **Latency & buffering** — Nagle, delayed ACK, `TCP_NODELAY`, and the 40 ms you cannot explain.
5. **Choosing** — when TCP, when UDP, when neither (QUIC, HTTP/3).

## Milestones (checkable)
- [ ] M1: implement a blocking echo server and a NIO selector-based one, and compare.
- [ ] M2: measure the 40 ms delay that Nagle plus delayed ACK causes, then fix it.
- [ ] M3: explain why TCP is a byte stream, not a message protocol, and what that implies.
- [ ] M4: write a UDP protocol with sequence numbers, ACKs, and retransmission.
- [ ] M5: state the four guarantees UDP does not give you.

## Core Competencies
- Connection lifecycle, flow control, and the cost of reliability.
- Java socket options: `SO_TIMEOUT`, `SO_REUSEADDR`, `TCP_NODELAY`, buffer sizing.
- Non-blocking I/O with `Selector`, and the read-buffering discipline it requires.
- Latency debugging: which layer is introducing the delay you can feel.

## Anti-Goals
- Assuming one `read()` returns one message.
- Using blocking sockets inside a request-handling thread pool without backpressure thought.
- Enabling Nagle on a request/response protocol with small messages.

## Interview Lens
- "Why do I get exactly 40 ms extra latency on small writes?"
- "When is UDP the right choice, and what do you have to build yourself?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: echo servers, blocking then NIO.
- Wk2 QUIZ/FLASHCARDS to 90%+; latency experiments with socket options.
- Wk3 MINI_PROJECT: reliable UDP with reliability you implement.
- Wk4 REAL_WORLD_PROJECT: a real-time telemetry pipeline choosing the transport deliberately.

## Done = You Can
- Pick a transport for a workload and defend it with measured latency, throughput, and
  failure-behaviour data rather than folklore.
