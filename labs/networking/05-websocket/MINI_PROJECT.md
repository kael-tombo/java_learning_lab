# WebSocket - MINI PROJECT

## Project: Relay — a WebSocket chat and presence server with reconnection replay

Implement the handshake and frame codec by hand, then build a chat server with presence,
broadcast, heartbeats, slow-client handling, and a replay cursor so a reconnecting client
does not lose or duplicate messages.

### Architecture

```
  Client A            Relay Server (N instances)            Client B
  ────────            ──────────────────────────            ────────
  GET /ws (Upgrade)   1. complete handshake (Sec-WebSocket-Accept)
  ──────────────────▶ 2. authenticate the upgrade request (the handshake is plain HTTP,
                       so auth must happen HERE, not in a WebSocket message)
  ◀────────────────── 101 Switching Protocols
  frames ◀──────────▶ 3. route: presence, broadcast, DMs
                      4. ping every 30s; drop a peer missing 2 pongs
                      5. broadcast with slow-client backpressure
  reconnect:          6. client sends {resume_from: lastSeq} → replay, then live
```

### Implementation

Handshake and frame codec, written from the spec:

```java
public final class WebSocketCodec {
    // The accept value proves the server understood the key, which stops a cache from
    // replaying a stale 101 response to a different client. It is NOT a security control.
    static String acceptKey(String clientKey) {
        String magic = clientKey.trim() + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
        return Base64.getEncoder().encodeToString(sha1(magic.getBytes(US_ASCII)));
    }

    /** Frame: FIN/RSV/opcode byte, MASK+length, optional masking key, payload. */
    static ByteBuffer encode(int opcode, ByteBuffer payload, boolean mask) {
        int len = payload.remaining();
        ByteBuffer out = ByteBuffer.allocate(2 + 4 + len);
        out.put((byte) (0x80 | opcode));                       // FIN=1: no fragmentation
        int lengthByte = mask ? 0x80 : 0x00;                  // MASK bit
        if (len < 126) out.put((byte) (lengthByte | len));
        else if (len <= 0xFFFF) { out.put((byte) (lengthByte | 126)); out.putShort((short) len); }
        else { out.put((byte) (lengthByte | 127)); out.putLong(len); }   // 8-byte extended length
        if (mask) {
            byte[] key = new byte[4]; SecureRandom.getInstanceStrong().nextBytes(key);
            out.put(key);
            byte[] p = new byte[len]; payload.get(p);
            for (int i = 0; i < len; i++) out.put((byte) (p[i] ^ key[i % 4]));   // masked
        } else {
            out.put(payload);
        }
        return (ByteBuffer) out.flip();
    }
}
```

Heartbeat and dead-peer detection, which is the difference between a service and a leak:

```java
@Component
class HeartbeatService {
    private static final Duration INTERVAL = Duration.ofSeconds(30);
    private static final int MISSED_LIMIT = 2;

    @Scheduled(fixedRate = 30_000)
    void pingAll() {
        for (Session s : sessions.all()) {
            if (s.missedPongs() >= MISSED_LIMIT) {
                // A TCP connection can stay open for hours with no traffic and no peer.
                // Without this, sessions accumulate and fan-out cost grows without bound.
                metrics.counter("ws.session.dropped", "reason", "no_pong");
                s.close(CloseCode.GOING_AWAY, "no pong");
                continue;
            }
            s.missedPongs().incrementAndGet();
            s.sendRaw(encode(OPCODE_PING, ByteBuffer.allocate(0), true));
        }
    }
}
```

Backpressure: a slow client must not be allowed to consume unbounded memory.

```java
class Session {
    // An outbound queue per session. A slow client gets its queue trimmed, NOT the
    // publisher blocked - one slow consumer must not stall a broadcast to everyone else.
    private final ArrayDeque<ByteBuffer> outbound = new ArrayDeque<>();
    private static final int MAX_QUEUED_BYTES = 256 * 1024;

    void enqueue(ByteBuffer frame) {
        int queuedBytes = outbound.stream().mapToInt(Buffer::remaining).sum();
        if (queuedBytes + frame.remaining() > MAX_QUEUED_BYTES) {
            // Policy for a chat: drop the OLDEST messages (they are stale anyway) and keep
            // the newest, so a reconnecting user sees current state rather than a backlog.
            while (queuedBytes + frame.remaining() > MAX_QUEUED_BYTES && !outbound.isEmpty()) {
                queuedBytes -= outbound.pollFirst().remaining();
                metrics.counter("ws.backpressure.dropped_oldest");
            }
        }
        outbound.add(frame);
        scheduleDrain();     // write only when the socket is actually writable
    }
}
```

Reconnection with a sequence cursor, so no message is lost or duplicated:

```java
@Component
class ReplayService {
    /** Bounded history per room. A cursor, not a timestamp: clients cannot be trusted to
     *  have a reliable clock, and a timestamp has resolution problems at the boundary. */
    private final Map<String, Deque<SequencedMessage>> history = new ConcurrentHashMap<>();

    List<SequencedMessage> since(String roomId, long lastSeq) {
        var h = history.getOrDefault(roomId, new ArrayDeque<>());
        return h.stream().filter(m -> m.seq() > lastSeq).toList();
    }

    public void publish(String roomId, OutboundMessage msg) {
        long seq = sequenceOf(roomId).incrementAndGet();
        var sequenced = new SequencedMessage(seq, Instant.now(), msg);
        history.computeIfAbsent(roomId, k -> new ArrayDeque<>()).addLast(sequenced);
        trimHistory(roomId);                                 // bound memory
        // Dedupe on the client: a client that already has seq 42 ignores a replayed 42.
        // Combined with the server cursor this is exactly-once from the user's perspective.
        hub.broadcast(roomId, sequenced);
    }
}
```

Client-side resume, and duplicate suppression:

```java
// Browser: reconnect with a cursor, dedupe by seq, and back off rather than hammering.
function connect() {
  const ws = new WebSocket(`wss://relay.example/ws?room=${room}&from=${lastSeq}`);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.seq <= lastSeq) return;            // already seen - a replay after reconnect
    lastSeq = msg.seq;
    render(msg);
  };
  ws.onclose = () => setTimeout(connect, backoff());   // exponential backoff with jitter
}
function backoff() { return Math.min(30000, 500 * 2 ** attempts++) + Math.random() * 500; }
```

### Test It

```java
@Test void acceptKeyMatchesSpecificationExample() {
    // RFC 6455's published example pair. If this fails, nothing else can be trusted.
    assertThat(WebSocketCodec.acceptKey("dGhlIHNhbXBsZSBub25jZQ=="))
        .isEqualTo("s3pPLMBiTxaQ9kYGzzhZRbK+xOo=");
}

@Test void clientFramesAreMaskedAndServerFramesAreNot() {
    assertThat(WebSocketCodec.encode(OPCODE_TEXT, payload("hi"), true).get(1) & 0x80).isEqualTo(0x80);
    assertThat(WebSocketCodec.encode(OPCODE_TEXT, payload("hi"), false).get(1) & 0x80).isZero();
}

@Test void deadPeerIsDroppedAfterTwoMissedPongs() {
    session.mockNoPongResponse();
    heartbeat.pingAll(); heartbeat.pingAll();
    assertThat(session.isOpen()).isFalse();
    assertThat(metrics.counter("ws.session.dropped", "reason", "no_pong").count()).isEqualTo(1);
}

@Test void slowClientDropsOldestNotNewest() {
    slowSession.fillOutboundQueue();
    slowSession.enqueue(encodeText("newest message"));
    assertThat(slowSession.deliveredFrames()).anyMatch(f -> f.contains("newest message"));
    assertThat(metrics.counter("ws.backpressure.dropped_oldest").count()).isGreaterThan(0);
}

@Test void reconnectReplaysExactlyOnce() {
    long cursor = client.lastSeq();
    publisher.publish(room, message("while disconnected"));
    client.disconnect();
    client.reconnect(cursor);
    assertThat(client.messages()).hasSize(1).anyMatch(m -> m.text().equals("while disconnected"));
    assertThat(client.duplicates()).isEmpty();
}
```

## Deliverables

- [ ] Handshake implementation with a `Sec-WebSocket-Accept` check against the RFC example
- [ ] Frame codec: opcodes, masking/unmasking, 7/16/64-bit lengths, fragmentation
- [ ] Ping/pong heartbeat with dead-peer detection and close-code handling
- [ ] Per-session outbound queue with a bounded size and an explicit drop policy
- [ ] Presence tracking with join/leave broadcast and stale-entry expiry
- [ ] Sequence-based replay cursor for reconnection, with client-side dedupe
- [ ] Authentication performed on the upgrade request, not in a WebSocket message
- [ ] Tests: accept key, masking, dead peer, backpressure policy, replay once
- [ ] An annotated frame-capture diagram in the README
