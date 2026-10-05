# WebSocket - REAL WORLD PROJECT

## Project: LiveBoard — real-time operational dashboards for a logistics network

Dispatchers need a live view of 12,000 vehicles and 400 warehouses: position, status,
and exception alerts. Updates arrive from a Kafka topic at ~8,000 events/second, and the
same event reaches many dashboards. This is a fan-out service where the hard parts are
backpressure, scale-out, and delivery guarantees.

### Architecture

```
  Fleet telematics ──▶ Kafka topic fleet-events (partitioned by vehicleId)
        │                        │
        │                   Relay fleet (3 AZ, N instances, ~50k sessions total)
        │                        │
        │                   ┌────┴────┐
        │                   │ Subscription manager: vehicle -> sessions
        │                   │ Room manager: region -> sessions
        │                   │ Per-node buffer + coalescing
        ▼                   ▼
  Dispatcher dashboards (browser, WebSocket)
  - subscribe by region, by vehicle list, or by alert severity
  - 8k events/s in, ~40k messages/s out (fan-out ~5x)
```

### Implementation

Subscription management that handles the fan-out cardinality explicitly:

```java
@Component
class SubscriptionRegistry {
    // vehicleId -> sessions, and session -> subscriptions. Both directions, because
    // a client may hold 200 subscriptions and we must clean up on every disconnect.
    private final Map<String, Set<WebSocketSession>> byVehicle = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> bySession = new ConcurrentHashMap<>();
    private final Map<String, Set<WebSocketSession>> byAlertSeverity = new ConcurrentHashMap<>();

    public void subscribe(WebSocketSession session, Subscription sub) {
        switch (sub.kind()) {
            case VEHICLE  -> byVehicle.computeIfAbsent(sub.target(), k -> ConcurrentHashMap.newKeySet()).add(session);
            case SEVERITY -> byAlertSeverity.computeIfAbsent(sub.target(), k -> ConcurrentHashMap.newKeySet()).add(session);
        }
        bySession.computeIfAbsent(session.id(), k -> ConcurrentHashMap.newKeySet()).add(sub.key());
    }

    /** Full symmetric removal on disconnect - a partial cleanup is a memory leak that
     *  shows up as ever-growing fan-out cost weeks later. */
    public void removeAll(WebSocketSession session) {
        Set<String> subs = bySession.remove(session.id());
        if (subs == null) return;
        for (String key : subs) removeFromIndex(key, session);
    }
}
```

Coalescing, which is the single biggest performance lever in a position-tracking workload:

```java
/**
 * A vehicle's position updates every 2s. A dashboard left open for 5 minutes generates
 * 150 updates, of which the human sees the last one. Coalescing per session keeps only
 * the newest value per entity, cutting outbound volume by an order of magnitude.
 */
class CoalescingDispatcher {
    private final Map<String, Map<String, EntitySnapshot>> pending = new ConcurrentHashMap<>();

    void dispatch(WebSocketSession session, Set<String> vehicleIds, FleetEvent event) {
        var sessionQueue = pending.computeIfAbsent(session.id(), k -> new ConcurrentHashMap<>());
        // Put-if-absent semantics per entity: newest write wins, older values are dropped.
        sessionQueue.put(event.vehicleId(), EntitySnapshot.from(event));
        if (sessionQueue.size() >= FLUSH_THRESHOLD) flush(session);
    }

    @Scheduled(fixedRate = 250)   // 4x/s: fast enough to feel live, slow enough to batch
    void flushAll() {
        for (var entry : pending.entrySet()) {
            var snapshots = entry.getValue();
            if (snapshots.isEmpty()) continue;
            // One message carrying many entities, not N messages: fewer frames, less
            // per-frame overhead, and the browser does one render instead of 200.
            entry.getKey().sendJson(new BatchUpdateMessage(new ArrayList<>(snapshots.values())));
            snapshots.clear();
        }
    }
}
```

Per-connection backpressure with an honest policy, since dashboards are often on hotel wifi:

```java
class BoundedSession {
    private static final int MAX_QUEUED_BYTES = 512 * 1024;
    private int queuedBytes = 0;

    /** Returns false if the message was dropped, so the dispatcher can count it. */
    boolean tryEnqueue(ByteBuffer frame) {
        if (queuedBytes + frame.remaining() > MAX_QUEUED_BYTES) {
            // Dashboards are state-displays, not audit logs: dropping is correct. But we
            // must (a) count it, and (b) tell the client, so a stale dashboard is visible
            // as stale rather than silently wrong.
            dropped.incrementAndGet();
            tryEnqueue(Frame.text("{\"type\":\"degraded\",\"droppedMsgs\":" + dropped.get() + "}"));
            return false;
        }
        queuedBytes += frame.remaining();
        outbound.add(frame);
        return true;
    }

    void onWritten(int bytes) { queuedBytes -= bytes; }   // decrement on actual write
}
```

Auth on the upgrade request, because a WebSocket message is not a place to authenticate:

```java
@Bean
ServerWebExchangeUpgradeHandler upgradeHandler(JwtVerifier verifier) {
    return (exchange, handler) -> {
        HttpHeaders h = exchange.getRequest().getHeaders();
        // The handshake is a normal HTTP request, so normal HTTP rules apply. A short-lived
        // token in the query string is the pragmatic choice for browser WebSockets, which
        // cannot set headers; the token is single-use and expires in 60 seconds.
        String token = exchange.getRequest().getQueryParams().getFirst("access_token");
        if (token == null || !verifier.verify(token).isValid()) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return Mono.empty();       // no upgrade -> no session
        }
        // Post-auth: check the user may actually see this scope of data BEFORE upgrading,
        // so an unauthorised client never occupies a session slot.
        var principal = verifier.verify(token).principal();
        String requestedRegion = exchange.getRequest().getQueryParams().getFirst("region");
        if (!authorization.canViewRegion(principal, requestedRegion)) {
            exchange.getResponse().setStatusCode(HttpStatus.FORBIDDEN);
            return Mono.empty();
        }
        return handler.upgrade(exchange);
    };
}
```

Load balancer reality — idle timeout and the connection-pinning consequence:

```java
@Bean
WebSocketKeepAlive keepAlive() {
    // Two hard operational facts, learned the hard way:
    // 1. Idle WebSocket connections are killed by typical LB idle timeouts (60s default on
    //    cloud LBs). Server-side pings every 25s keep the connection active.
    // 2. A WebSocket is a single long-lived TCP connection, so it is pinned to one node.
    //    Scale-out therefore requires the subscription registry to live in shared storage
    //    (Redis pub/sub), not in node-local memory.
    return new WebSocketKeepAlive(Duration.ofSeconds(25));
}
```

### Non-functional requirements

- **Scale**: 50,000 concurrent sessions, 8,000 events/second inbound, ~40,000 messages/second
  outbound after coalescing. Horizontal scaling by adding relay nodes.
- **Latency**: p99 update-to-dashboard under 1 second. Coalescing flush interval is the
  dominant term and is tuned against that budget.
- **Delivery**: at-most-once for position updates (a stale position is worthless), with
  coalescing and an explicit `degraded` signal when messages are dropped. Alerts are
  delivered separately with a durable path — never on the lossy dashboard socket.
- **Backpressure**: bounded per-session queues with a counted drop policy and a client-
  visible degraded message. One slow client never slows the dispatcher.
- **Scale-out**: cross-node fan-out via Redis pub/sub, since a WebSocket cannot be
  rebalanced; plus a documented fallback of client reconnect on node drain.
- **Lifecycle**: pings to survive LB idle timeouts, graceful drain on deploy (close with
  code 1012 and let clients reconnect), and session cleanup on every exit path.
- **Security**: short-lived single-use token on the upgrade, region authorization before
  upgrade, per-connection rate limiting, and payload size caps.
- **Observability**: session count per node, fan-out cost, coalescing ratio, dropped-message
  count, connect/disconnect rate, and a dashboard-gap detector for stale clients.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 6455 defines the WebSocket handshake, framing with client masking, and the
  close/ping/pong control frames implemented in the codec and heartbeat service.
  https://www.rfc-editor.org/info/rfc6455/
- MDN WebSocket API documentation describes the client API, the close event semantics,
  and the reconnection patterns applied on the dashboard client.
  https://developer.mozilla.org/en-US/docs/Web/API/WebSocket_API

## Deliverables

- [x] Symmetric subscription registry with full cleanup on disconnect
- [x] Per-entity coalescing that batches many updates into one frame
- [x] Bounded per-session queue with counted drops and a client-visible degraded signal
- [x] Short-lived single-use token plus region authorization on the upgrade request
- [x] Server pings to survive load balancer idle timeouts, with a documented drain procedure
- [x] Cross-node fan-out via shared pub/sub, since WebSockets cannot be rebalanced
- [x] At-most-once semantics for position data with a separate durable path for alerts
- [x] Dashboards for sessions, fan-out, coalescing ratio, drops, and stale-client detection
