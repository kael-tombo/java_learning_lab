# THEORY: Microservices Architecture at Massive Scale
## Lab 06 | Production Engineering Academy

---

## 1. The Microservices Scale Dilemma

At modest scale (5–10 services, < 1,000 requests/sec), microservices communicate cleanly over basic REST/JSON via central load balancers. However, when an enterprise scales to 50–200+ services, 50,000+ requests/sec, and millions of daily active users, foundational network physics and protocol dynamics take over:

1. **Protocol Overhead (JSON vs Protobuf)**:
   - JSON is text-based, verbose, and requires expensive string parsing, serialization, and UTF-8 encoding.
   - Protobuf uses packed binary format with varints and field tags. Serialization/deserialization is 5x–10x faster with 60%–80% smaller wire size.
2. **Transport Layer (HTTP/1.1 vs HTTP/2 vs HTTP/3)**:
   - HTTP/1.1 suffers from Head-of-Line (HoL) blocking at the application layer: each TCP connection handles only one concurrent in-flight request.
   - HTTP/2 multiplexes hundreds of concurrent bi-directional streams over a single TCP connection, eliminating connection handshake latency.
   - HTTP/3 (QUIC over UDP) eliminates TCP-level HoL blocking across packet losses.
3. **Load Balancing Topologies**:
   - *Centralized L4/L7 Proxy*: Traffic flows `Client -> ALB/HAProxy -> Server`. Adds an extra network hop and proxy CPU bottleneck.
   - *Client-Side Load Balancing* (e.g., gRPC NameResolver, Envoy sidecar / Service Mesh): Client resolves endpoints and routes directly to the target pod, cutting latency by 50%.

```
Centralized Proxy:
[Pod A] ----(Hop 1)----> [Central Load Balancer] ----(Hop 2)----> [Pod B]
                        (Bottleneck & +2ms latency)

Client-Side / Service Mesh:
[Pod A + Envoy Sidecar] ----------------(Direct Hop)------------> [Pod B]
```

---

## 2. Load Balancing Algorithms at Scale

Standard Round-Robin fails under heterogeneous workload distribution (where some requests take 1ms and others take 500ms).

1. **Round Robin**: Distributes sequentially: $1, 2, 3, 1, 2, 3$. Fails when Pod 2 gets three slow queries in a row, causing thread starvation.
2. **Least Connections**: Sends requests to the instance with the fewest active requests. Better, but slow to react to sudden instance degradation.
3. **The Power of Two Random Choices (P2C) with Peak EWMA**:
   - Pick two backend instances at random.
   - Compare their moving average response latency (Exponentially Weighted Moving Average - Peak EWMA).
   - Route to the instance with lower latency.
   - Mathematically proven to avoid the "herding effect" while achieving near-optimal load distribution with $O(1)$ overhead.

---

## 3. Backpressure & Flow Control

When downstream consumers cannot keep pace with producers, buffers fill up. In Java systems, if flow control is missing, memory exhausts leading to OOM.

- **Reactive Streams Specification**:
  - `Publisher`, `Subscriber`, `Subscription`.
  - Subscriber explicitly signals demand via `subscription.request(n)`.
  - Publisher is forbidden from sending more than $n$ items until next demand signal.
- **gRPC Flow Control**:
  - Built-in HTTP/2 `WINDOW_UPDATE` frames manage flow control at both connection and stream levels.
  - Callers block or receive backpressure signals before memory balloons.
