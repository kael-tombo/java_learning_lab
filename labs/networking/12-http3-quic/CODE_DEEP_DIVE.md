# HTTP/3 & QUIC - CODE DEEP DIVE

## 1. Header protection — a two-layer encryption that is easy to get wrong

QUIC encrypts the packet payload with the AEAD, then applies a **second** layer of
protection to the header. A naive implementation treats these as one step and produces a
server that fails on some packets and not others.

```java
final class HeaderProtector {
    /**
     * Two keys, from the same secret, sampled at different offsets. This is HPACK-style
     * key derivation: hpk = HKDF-Expand-Label(secret, "quic hp", "", keylen).
     * A single key for both layers is the classic bug: it works until it does not, and
     * the failure looks like random packet loss rather than a header error.
     */
    record HpKeys(byte[] packetNumberKey, byte[] headerKey) {
        static HpKeys derive(byte[] secret) {
            return new HpKeys(
                hkdfExpandLabel(secret, "quic hp", 0, 16),
                hkdfExpandLabel(secret, "quic ro", 0, 16));
        }
    }

    /**
     * The sample is taken from the ENCRYPTED payload, starting at pnOffset + 4, because
     * the packet number length is not yet known when the sample must be taken. The
     * reserved 4 bytes exist precisely to make this sampling position well-defined
     * regardless of the actual packet number length.
     */
    byte[] sampleForHeaderProtection(ByteBuffer packet, int pnOffset) {
        if (packet.remaining() < pnOffset + 4 + SAMPLE_LEN)
            throw new IllegalArgumentException("packet too small to sample");  // >= 1200 enforced upstream
        byte[] sample = new byte[SAMPLE_LEN];    // 16 bytes
        for (int i = 0; i < SAMPLE_LEN; i++) sample[i] = packet.get(pnOffset + 4 + i);
        return sample;
    }

    /**
     * First byte: mask the low 4 bits (reserved) and the top 2 bits of the packet number
     * length. Critically, the QUIC version and the fixed bit of a LONG header are NOT
     * protected - they must be readable for version negotiation.
     */
    void apply(byte[] firstByte, int packetNumberLen) {
        if ((firstByte[0] & 0x40) != 0) {                 // short header: protect pn len + reserved
            firstByte[0] ^= (byte) (aesEcb(hpKeys.headerKey(), sample)[0] & 0x0F);
        } else {                                           // long header: only reserved bits
            firstByte[0] ^= (byte) (aesEcb(hpKeys.headerKey(), sample)[0] & 0x0F);
        }
        for (int i = 0; i < packetNumberLen; i++)
            firstByte[1 + i] ^= aesEcb(hpKeys.headerKey(), sample)[1 + i];
    }
}
```

**Packet number encoding** is a space optimisation with a correctness requirement: the
length is chosen from the largest acknowledged packet number, and a receiver that
mis-decodes it desynchronises the whole stream.

```java
/**
 * Full packet numbers are 62-bit; only 1-4 bytes are on the wire. The length comes from
 * the expected next packet number relative to the largest ACKed. The rule: use the
 * smallest length that unambiguously represents (largestAcked + 1).
 */
int packetNumberLength(long largestAcked, long nextToSend) {
    long range = 2 * (largestAcked + 1);      // half the 2^len window, per RFC 9000 A.2
    if (nextToSend + range < 2 * 64)   return 1;   // 2^8
    if (nextToSend + range < 2 * 16384) return 2;   // 2^16
    if (nextToSend + range < 2 * 1_073_741_824L) return 3;  // 2^24
    return 4;                                        // 2^32
}
```

## 2. Per-stream reassembly — the exact place HOL blocking is eliminated

```java
final class StreamReassembler {
    // A TreeMap keyed by offset. A HashMap would be wrong: delivery MUST be in offset
    // order, and a TreeMap's firstKey() is the next contiguous byte position.
    private final NavigableMap<Long, byte[]> pending = new TreeMap<>();
    private long nextOffset;
    private long highestReceived;
    private final long maxStreamData;

    /**
     * Gap tracking is a first-class signal, not a side effect. Two reasons it matters:
     *  1. The sender needs to know WHICH ranges to retransmit (selective, not go-back-to).
     *  2. Flow control must be granted by HIGHEST offset, not by received byte count -
     *     a receiver that grants on received bytes stops granting when a gap opens,
     *     because "received" stops growing. That is a real deadlock in naive code.
     */
    void onFrame(long offset, byte[] data, boolean fin) {
        if (offset + data.length > maxStreamData) throw new FlowControlException(offset, data.length);
        pending.put(offset, data);
        highestReceived = Math.max(highestReceived, offset + data.length);
        if (fin) this.finEndOffset = offset + data.length;
        deliverContiguous();
    }

    private void deliverContiguous() {
        while (true) {
            var e = pending.pollFirstEntry();
            if (e == null) return;
            if (e.getKey() > nextOffset) {                 // gap: put it back, we cannot deliver
                pending.put(e.getKey(), e.getValue());
                metrics.gauge("stream.gap", 1);
                return;
            }
            if (e.getKey() + e.getValue().length <= nextOffset) continue;  // duplicate: drop
            // Partial overlap: trim the already-delivered prefix.
            int skip = (int) (nextOffset - e.getKey());
            onBytesDelivered(e.getValue(), skip, e.getValue().length - skip);
            nextOffset = e.getKey() + e.getValue().length;
        }
    }

    /** Ranges still missing. This is what makes retransmission selective rather than
     *  go-back-to, which is the second half of the HOL-blocking story. */
    List<ByteRange> missingRanges() {
        var missing = new ArrayList<ByteRange>();
        long cursor = nextOffset;
        for (var e : pending.entrySet()) {
            if (e.getKey() > cursor) missing.add(new ByteRange(cursor, e.getKey()));
            cursor = Math.max(cursor, e.getKey() + e.getValue().length);
        }
        if (finEndOffset > cursor) missing.add(new ByteRange(cursor, finEndOffset));
        return missing;
    }
}
```

## 3. Flow control credit — the deadlock waiting to happen

```java
final class FlowController {
    /**
     * The send side. `available` is granted credit MINUS bytes sent. Blocking here is
     * correct; the danger is a receiver that never grants.
     */
    long availableToSend() {
        return Math.max(0, sendLimit - sentTotal);
    }

    /**
     * The receive side. The subtle, load-bearing decision: credit is granted as data is
     * CONSUMED by the application, not as it is received off the wire.
     *
     * Why it matters: if credit were granted on receipt, a slow consumer would still be
     * flooded by the sender (the window never fills, because the buffer drains as fast as
     * the network delivers). Flow control's entire purpose is to throttle a sender that
     * is faster than the CONSUMER. Granting on receipt removes that.
     */
    void onApplicationConsumed(long bytesConsumed) {
        consumedTotal += bytesConsumed;
        if (consumedTotal - lastGrantReportedAt >= autoTuneThreshold) {
            // Auto-tuning: grow the window while the app keeps up. Bounded, or a fast
            // consumer on a fat link grows the window without limit.
            receiveLimit = Math.min(maxAllowedWindow,
                    initialWindow + (long) (consumedTotal * GROWTH_FACTOR));
            peer.sendMaxStreamData(streamId, receivedTotal + receiveLimit);
            lastGrantReportedAt = consumedTotal;
        }
    }

    /** Connection-level counterpart. A connection window can still stall every stream,
     *  so it must be set generously relative to the expected concurrent stream count. */
    void onConnectionConsumed(long bytes) {
        connectionConsumed += bytes;
        if (connectionConsumed - lastConnGrant > connectionWindow / 2)
            peer.sendMaxData(connectionConsumed + connectionWindow);
    }
}
```

**A reviewer should check** that `sendLimit` is only ever increased, never decreased —
a receiver that shrinks a window mid-connection violates the protocol and causes a
spurious `FLOW_CONTROL_ERROR` on the peer.

## 4. ACK handling — ranges, not a single number

```java
final class AckProcessor {
    /**
     * QUIC ACKs report RANGES of acknowledged packet numbers, not a single cumulative
     * number. This is what makes loss detection accurate under reordering: a receiver can
     * say "I got 100-120 except 107", so the sender retransmits 107 alone instead of
     * assuming everything after 100 is missing.
     */
    record AckRanges(List<long[]> ranges) {
        boolean isAcked(long pn) {
            return ranges.stream().anyMatch(r -> pn >= r[0] && pn <= r[1]);
        }
        long largestAcked() { return ranges.get(0)[1]; }      // ranges sorted descending
    }

    /**
     * ACK-only vs ack-eliciting. A packet that only carries ACK/FLOW_CONTROL frames does
     * NOT arm the PTO timer. If it did, a receiver that sends only such packets would
     * cause the sender to probe forever, which is a real bug seen in early QUIC stacks.
     */
    void onPacketReceived(boolean ackEliciting) {
        if (ackEliciting) ptoDeadline = null;   // outstanding ack-eliciting data: re-arm
    }

    /** Encryption level: handshake packets use one key epoch, 1-RTT another. An ACK for
     *  the wrong level is a protocol violation, and silently accepting it corrupts the
     *  loss-detection state. */
    void validateEncryptionLevel(EncryptionLevel expected, EncryptionLevel actual) {
        if (expected != actual) throw new ProtocolViolationException("ACK for wrong encryption level");
    }
}
```

## 5. Connection migration — demultiplexing by Connection ID

```java
final class ConnectionRegistry {
    private final Map<ConnectionId, QuicConnection> connections = new ConcurrentHashMap<>();
    private final Map<InetSocketAddress, ConnectionId> lastAddress = new ConcurrentHashMap<>();

    /**
     * Packets are demultiplexed by Connection ID, not by source address. The source
     * address is a HINT used only to pick a Connection ID space, because a client whose
     * address changed may not know which CID to send, and a server may have several.
     */
    Optional<QuicConnection> route(ByteBuffer packet, InetSocketAddress from) {
        ConnectionId cid = parseDestinationConnectionId(packet);
        var direct = connections.get(cid);
        if (direct != null) {
            InetSocketAddress previous = lastAddress.put(cid, from);
            if (!from.equals(previous)) direct.onAddressChange(from);   // not an error: expected
            return Optional.of(direct);
        }
        // Unknown CID: could be a NEW connection, a RETIRED one (server has a
        // replacement CID), or a stateless reset. The retry token is the safe reply
        // for a genuinely new connection, so an attacker cannot get amplification.
        return Optional.of(lastAddress.entrySet().stream()
                .filter(e -> e.getValue().equals(from))
                .findFirst()
                .map(e -> connections.get(e.getKey()))
                .orElse(null);
    }

    /**
     * Path validation. Migration is NOT instant: the client must prove the new path works
     * (PATH_CHALLENGE / PATH_RESPONSE) before sending real data on it. Skipping this lets
     * an off-path attacker hijack a connection by spoofing the client's address.
     */
    void onAddressChange(InetSocketAddress newAddress) {
        state = State.VALIDATING_PATH;
        sendPathChallenge(newAddress);
        // Until validated, only retransmissions of already-sent data are allowed on the
        // new path, and the congestion window is reset to the initial value.
        congestion.onPathChange(newAddress);
    }
}
```

## 6. Stateless reset — how a server sheds a QUIC connection cheaply

```java
/**
 * QUIC has no TCP RST. When a server must drop a connection it has lost state for, it
 * sends a STATELESS_RESET: a short, unparseable-looking packet whose last 16 bytes are an
 * HMAC over the connection ID. The client recognises it and closes cleanly.
 *
 * The flip side is a security consideration: a stateless reset lets ANY party that can
 * guess a connection ID and knows the reset key terminate a connection. So the reset key
 * must be per-connection and unpredictable, and the token must be authenticated - an
 * unauthenticated token would let an attacker forge resets and cause a denial of service.
 */
byte[] buildStatelessReset(ConnectionId cid, byte[] resetKey) {
    byte[] token = hmac(resetKey, cid.getBytes());     // 16 bytes, unpredictable without the key
    return concat(randomUnparseableBytes(), token);
}

boolean isStatelessReset(byte[] packet, ConnectionId cid, byte[] resetKey) {
    if (packet.length < RESET_TOKEN_LEN) return false;
    byte[] token = lastBytes(packet, RESET_TOKEN_LEN);
    return MessageDigest.isEqual(token, hmac(resetKey, cid.getBytes()));   // constant time
}
```

## 7. Testing QUIC code: what the test harness must fake

Testing a QUIC implementation without a network requires disciplined seams:

- **Virtual clock** for PTO, time thresholds, and idle timeouts. A test that sleeps is
  flaky and slow; a test with a `FakeClock` is deterministic.
- **Lossy channel** that drops, duplicates, and reorders packets on demand — a property
  test over random loss sequences finds reassembly bugs that a scripted test misses.
- **Packet decoder assertions** on the exact wire bytes, because a header bug is
  invisible to an API-level test.
- **Interop tests against a reference implementation**, since QUIC's on-wire format has
  many legal encodings (variable packet number length, both key phases) and a
  self-consistent implementation can be wrong in both directions.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 9000 Appendix A specifies the packet formats, header protection algorithm, and the
  packet number encoding rules implemented in §1.
  https://www.rfc-editor.org/info/rfc9000/
- RFC 9000 §4.1-4.5 specifies stream state, flow control frames, and the variable-length
  integer encoding used for all QUIC frame parameters.
  https://www.rfc-editor.org/info/rfc9000/
- RFC 9000 §10.3 specifies connection migration, path validation, and the NAT rebinding
  handling implemented in §5.
  https://www.rfc-editor.org/info/rfc9000/
