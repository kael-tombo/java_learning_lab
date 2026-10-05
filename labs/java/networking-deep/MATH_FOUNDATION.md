# Math Foundation — Deep Java Networking (networking-deep)

Quantitative models behind sockets, NIO/NIO.2, Netty, HTTP client, gRPC. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (networking-deep)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `TCP/UDP sockets`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `NIO selectors & channels`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `NIO.2 async channels`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `Netty pipeline`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `Java HttpClient`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `WebSocket`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `gRPC stubs`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `backpressure over network`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to TCP/UDP sockets; record assumption + error.
- Note 1: apply to NIO selectors & channels; record assumption + error.
- Note 2: apply to NIO.2 async channels; record assumption + error.
- Note 3: apply to Netty pipeline; record assumption + error.
- Note 4: apply to Java HttpClient; record assumption + error.
- Note 5: apply to WebSocket; record assumption + error.
- Note 6: apply to gRPC stubs; record assumption + error.
- Note 7: apply to backpressure over network; record assumption + error.
- Note 8: apply to TCP/UDP sockets; record assumption + error.
- Note 9: apply to NIO selectors & channels; record assumption + error.
- Note 10: apply to NIO.2 async channels; record assumption + error.
- Note 11: apply to Netty pipeline; record assumption + error.
- Note 12: apply to Java HttpClient; record assumption + error.
- Note 13: apply to WebSocket; record assumption + error.
- Note 14: apply to gRPC stubs; record assumption + error.
- Note 15: apply to backpressure over network; record assumption + error.
- Note 16: apply to TCP/UDP sockets; record assumption + error.
- Note 17: apply to NIO selectors & channels; record assumption + error.
- Note 18: apply to NIO.2 async channels; record assumption + error.
- Note 19: apply to Netty pipeline; record assumption + error.
- Note 20: apply to Java HttpClient; record assumption + error.
- Note 21: apply to WebSocket; record assumption + error.
- Note 22: apply to gRPC stubs; record assumption + error.
- Note 23: apply to backpressure over network; record assumption + error.
- Note 24: apply to TCP/UDP sockets; record assumption + error.
- Note 25: apply to NIO selectors & channels; record assumption + error.
- Note 26: apply to NIO.2 async channels; record assumption + error.
- Note 27: apply to Netty pipeline; record assumption + error.
- Note 28: apply to Java HttpClient; record assumption + error.
- Note 29: apply to WebSocket; record assumption + error.
- Note 30: apply to gRPC stubs; record assumption + error.
- Note 31: apply to backpressure over network; record assumption + error.
- Note 32: apply to TCP/UDP sockets; record assumption + error.
- Note 33: apply to NIO selectors & channels; record assumption + error.
- Note 34: apply to NIO.2 async channels; record assumption + error.
- Note 35: apply to Netty pipeline; record assumption + error.
- Note 36: apply to Java HttpClient; record assumption + error.
- Note 37: apply to WebSocket; record assumption + error.
- Note 38: apply to gRPC stubs; record assumption + error.
- Note 39: apply to backpressure over network; record assumption + error.
- Note 40: apply to TCP/UDP sockets; record assumption + error.
- Note 41: apply to NIO selectors & channels; record assumption + error.
- Note 42: apply to NIO.2 async channels; record assumption + error.
