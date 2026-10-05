# HTTP/3 & QUIC - MINI PROJECT

## Project: QuicPipe — a multiplexed QUIC-style transport with per-stream flow control

Implement a simplified QUIC-style protocol over UDP: connection handshake, multiple
independent streams, per-stream flow control, and a packet retransmission mechanism.
Demonstrate that a lossy stream does not stall a healthy one.

### Architecture

```
  Connection (single UDP 4-tuple, many streams)
  ┌──────────────────────────────────────────────────────────────┐
  │  Connection ID (8+ bytes): stable identity, not the 4-tuple   │
  │  Packet Number: per-connection, for loss detection & ordering  │
  │  Frames carried in packets:                                   │
  │    STREAM(stream_id, offset, data, fin)                       │
  │    CRYPTO(offset, handshake data)                             │
  │    MAX_STREAM_DATA(stream_id, limit)                          │
  │    ACK(packet ranges)                                         │
  │    RESET_STREAM(stream_id, error)                             │
  └──────────────┬───────────────────────────────────────────────┘
                 │  multiplexed
      ┌──────────┼──────────┬──────────┐
      ▼          ▼          ▼          ▼
   Stream 0   Stream 4   Stream 8   Stream 12
   (request)  (asset)    (upload)   (telemetry)
   each with independent:
     - ordering (by offset within stream)
     - flow control (per-stream MAX_STREAM_DATA credit)
     - completion (fin flag)

  Loss in Stream 4 does NOT block Stream 0/8/12: this is the whole point of QUIC.
```

### Implementation

The connection and stream multiplexing core, distinguishing per-connection and per-stream state:

```java
final class QuicConnection {
    private final long connectionId;
    private final AtomicLong nextPacketNumber = new AtomicLong();
    // Per-connection congestion state, but SEPARATE reassembly and flow control per stream.
    private final Map<Long, QuicStream> streams = new ConcurrentHashMap<>();
    private final CongestionController congestion = new RenoCongestionController();

    long registerStream() {
        long id = streams.size() * 4;            // client-initiated bidirectional ids: 0, 4, 8...
        streams.put(id, new QuicStream(id, InitialFlowControlWindow.DEFAULT));
        return id;
    }

    /**
     * Retransmission is per-packet, and a lost packet only retransmits its OWN frames.
     * Because each stream reassembles independently by offset, a lost packet on stream 4
     * creates a gap on stream 4 only - streams 0, 8, 12 continue delivering immediately.
     * This is the elimination of cross-stream head-of-line blocking.
     */
    void onPacketLost(long lostPacketNumber) {
        for (Frame f : sentFramesByPacket.remove(lostPacketNumber)) {
            switch (f.type()) {
                case STREAM -> {
                    QuicStream s = streams.get(f.streamId());
                    // Only the missing byte range is queued for retransmit. Retransmitting
                    // the whole stream (go-back-to-retransmit, as TCP must) would stall
                    // every byte after the gap, reintroducing exactly the HOL blocking QUIC removes.
                    s.enqueueForRetransmit(f.offset(), f.data());
                }
                case ACK  -> {}                     // losing an ACK costs a retransmit, not data
                default -> {}
            }
        }
    }
}
```

Per-stream flow control with explicit credit, which is a genuinely different model from TCP:

```java
final class QuicStream {
    private final long streamId;
    // Flow control is PER STREAM in QUIC, not just per connection. A receiver grants
    // credit per stream, so a fast bulk-transfer stream cannot consume the entire
    // connection window and starve a small latency-sensitive request stream.
    private volatile long sendWindowBytes;
    private volatile long recvWindowBytes;
    private long nextSendOffset;
    private final TreeMap<Long, byte[]> reassembly = new TreeMap<>();   // offset -> chunk
    private boolean finReceived;

    void onFrameReceived(Frame.StreamFrame frame) {
        reassembly.put(frame.offset(), frame.data());
        // Deliver contiguous bytes only. A gap means a later-offset chunk is BUFFERED,
        // not dropped and not delivered out of order - the same ordering guarantee as TCP,
        // but scoped to this stream only.
        deliverContiguous();
    }

    private void deliverContiguous() {
        while (!reassembly.isEmpty() && reassembly.firstKey() == nextSendOffset) {
            var entry = reassembly.pollFirstEntry();
            applicationBytes.add(concat(nextSendOffset, entry.getValue()));
            nextSendOffset += entry.getValue().length;
        }
        if (finReceived && nextSendOffset == finEndOffset) applicationCallbacks.onStreamComplete(streamId);
    }

    /**
     * SEND-side flow control: the sender may not transmit beyond the granted limit.
     * This is where a naive implementation deadlocks - if the receiver never grants
     * credit and the sender never sends, nothing progresses.
     */
    byte[] prepareSend(int maxBytes) {
        int allowed = (int) Math.min(maxBytes, sendWindowBytes - nextSendOffset);
        if (allowed <= 0) return EMPTY;             // blocked on credit; wait for MAX_STREAM_DATA
        return nextChunk(allowed);
    }

    /** The receiver grants more credit as it CONSUMES data, not as it receives it.
     *  Granting on receipt defeats the purpose: a slow consumer must throttle the sender. */
    void grantCredit() {
        recvWindowBytes = INITIAL_WINDOW + applicationBytes.consumed() * 2;   // autotuning
        peer.sendFrame(Frame.maxStreamData(streamId, nextSendOffset + recvWindowBytes));
    }
}
```

The packet builder, showing the header that replaces TCP + TLS:

```java
final class QuicPacketBuilder {
    /**
     * Short header (1 byte flags) is used after the handshake. Note what is ABSENT
     * versus TCP: no source/destination port, no sequence/ack numbers, no checksum
     * field, no window field. Those roles are filled by: the Connection ID (demux),
     * packet number (loss detection), AEAD tag (integrity - not just the header),
     * and flow control frames (the window).
     */
    ByteBuffer buildShortHeader(QuicConnection conn, List<Frame> frames) {
        // Header protection: packet number and reserved bits are encrypted, so a
        // middlebox cannot read or alter them. This prevents the ossification that
        // ossified TCP and stalled its evolution for a decade.
        long pn = conn.nextPacketNumber.getAndIncrement();
        int pnLen = packetNumberLength(pn);        // 1, 2, 3 or 4 bytes, based on the ACK range
        boolean shortHeader = true;
        boolean keyPhase = conn.currentKeyPhase();  // indicates current vs next encryption keys

        ByteBuffer buf = ByteBuffer.allocate(1200);   // QUIC requires >= 1200 bytes payload
        buf.put((byte) ((shortHeader ? 0x40 : 0x80) | (keyPhase ? 0x04 : 0) | (pnLen - 1)));
        buf.putLong(conn.connectionId());            // stable identity enables NAT rebinding + migration
        putPacketNumber(buf, pn, pnLen);
        int headerLen = buf.position();

        byte[] headerForAead = Arrays.copyOf(buf.array(), headerLen);
        byte[] payload = framesToBytes(frames);
        byte[] aad = headerForAead;                  // the AAD is the PROTECTED header
        byte[] ciphertext = conn.aeadEncrypt(aad, payload, pn);

        buf.position(headerLen);
        buf.put(ciphertext);
        buf.put(conn.aeadTag());                      // 16 bytes; covers both header and payload integrity
        return buf;
    }
}
```

Loss recovery, where QUIC's rules differ from TCP's:

```java
final class LossDetector {
    /**
     * QUIC uses a PACKET THRESHOLD (default 3), not a time threshold, to declare loss.
     * This is more robust than TCP's 3-duplicate-ACK heuristic because a QUIC sender
     * does not rely on the receiver's ACK behaviour the same way, and packet reordering
     * is more common with multipath/migration.
     */
    boolean isLost(long pn, AckState ack) {
        if (ack.largestAcked() - pn >= PACKET_THRESHOLD) return true;   // 3 newer acked
        long now = clock.now();
        if (ack.timeOfLargestAck() + kTimeThreshold(maxRtt, latestRtt) <= now) return true;
        return false;
    }

    /**
     * PTO (probe timeout) is the QUIC equivalent of TCP's RTO, but there are TWO of them,
     * because losing all ACKs is different from losing data:
     *   - PTO after sending new data
     *   - PTO after becoming PTO-eligible on an ack-eliciting packet
     * Without the distinction, a receiver that acks only non-ack-eliciting packets causes
     * a connection to probe constantly.
     */
    Duration pto() {
        Duration srtt = smoothedRtt();
        Duration rttvar = rttVariation();
        return srtt + max(4 * rttvar, GRANULARITY) + maxAckDelay;
    }
}
```

### Test It

```java
@Test void lossOnOneStreamDoesNotStallAnother() {
    var conn = clientConnection();
    long slowStream = conn.registerStream();
    long fastStream = conn.registerStream();

    conn.sendData(fastStream, "critical request");
    conn.sendData(slowStream, "bulk download chunk 1");
    conn.sendData(slowStream, "bulk download chunk 2");

    // Drop the packet carrying the slow stream's FIRST chunk (the lossy download).
    dropNextPacketContaining(slowStream);

    // The fast stream's data must still be delivered promptly.
    assertThat(receivedWithin(fastStream, Duration.ofMillis(50))).isTrue();
    // The slow stream is missing a gap, so it is incomplete - but only it.
    assertThat(receivedWithin(slowStream, Duration.ofMillis(50))).isFalse();
    assertThat(conn.hasGapIn(slowStream)).isTrue();
}

@Test void perStreamFlowControlPreventsOneStreamFromStarvingAnother() {
    var conn = clientConnection();
    long bulk = conn.registerStream();
    long req  = conn.registerStream();

    server.grantWindow(bulk, 1_000_000);        // bulk gets a huge window
    server.grantWindow(req, 16_384);            // request stream gets a small one
    conn.setSendWindow(bulk, 1_000_000);
    conn.setSendWindow(req, 16_384);

    // Bulk fills its window entirely. The request stream must STILL be able to send,
    // because flow control credit is per stream in QUIC (TCP would block the whole connection).
    conn.exhaustSendWindow(bulk);
    assertThat(conn.prepareSend(bulk, 64_000).length).isGreaterThan(0);   // bulk still blocked
    assertThat(conn.prepareSend(req, 64_000).length).isGreaterThan(0);    // request unaffected
}

@Test void reassemblyBuffersOutOfOrderDataUntilTheGapFills() {
    var s = newStream();
    s.onFrameReceived(frame(streamId: s.id(), offset: 10, data: "world"));
    assertThat(s.deliveredSoFar()).isEmpty();       // gap at offset 0: buffer, do not deliver
    s.onFrameReceived(frame(streamId: s.id(), offset: 0, data: "hello "));
    assertThat(s.deliveredSoFar()).isEqualTo("hello world");   // gap filled: deliver in order
}

@Test void connectionIdIsStableAcrossPortChange() {
    var conn = clientConnection();
    long cid = conn.connectionId();
    // Client's UDP source port changes (NAT rebinding). The connection must survive
    // because the server demultiplexes on Connection ID, not on the 4-tuple.
    clientChangeSourcePort();
    serverReceiveNextPacket();
    assertThat(server.connectionFor(cid)).isNotNull();
}

@Test void ptoIsLongerThanRttToAvoidSpuriousRetransmits() {
    var detector = lossDetectorWith(srtt: 50ms, rttvar: 10ms);
    assertThat(detector.pto()).isGreaterThanOrEqualTo(Duration.ofMillis(50 + 40));
}
```

## Deliverables

- [ ] Connection with Connection ID, per-connection packet numbering, and stream multiplexing
- [ ] Packet builder with short header, header protection, and AEAD over header + payload
- [ ] Per-stream flow control with MAX_STREAM_DATA credit granted on consumption
- [ ] Per-stream reassembly that buffers out-of-order data until gaps fill
- [ ] Packet-threshold loss detection and PTO calculation with ack-delay handling
- [ ] Connection ID enabling survival across a source port change (migration)
- [ ] A test proving loss on one stream does not stall another (the HOL-blocking test)
- [ ] A test proving per-stream flow control prevents cross-stream starvation
