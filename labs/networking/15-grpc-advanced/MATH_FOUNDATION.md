# MATH_FOUNDATION — gRPC

## 1. Multiplexing gain

N concurrent RPCs over 1 TCP connection vs N connections: handshake cost
(TLS ~2 RTT + SETTINGS) paid once, not N times; congestion window shared
and warm. Per-stream head-of-line blocking replaces per-connection
blocking — one slow stream stalls itself, not the connection (unlike
HTTP/1.1 pipelining).

## 2. Deadline budgeting

End-to-end deadline D, hops h₁…hₖ with budgets dᵢ, Σdᵢ ≤ D. Each hop sees
`remaining = D − elapsed`; a hop exceeding its share cancels downstream
work (no wasted compute past expiry). Retry math: expected attempts ≈
1/(1−p) for per-try failure p (p=0.1 → ~1.11 attempts); with backoff
b·2ⁿ + jitter, worst-case added latency ≈ Σ backoffs < remaining deadline
or the retry never fires — the standard "retries configured but never
observed" mystery.

## 3. Stream limits

Default max 100 concurrent streams/connection: the 101st RPC queues
(client-side) — latency cliff misdiagnosed as server slowness. Fix:
raise `MAX_CONCURRENT_STREAMS`, pool connections, or shed. Same shape as
partition-bound consumer scaling (lab14): count the lanes before blaming
the workers.
