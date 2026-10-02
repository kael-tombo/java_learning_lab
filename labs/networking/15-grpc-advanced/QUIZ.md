# QUIZ — gRPC Advanced

## 1. gRPC message on the wire: exact bytes?
<details><summary>Answer</summary>5-byte envelope (1 compressed flag + 4 length) + protobuf payload, inside HTTP/2 DATA frames; call metadata in HEADERS.</details>

## 2. Channel vs subchannel?
<details><summary>Answer</summary>Channel: logical service connection (name→addresses). Subchannel: one TCP to one backend with a state machine.</details>

## 3. Subchannel states?
<details><summary>Answer</summary>IDLE, CONNECTING, READY, TRANSIENT_FAILURE, SHUTDOWN — tracked via health checks.</details>

## 4. Interceptor chain order significance?
<details><summary>Answer</summary>Outer runs first (auth before rate-limit before tracing, or traces include rejected calls). Order is the contract.</details>

## 5. Hedging vs retrying?
<details><summary>Answer</summary>Retry: sequential re-attempts on failure. Hedging: parallel clones, first wins — buys tail latency with bandwidth, idempotent-only.</details>

## 6. Deadline propagation in one line?
<details><summary>Answer</summary>Each hop gets deadline−elapsed; expiry cancels the stream — no compute past the budget.</details>

## 7. Retryable codes?
<details><summary>Answer</summary>UNAVAILABLE, RESOURCE_EXHAUSTED, DEADLINE_EXCEEDED — configured with attempts/backoff/jitter.</details>

## 8. gRPC-inside/REST-outside: why the hybrid?
<details><summary>Answer</summary>Throughput/typing/streaming internally; browser-friendly caching/simplicity externally (grpc-gateway bridges).</details>

## 9. 101st concurrent stream symptom?
<details><summary>Answer</summary>Client-side queueing at the 100-stream default — latency cliff misread as server slowness.</details>

## 10. Debug order for latency + errors?
<details><summary>Answer</summary>Codes → grpcurl/reflection/channelz → HTTP/2 frames (GOAWAY/RST/PING) → TCP/DNS/ALPN. Never tcpdump first.</details>
