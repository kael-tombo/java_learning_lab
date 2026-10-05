# Real-World Project — Deep Java Networking (networking-deep)

Production-style build around sockets, NIO/NIO.2, Netty, HTTP client, gRPC: design, scale, operate.

## Problem statement
Design a service/demo where TCP/UDP sockets, NIO selectors & channels, NIO.2 async channels are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `TCP/UDP sockets` → component + owner + SLO.
- `NIO selectors & channels` → component + owner + SLO.
- `NIO.2 async channels` → component + owner + SLO.
- `Netty pipeline` → component + owner + SLO.
- `Java HttpClient` → component + owner + SLO.

## Milestones (4)
1. Slice: happy path + test.
2. Harden: timeouts, retries, validation.
3. Observe: logs/metrics/JFR + dashboard.
4. Scale: benchmark + tune one bottleneck.

## Ops checklist
- [ ] Dockerfile + health check
- [ ] Load test (k6/JMeter) with p99
- [ ] Runbook: top-3 failures + mitigations

## Interview story
Prepare STAR: problem → approach → metric → lesson.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/channels/package-summary.html
- https://docs.oracle.com/en/java/javase/17/docs/api/java.net.http/java/net/http/package-summary.html
- https://openjdk.org/jeps/444 (virtual threads)

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale TCP/UDP sockets under load.
Extension 1: scale NIO selectors & channels under load.
Extension 2: scale NIO.2 async channels under load.
Extension 3: scale Netty pipeline under load.
Extension 4: scale Java HttpClient under load.
Extension 5: scale WebSocket under load.
Extension 6: scale gRPC stubs under load.
Extension 7: scale backpressure over network under load.
Extension 8: scale TCP/UDP sockets under load.
Extension 9: scale NIO selectors & channels under load.
Extension 10: scale NIO.2 async channels under load.
Extension 11: scale Netty pipeline under load.
Extension 12: scale Java HttpClient under load.
Extension 13: scale WebSocket under load.
Extension 14: scale gRPC stubs under load.
Extension 15: scale backpressure over network under load.
Extension 16: scale TCP/UDP sockets under load.
Extension 17: scale NIO selectors & channels under load.
Extension 18: scale NIO.2 async channels under load.
Extension 19: scale Netty pipeline under load.
Extension 20: scale Java HttpClient under load.
Extension 21: scale WebSocket under load.
Extension 22: scale gRPC stubs under load.
Extension 23: scale backpressure over network under load.
Extension 24: scale TCP/UDP sockets under load.
Extension 25: scale NIO selectors & channels under load.
Extension 26: scale NIO.2 async channels under load.
Extension 27: scale Netty pipeline under load.
Extension 28: scale Java HttpClient under load.
Extension 29: scale WebSocket under load.
Extension 30: scale gRPC stubs under load.
Extension 31: scale backpressure over network under load.
Extension 32: scale TCP/UDP sockets under load.
Extension 33: scale NIO selectors & channels under load.
Extension 34: scale NIO.2 async channels under load.
Extension 35: scale Netty pipeline under load.
Extension 36: scale Java HttpClient under load.
Extension 37: scale WebSocket under load.
Extension 38: scale gRPC stubs under load.
Extension 39: scale backpressure over network under load.
Extension 40: scale TCP/UDP sockets under load.
Extension 41: scale NIO selectors & channels under load.
Extension 42: scale NIO.2 async channels under load.
Extension 43: scale Netty pipeline under load.
Extension 44: scale Java HttpClient under load.
Extension 45: scale WebSocket under load.
Extension 46: scale gRPC stubs under load.
Extension 47: scale backpressure over network under load.
Extension 48: scale TCP/UDP sockets under load.
Extension 49: scale NIO selectors & channels under load.
Extension 50: scale NIO.2 async channels under load.
Extension 51: scale Netty pipeline under load.
Extension 52: scale Java HttpClient under load.
Extension 53: scale WebSocket under load.
Extension 54: scale gRPC stubs under load.
Extension 55: scale backpressure over network under load.
Extension 56: scale TCP/UDP sockets under load.
Extension 57: scale NIO selectors & channels under load.
Extension 58: scale NIO.2 async channels under load.
Extension 59: scale Netty pipeline under load.
Extension 60: scale Java HttpClient under load.
Extension 61: scale WebSocket under load.
Extension 62: scale gRPC stubs under load.
Extension 63: scale backpressure over network under load.
Extension 64: scale TCP/UDP sockets under load.
Extension 65: scale NIO selectors & channels under load.
Extension 66: scale NIO.2 async channels under load.
Extension 67: scale Netty pipeline under load.
Extension 68: scale Java HttpClient under load.
Extension 69: scale WebSocket under load.
Extension 70: scale gRPC stubs under load.
Extension 71: scale backpressure over network under load.
Extension 72: scale TCP/UDP sockets under load.
Extension 73: scale NIO selectors & channels under load.
Extension 74: scale NIO.2 async channels under load.
