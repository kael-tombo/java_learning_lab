# THEORY — gRPC Advanced (lab15)

## 1. HTTP/2 is the transport, protobuf the payload

Every gRPC call is HTTP/2 streams: HEADERS frame carries call metadata
(`:path: /package.Service/Method`, `content-type: application/grpc`,
authority), DATA frames carry length-prefixed messages (1-byte compressed
flag + 4-byte length + protobuf bytes), PING = keepalive, GOAWAY =
graceful drain, RST_STREAM = cancel. Multiplexing many RPCs over one TCP
connection is what makes 500K bids/s on few connections possible —
head-of-line blocking per stream, not per connection.

## 2. Channels, subchannels, and who picks

**Channel** = logical connection to a service name (resolved to addresses);
**subchannel** = TCP connection to one backend with state
(READY/IDLE/CONNECTING/TRANSIENT_FAILURE/SHUTDOWN) tracked by health
checks (`grpc.health.v1.Health/Check`). Load balancers (`pick_first`,
`round_robin`, `weighted_target`, xDS) choose among *ready* subchannels;
RPCs multiplex over the chosen one. Debugging starts here: channelz shows
subchannels, sockets, resolution — before tcpdump.

## 3. Interceptors = cross-cutting layer

Client side (auth injection, retry, timeout, logging) and server side
(auth validation, rate limiting, tracing extraction, request validation),
unary vs streaming variants, chained in order. Same architectural slot as
the API-gateway filters from `01-core-java/42` and servlet filters —
just inside the RPC stack.

## 4. Retries, hedging, deadlines

Service config: maxAttempts, backoff ×multiplier with jitter, retryable
codes (UNAVAILABLE, RESOURCE_EXHAUSTED, DEADLINE_EXCEEDED). **Hedging**:
send clones, take the first — trades bandwidth for tail latency.
**Deadlines propagate**: each hop gets `deadline − elapsed`; expiry
cancels the stream. Debugging ladder: status codes (UNAVAILABLE =
transport, RESOURCE_EXHAUSTED = congestion, DEADLINE_EXCEEDED = slow)
→ grpcurl/reflection/channelz → HTTP/2 frames (GOAWAY/RST/PING RTT,
100-stream default limit) → TCP/DNS/ALPN(h2).
