# VISION — Networking (Sockets → NIO → HttpClient)

## Vision Statement
**Network code is failure code** — timeouts, retries, and backpressure are the
feature. Build on `HttpClient`, NIO selectors, and virtual threads so I/O
scales without thread-per-connection collapse.

---

## Mental Models
### 1. Everything Blocks Until It Doesn't
Classic `Socket` I/O blocks a thread; NIO (`Selector/ByteBuffer`) multiplexes;
virtual threads make blocking code cheap again — pick one model per boundary.
### 2. Timeouts Are Mandatory
Connect, read, and request timeouts + deadlines bound tail latency. No
timeout = one slow peer parks your pool forever.
### 3. Retries Need Budgets
Idempotent GETs retry with jittered backoff; non-idempotent POSTs need keys.
Circuit breakers + bulkheads stop cascades; log trace IDs, not bodies.
### 4. Frames Beat Streams
Length-prefix or HTTP framing; partial reads are normal — loop on `read()`
until frame complete; TLS via `SSLContext`, never plaintext secrets.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Outbound REST? | `HttpClient` + explicit timeouts + retry budget |
| 10k connections? | NIO or virtual-thread-per-conn, never platform-thread-per-conn |
| Retry? | Only idempotent or keyed; exponential backoff + jitter |
| Custom protocol? | Length-prefixed frames + version byte |
| Prod debug? | `jcmd Thread.print` + JFR `jdk.SocketRead/Write` |

---

## Career Trajectory
- **L1:** Sockets, URL/URI, `HttpClient` sync calls, timeouts.
- **L2:** Async `HttpClient`, NIO channels/selectors, TLS setup.
- **L3:** Proxies, connection-pool tuning, breaker/retry architecture.
- **L4:** Edge architecture (gateway, mTLS mesh, load-shedding policy).

---

## 4-Week Path
```
W1: TCP/UDP sockets, HttpClient + timeouts, status/error mapping.
W2: Async client, CompletableFuture fan-out, retry with backoff.
W3: NIO echo server, ByteBuffer framing, virtual-thread server.
W4: Resilient fetch-service capstone (pool + breaker + JFR proof).
```
## Success Metrics
- [ ] Every call has connect+read timeout; retry budget documented
- [ ] 5k-conn test without thread exhaustion
- [ ] JFR shows socket waits, not thread starvation
