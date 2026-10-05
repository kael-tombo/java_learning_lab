# HTTP/3 & QUIC - README

## Overview
This lab covers QUIC and HTTP/3, the transport that finally removed the layering problems
inherited from TCP: head-of-line blocking, a multi-round-trip handshake, and connection
identity tied to a 4-tuple. QUIC is not a speed tweak — it is a different transport with
per-stream recovery, connection migration, and TLS fused into the protocol.

## Learning Objectives
- Explain head-of-line blocking in HTTP/1.1 and HTTP/2, and what QUIC changes
- Parse a QUIC long/short header and identify packet number encoding and header protection
- Implement per-stream flow control and prove it does not starve other streams
- Describe TLS 1.3 in QUIC, 0-RTT, and the replay risk it introduces
- Explain loss detection: packet thresholds, ACK ranges, and PTO
- Explain what Connection ID enables that a TCP 4-tuple cannot
- Evaluate an HTTP/3 rollout using measured latency by network segment

## Prerequisites
- Java 21+
- Solid understanding of TCP congestion control and TLS handshakes (labs 02 and _10)
- Familiarity with UDP datagram programming

## Lab Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main/java/` | QUIC-style connection, stream, packet builder, loss detector |
| `src/test/java/` | JUnit 5 tests for multiplexing, flow control, reassembly |
| `MINI_PROJECT/` | QuicPipe: multiplexed transport with per-stream flow control |
| `REAL_WORLD_PROJECT/` | Edge3: HTTP/3 rollout for a lossy mobile profile |
| `SOLUTION/` | Solutions to exercises |

## Quick Start

```java
// Open a connection, register two streams, and send on both.
var conn = QuicClient.connect("cdn.example.com", 443);
long reqStream = conn.registerStream();
long assetStream = conn.registerStream();
conn.sendData(reqStream, "GET /index.html HTTP/3\r\n");
conn.sendData(assetStream, "GET /logo.png\r\n");
// Loss on assetStream will not delay reqStream — that is the entire point.
```

## Topics Covered
1. Why QUIC: handshake cost, transport-level HOL blocking, connection identity
2. Packet structure: long vs short header, header protection, AEAD, 1200-byte minimum
3. Streams and multiplexing; stream IDs and direction
4. Per-stream and per-connection flow control with MAX_STREAM_DATA credit
5. Loss detection: packet threshold, ACK ranges, PTO and ack delay
6. TLS 1.3 in QUIC, session resumption, 0-RTT replay risk
7. Connection migration and connection coalescing
8. BBR vs CUBIC on lossy paths
9. Deployment: Alt-Svc, fallback, MTU, capacity

## Assessment
- Complete the coding exercises in `EXERCISES.md`
- Pass the quiz in `QUIZ.md`
- Submit the mini project
- Complete the real-world project

## Estimated Time
5-6 hours

## References
- RFC 9000 - QUIC: Transport
- RFC 9001 - Using TLS to Secure QUIC
- RFC 9002 - QUIC Loss Detection and Congestion Control
- RFC 9114 - HTTP/3
