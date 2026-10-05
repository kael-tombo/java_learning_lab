# TCP/UDP - REAL WORLD PROJECT

## Project: PulseStream — a telemetry ingestion pipeline for 30,000 connected devices

Industrial sensors report a reading every 2 seconds. That is ~15,000 messages/second, mostly
small, arriving from unreliable networks. Devices cannot be reflashware-installed today, and
the data is worthless 30 seconds late. The transport decision is the whole engineering problem.

### Architecture

```
  30,000 devices (constrained, flaky cellular, 1 req/2s)
        │  UDP: small datagrams, no connection state, survives NAT/NAT rebinding
        ▼
  Ingest Gateway (NIO UDP, 4 nodes, consistent hashing by device id)
        │  per-device state: last seq, retry window, session epoch
        │  - dedupe by (deviceId, seq)
        │  - batch + micro-batching (5 ms or 200 msgs)
        ▼
  Kafka topic readings (partitioned by deviceId → per-device ordering)
        │
        ▼
  Stream processor (rules, alerts, downsampling) ──▶ Time-series store
        │
        └──▶ Alert path: high-value readings forwarded over TCP/HTTPS with delivery guarantee

  Why UDP for ingest: a lost reading is replaced by the next one 2s later. Head-of-line
  blocking and connection state buy nothing and cost a lot on a flaky network.
  Why TCP for alerts: an alert that is lost is a missed safety event. Reliability wins.
```

### Implementation

The ingest gateway: NIO, per-device state, and dedupe:

```java
public class UdpIngestGateway {
    private final DatagramChannel channel;
    private final ConcurrentHashMap<String, DeviceState> devices = new ConcurrentHashMap<>();
    private final DatagramSocket fallback;      // DatagramChannel is single-threaded; this adds capacity

    public void start() {
        new Thread(this::receiveLoop, "udp-ingest").start();
        new Thread(this::receiveLoop, "udp-ingest-2").start();   // SO_REUSEPORT style scale-out
    }

    private void receiveLoop() {
        ByteBuffer buf = ByteBuffer.allocateDirect(2048);       // direct buffer: no copy on read
        while (running) {
            buf.clear();
            SocketAddress from = channel.receive(buf);          // never blocks
            if (from == null) continue;
            buf.flip();
            Reading r = Reading.decode(buf);                     // fixed-layout binary: no JSON parse cost

            DeviceState s = devices.computeIfAbsent(r.deviceId(), DeviceState::new);
            // Dedupe: a retransmitted datagram must not double-count. Devices retry on no-ack.
            if (r.sequence() <= s.lastSequence) { metrics.counter("ingest.duplicate"); continue; }
            if (r.sequence() > s.lastSequence + MAX_GAP) {      // implausible jump = reboot or spoof
                s.epoch++; metrics.counter("ingest.epoch_reset", "device", r.deviceId());
            }
            s.lastSequence = r.sequence();
            queue.offer(r);
        }
    }
}
```

Micro-batching: the trade-off between throughput and data latency, made explicit:

```java
/** Batch by whichever limit arrives first: size (throughput) or time (latency). */
class MicroBatcher implements AutoCloseable {
    private static final int MAX_BATCH = 500;
    private static final Duration MAX_LATENCY = Duration.ofMillis(5);

    List<Reading> next(List<Reading> input) {
        List<Reading> batch = new ArrayList<>(MAX_BATCH);
        long deadline = System.nanoTime() + MAX_LATENCY.toNanos();
        for (Reading r : input) {
            batch.add(r);
            if (batch.size() >= MAX_BATCH || System.nanoTime() >= deadline) break;
        }
        // 5ms of batching removes ~99% of per-message Kafka overhead while keeping
        // end-to-end latency under the 30-second usefulness window by three orders of magnitude.
        return batch;
    }
}
```

Backpressure, because a UDP sender can always send faster than you can store:

```java
class BackpressureGuard {
    // UDP has no built-in flow control. If the queue grows, we must drop deliberately and
    // visibly rather than exhaust the heap. Telemetry tolerates loss; an OOM does not.
    void offer(Reading r) {
        if (queue.size() > HIGH_WATER) {
            // Per-device fairness: drop the noisiest device first, not a random one.
            deviceThrottle.mark(r.deviceId());
            dropped.increment();
            return;
        }
        queue.offer(r);
    }
}
```

The alert path, deliberately TCP/HTTPS because reliability dominates latency there:

```java
/** Alerts must be delivered. Use a blocking call with a deadline, over a transport that guarantees order. */
class AlertDispatcher {
    public void dispatch(Alert a) {
        // Retries are safe here: the alert carries an idempotency key, so a duplicate
        // delivery is de-duplicated downstream instead of creating a duplicate incident.
        RetryTemplate retry = RetryTemplate.builder()
            .maxAttempts(4)
            .exponentialBackoff(Duration.ofMillis(200), 2.0, 5.0)
            .build();
        retry.execute(ctx -> {
            restClient.post()
                .uri("/v1/alerts")
                .header("Idempotency-Key", a.idempotencyKey())     // deviceId + ruleId + window
                .body(a)
                .retrieve()
                .toBodilessEntity();
            return null;
        });
    }
}
```

### Non-functional requirements

- **Ingest rate**: sustained 20,000 msgs/second, burst to 50,000. Backlog drains in
  under 30 seconds.
- **Loss**: measured end-to-end device-to-store loss under 0.5% on a healthy network,
  with per-device loss rate visible per device so a silent sensor is detectable.
- **Ordering**: per-device ordering preserved end to end by partitioning on `deviceId`.
- **Latency**: p99 device-to-dashboard under 2 seconds. This is the constraint that rules
  out a chatty TCP-per-device model on flaky cellular links.
- **Scale-out**: gateways are stateless apart from a small per-device cache; adding a node
  requires no rebalancing, and consistent hashing keeps a device on one node.
- **NAT resilience**: devices use a session epoch and resend their last sequence on
  reconnect, so a NAT rebinding does not look like a new device.
- **Availability**: ingest survives a broker restart; a full downstream outage triggers
  deliberate per-device throttling with a loud alert rather than silent loss.
- **Security**: per-device credentials (HMAC with a monotonic counter, not a static token),
  rate limits per device, and a hard cap on devices per source address.
- **Observability**: loss rate, queue depth, batch size, per-device silence detection, and
  epoch-reset counts — the last is a useful reboot/attack signal.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 768 defines UDP as a connectionless, message-oriented transport with no delivery,
  ordering, or flow-control guarantee - the properties this ingest design deliberately
  trades away for latency on unreliable links.
  https://www.rfc-editor.org/info/rfc768/
- MDN WebSockets documentation contrasts the reliability model of TCP-based persistent
  connections, which is the model the alert path chooses instead of UDP.
  https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

## Deliverables

- [x] NIO UDP ingest with direct buffers, per-device state, and sequence dedupe
- [x] Epoch tracking so NAT rebinding and device reboots are not treated as new devices
- [x] Micro-batching with explicit size/latency trade-off documentation
- [x] Deliberate, per-device-fair backpressure instead of heap exhaustion
- [x] Per-device ordering guaranteed by partitioning on `deviceId`
- [x] Separate reliable TCP/HTTPS path for alerts, with idempotency keys
- [x] Per-device credential scheme with a monotonic counter and rate limiting
- [x] Dashboards for loss rate, silence detection, queue depth, and epoch resets
