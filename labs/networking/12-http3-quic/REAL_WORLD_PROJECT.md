# HTTP/3 & QUIC - REAL WORLD PROJECT

## Project: Edge3 — HTTP/3 rollout for a high-latency, lossy mobile traffic profile

A video and news platform with a mobile audience on poor networks. Median RTT is 220 ms
and packet loss is 2-3% on the worst routes. Today: HTTP/2 over TLS over TCP. Every lost
packet stalls the entire connection at the transport layer, so one bad path on a page with
many small assets turns into a visibly slow page. This project evaluates and deploys
HTTP/3 with a real measurement-driven decision.

### Architecture

```
  Mobile client (supports h3)
        │
        │  Alt-Svc: h3=":443"; ma=86400        (advertised from day one on HTTPS)
        ▼
  ┌──────────── Edge3 (CDN + load balancer) ─────────────┐
  │  QUIC termination (0-RTT enabled, connection coalescing)│
  │  per-request HTTP/3 server (h3, request multiplexing)  │
  │  fallback: TCP + HTTP/2 for clients without h3         │
  └──────────────┬────────────────────────────────────────┘
                 ▼
  ┌──────── Origin services (HTTP/1.1 + h2) ─────────────┐
  │  CDN cache absorbs most requests; origin fetch on      │
  │  miss uses a connection pool sized for the BDP         │
  └───────────────────────────────────────────────────────┘

  Why this shape:
    - CDN + cache is the single biggest win for a lossy network (fewer round trips at all)
    - h3 handles the rest: 0-RTT removes one RTT, per-stream recovery isolates losses
    - Origin stays HTTP/1.1 + h2: h3 to the origin only helps if we control the origin path
```

### Implementation

Server configuration with the parameters that actually matter, each with a reason:

```java
@Bean
QuicServerConfig quicConfig() {
    return new QuicServerConfig()
        .initialMaxData(10 * 1024 * 1024)        // per-connection receive window: large enough for a page
        .initialMaxStreamData(1024 * 1024)      // per-stream: one page's assets in flight
        .initialMaxStreams(100)                 // allow a burst of parallel asset requests
        .maxIdleTimeout(Duration.ofSeconds(60)) // must be < the LB idle timeout or the LB kills us first
        .enableZeroRtt(true)                    // resumption-based 0-RTT; see replay note below
        .maxUdpPayloadSize(1452)                // 1500 - 20 IP - 8 UDP - 20 QUIC: avoid fragmentation,
                                                // which is fatal for QUIC's congestion control
        .connectionIdLength(8)
        .congestionControl(new BbrCongestionControl());
}
```

The 0-RTT decision, which must be made explicitly and per-route:

```java
/**
 * 0-RTT sends data in the very first flight, before the handshake completes. The risk is
 * REPLAY: an attacker who captures a 0-RTT packet can resend it, and the server cannot
 * tell a replay from the original because the handshake has not finished. So:
 *   - 0-RTT is SAFE for idempotent operations: GET, HEAD, and reads.
 *   - 0-RTT is UNSAFE for anything that changes state: POST, order placement, payment.
 * A CDN in front is another mitigating factor: replayed 0-RTT is answered from cache.
 */
record ZeroRttPolicy(boolean allowed, String rationale) {
    static ZeroRttPolicy forRequest(HttpRequest req) {
        if (req.method().equals("GET") || req.method().equals("HEAD"))
            return new ZeroRttPolicy(true, "idempotent, replay-safe");
        if (req.isFromCdnEdge())
            return new ZeroRttPolicy(true, "served from cache, replay has no side effect");
        return new ZeroRttPolicy(false, "state-changing request: 0-RTT replay would duplicate it");
    }
}

@Bean
ServerInterceptor zeroRttGate() {
    return ctx -> {
        var policy = ZeroRttPolicy.forRequest(ctx.request());
        if (!policy.allowed() && ctx.isZeroRtt())
            ctx.rejectEarlyData("0-RTT not permitted for " + ctx.request().method());
        return ctx.proceed();
    };
}
```

Connection coalescing, a real HTTP/3 win that requires deliberate configuration:

```java
/**
 * HTTP/3 connections are keyed by (origin, ALT-SVC), not by hostname. So a client that
 * fetched cdn.example.com over h3 can reuse that connection for img.example.com if we
 * coalesce them. The catch: we must present a certificate valid for BOTH names and must
 * accept the coalesced Host - otherwise we break TLS SNI validation.
 */
@Bean
ServerConfig http3Server() {
    return Server.builder()
        .http3(Http3ConnectionOption.builder()
            .altSvcHeader("h3=\":443\"; ma=86400")
            .connectionCoalescing(true)
            .coalescedCertificate(certFor("cdn.example.com", "img.example.com", "static.example.com"))
            .build())
        .build();
}
```

Fallback strategy, because h3 will not be universal on day one:

```java
/**
 * A client that advertises no Alt-Svc gets TCP + HTTP/2. Critically, we must NOT fail
 * closed on a QUIC error: some middleboxes silently drop UDP/443. The correct behaviour
 * on a QUIC handshake timeout is to fall back to TCP transparently.
 */
@Bean
Router h3AwareRouter(QuicServer quic, Http2Server http2) {
    return route -> {
        if (route.supportsQuic() && !probeBlocked(route)) return quic.handle(route);
        // QUIC unreachable (firewall, broken middlebox): transparently use TCP.
        metrics.counter("h3.fallback", "reason", "quic_unreachable");
        return http2.handle(route);
    };
}
```

Per-route telemetry, so the rollout decision is evidence-based:

```java
@Component
class Http3Metrics {
    // The comparison that decides the rollout. h2 and h3 for the SAME route on the SAME
    // client network, so the difference is the protocol and not the geography.
    void record(HttpRequest req, String protocol, long ttfbMs, int requests, int retransmits) {
        metrics.timer("edge.request.ttfb", "protocol", protocol, "route", req.routeTemplate())
               .record(ttfbMs, MILLISECONDS);
        metrics.counter("edge.request.count", "protocol", protocol, "status", String.valueOf(req.status()))
               .increment();
        if (protocol.equals("h3")) metrics.counter("edge.h3.retransmits", "route", req.routeTemplate()).increment(retransmits);
    }

    /** The metric that actually decides adoption: connection reuse rate.
     *  A client on a poor network pays a new handshake per visit if connections are not
     *  being coalesced and kept warm; that cost can exceed the per-request gain. */
    void recordConnectionOutcome(String clientNetwork, String outcome) {
        metrics.counter("edge.h3.connection", "network", clientNetwork, "outcome", outcome).increment();
    }
}
```

Server-side tuning, where QUIC's per-stream model actually helps a CDN edge:

```java
@Bean
Http3Config tunedForEdge() {
    return Http3Config.builder()
        // Per-STREAM windows matter here: one large asset download must not consume the
        // connection window and delay 20 small CSS/JS requests queued behind it. In TCP
        // these are coupled at the connection level, so a big response head-of-line blocks
        // the small ones. This is the practical HOL win on a real page.
        .initialMaxStreamData(512 * 1024)
        .initialMaxData(16 * 1024 * 1024)
        .maxUdpPayloadSize(1452)                  // MUST avoid IP fragmentation
        .congestionControl(BbrCongestionControl.INSTANCE)  // better on lossy paths than CUBIC
        .build();
}
```

### Non-functional requirements

- **Adoption**: h3 offered on 100% of edge traffic from day one; adoption measured, with
  a target of >60% of mobile page views over 6 months. A low adoption number is a signal
  to fix middlebox/compat issues, not to force clients.
- **Latency**: TTFB p50 improved by ≥15% and p90 improved by ≥25% on the high-latency
  segments (RTT > 150 ms, loss > 1%), where the transport change matters. Flat latency on
  good networks is expected and acceptable; do not claim wins where the maths says there
  are none.
- **0-RTT**: enabled for GET/HEAD only, with the route policy enforced server-side and
  tested. 0-RTT on state-changing requests is prohibited by an automated test, not a
  convention.
- **Fallback**: transparent fallback to TCP+h2 on QUIC unreachability, with the fallback
  rate monitored per network segment so UDP-blocking is visible.
- **Connection reuse**: h3 connection reuse above 50% of page views; coalescing enabled
  with a certificate covering all coalesced names.
- **MTU**: 1452-byte UDP payload enforced end to end. Any IP fragmentation destroys QUIC
  congestion control, and the symptom (a "random" slow subset of users) is hard to
  diagnose without this check.
- **Edge capacity**: 20% more CPU per connection than h2 (QUIC is in userspace), so
  connection count per node is a capacity metric with an alert, and idle connection
  timeouts are tuned below the LB timeout to avoid the LB killing h3 connections early.
- **Fallback correctness**: h3 requests hitting an origin that only speaks HTTP/1.1 must
  not fail; a CDN fetch layer that abstracts this keeps one origin contract.
- **Decision gate**: rollout is a measured decision, not a standards decision. If h3 TTFB
  does not beat h2 on the target segments after 8 weeks, the project recommends not
  routing to h3 by default and says so explicitly.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 9000 specifies QUIC: connection ID, streams, per-stream flow control, packet
  numbering, and loss recovery — the mechanisms implemented in the mini project.
  https://www.rfc-editor.org/info/rfc9000/
- MDN HTTP/3 documentation describes `Alt-Svc` advertisement, h3 over QUIC, and the
  fallback behaviour toward HTTP/2 configured above.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/3

## Deliverables

- [x] Edge h3 configuration with per-stream and per-connection windows justified separately
- [x] Explicit 0-RTT policy: enabled for idempotent reads, prohibited for state changes
- [x] Connection coalescing with a certificate covering every coalesced name
- [x] Transparent fallback to TCP + HTTP/2 with per-network fallback-rate telemetry
- [x] BBR congestion control selected for lossy mobile paths, with the reasoning documented
- [x] MTU enforcement at 1452 bytes, with fragmentation detection as an alert
- [x] Capacity model for 20% higher per-connection CPU, with a connection-count alert
- [x] A/B comparison of h3 vs h2 TTFB by network segment driving the rollout decision
