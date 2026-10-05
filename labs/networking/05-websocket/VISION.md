# VISION — WebSocket: Persistent Connections, Real Problems
> Where this lab takes you: from "it's just HTTP with `Upgrade`" to handling backpressure, reconnection, and scale-out honestly.

## The Arc
1. **The handshake** — `Upgrade: websocket`, `Sec-WebSocket-Key/Accept`, and why it is not encryption.
2. **Framing** — opcodes, masking, fragmentation, and control frames.
3. **Lifecycle** — ping/pong, close handshake, and detecting a silently dead connection.
4. **Scale** — connection affinity, load balancer timeouts, and the pub/sub problem.
5. **Application patterns** — presence, chat ordering, backpressure, and reconnection.

## Milestones (checkable)
- [ ] M1: perform the handshake by hand and verify the `Sec-WebSocket-Accept` value.
- [ ] M2: decode a masked frame and explain why the client must mask and the server must not.
- [ ] M3: implement ping/pong and detect a dead peer that never sent a close frame.
- [ ] M4: explain why a WebSocket cannot be load balanced without sticky sessions, and solve it.
- [ ] M5: implement a reconnection protocol with message replay that avoids duplicates.

## Core Competencies
- Handshake mechanics, frame format, and control-frame semantics.
- Keepalive, idle detection, and graceful close, which are operational requirements.
- Backpressure: what happens when a slow client cannot keep up with a broadcast.
- Pub/sub across horizontally scaled nodes, and delivery semantics you can actually promise.

## Anti-Goals
- Assuming the connection is alive because the socket is open.
- Broadcasting to every connection with no slow-consumer policy.
- Treating the handshake as providing authentication or confidentiality.

## Interview Lens
- "How do you scale a WebSocket service across ten nodes?"
- "Your chat messages arrive out of order after a reconnect. Fix it."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: raw handshake, frame codec.
- Wk2 QUIZ/FLASHCARDS to 90%+; ping/pong and backpressure experiments.
- Wk3 MINI_PROJECT: chat server with presence and reconnection replay.
- Wk4 REAL_WORLD_PROJECT: a real-time notification or collaboration service.

## Done = You Can
- Build and operate a WebSocket service that survives node restarts, slow clients, and
  reconnection without losing or duplicating messages.
