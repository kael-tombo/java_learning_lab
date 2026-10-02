# CODE_DEEP_DIVE — gRPC mock (lab15)

All references are to `MOCK_INTERVIEW.md` in this lab (Q1–Q8).

## 1. Q1 — Frames (lines 5–7)

The 5-byte gRPC envelope (compressed-flag + length) inside HTTP/2 DATA is
the detail interviewers probe: it explains message boundaries on a byte
stream, why compression is per-message, and what a frame parser (or
tcpdump decode) shows. HEADERS metadata vs DATA payload separation is why
auth/tracing interceptors never touch message bytes.

## 2. Q2 — Channels (lines 9–11)

Channel (name→addresses) vs subchannel (one TCP, one state machine).
Health protocol keeps READY sets honest; reuse means N RPCs share one
handshake (TLS + HTTP/2 SETTINGS amortized). `pick_first` = sticky
failover; `round_robin` = spread. Wrong choice shows up as hot backends
under `pick_first` with uneven streams.

## 3. Q3 — Interceptors (lines 13–15)

Unary vs stream variants exist because streaming calls need per-message
hooks, not just per-call. Chain order is the contract (auth before rate
limit before tracing, or the traces record rejected calls — sometimes
wanted, usually not).

## 4. Q4–Q5 — Balancing + retries (lines 19–25)

xDS (LRS/CDS/EDS/RDS/LDS) moves routing policy out of code into control
plane: splitting, outlier ejection, locality weights. Retry config is
arithmetic: attempts × backoff × jitter against deadline; hedging adds
load (clones) to buy tails — only valid for idempotent methods.

## 5. Q6–Q8 — Fit + design + debug (lines 27–38)

- gRPC-inside/REST-outside (via grpc-gateway) is the standard hybrid.
- 500K-bid design: bidi streaming + pooled pre-warmed channels + 50 ms
  propagated deadlines (ignore expiries) + keepalive + flow control +
  CPU-aware custom balancing. Every element answers the 50 ms budget.
- Debug order is load-bearing: codes → grpcurl/channelz → frames →
  network. Jumping to tcpdump first wastes the hour channelz would save.
