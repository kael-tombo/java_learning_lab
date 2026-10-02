# EXERCISES — gRPC Advanced

## 1. Frame anatomy (beginner)
Capture one unary call (grpcurl or test client + tcpdump/Wireshark).
Label HEADERS (:path, content-type, authority), the 5-byte envelope
(flag + length), and the protobuf payload. Flip the compressed flag bit
by hand — what breaks, and where?

## 2. Channel states (beginner)
Bring a backend up/down during a streaming call. Record subchannel states
(channelz) through IDLE→CONNECTING→READY→TRANSIENT_FAILURE→READY.
Which RPCs fail vs transparently retry, and under which codes?

## 3. Interceptor chain (intermediate)
Implement logging → auth → rate-limit interceptors (either side).
Reorder auth after rate limiting; show rejected calls now emit traces.
Argue the correct order for your org's audit requirements.

## 4. Retry arithmetic (intermediate)
Configure maxAttempts=3, backoff 100 ms ×2, retry on UNAVAILABL
30%-flaky backend. Predict expected attempts (1/(1−p)) and added latency;
measure over 1,000 calls. Then add a 200 ms deadline and show retries
starving — the misconfiguration from MATH_FOUNDATION §2.

## 5. Bidding sketch (advanced)
Size the Q7 pipeline: connection pool, pre-warm count, per-stream
deadlines, keepalive interval, flow-control windows, custom balancer
metric. Then inject 5% packet loss and show which knob (hedging?
window? balancer?) recovers p99 first, with numbers.
