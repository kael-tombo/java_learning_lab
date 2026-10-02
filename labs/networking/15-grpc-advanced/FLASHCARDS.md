# FLASHCARDS — gRPC Advanced

| # | Front | Back |
|---|-------|------|
| 1 | Wire envelope? | 1-byte flag + 4-byte length + protobuf, in HTTP/2 DATA. |
| 2 | HEADERS carry? | Path, authority, content-type: application/grpc (metadata, not bytes). |
| 3 | PING / GOAWAY / RST? | Keepalive / graceful drain / stream cancel. |
| 4 | Channel vs subchannel? | Logical service link vs one TCP + state machine. |
| 5 | Health protocol? | grpc.health.v1.Health/Check → READY set. |
| 6 | pick_first vs round_robin? | Sticky failover vs spread across ready. |
| 7 | xDS five APIs? | LRS, CDS, EDS, RDS, LDS — routing as control-plane config. |
| 8 | Retry tuple? | Attempts × backoff × jitter × retryable codes. |
| 9 | Hedging cost? | Bandwidth for tails; idempotent methods only. |
| 10 | Deadline math? | Per-hop budget = D − elapsed; expiry cancels. |
| 11 | 100-stream cliff? | Default cap — 101st queues client-side. |
| 12 | Status triage? | UNAVAILABLE transport / EXHAUSTED congestion / DEADLINE slow. |
| 13 | channelz shows? | Subchannels, sockets, resolution — before tcpdump. |
| 14 | Hybrid pattern? | gRPC inside, REST outside via gateway. |
| 15 | Interceptor slots? | Client out / server in; unary vs streaming variants. |
