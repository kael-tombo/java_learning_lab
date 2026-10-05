# HTTP/3 & QUIC - THEORY

## 1. What problem is QUIC actually solving?

Three, and they are related but distinct:

1. **Transport-level head-of-line blocking.** TCP delivers a byte stream *in order*. If
   packet 100 is lost, packets 101, 102... cannot be delivered even if they arrived, until
   100 is retransmitted. HTTP/2 fixed *application*-level HOL blocking by multiplexing
   requests over one connection, but the transport-level problem remained: a single lost
   TCP segment stalls every in-flight HTTP/2 stream. QUIC removes it by making recovery
   **per stream** — a lost packet only affects the stream whose data it carried.

2. **Handshake cost.** TCP needs 1 RTT for a TLS 1.2 handshake (2 with TLS 1.3), and
   application data waits for it. QUIC integrates TLS 1.3 directly, achieving **1-RTT**
   handshake and **0-RTT** resumption, because crypto state is established in parallel
   rather than in a layer above.

3. **Connection identity.** TCP connections are identified by a 4-tuple. Change your IP
   (mobile handover) or your port (NAT rebinding) and the connection breaks. QUIC
   identifies a connection by an explicit **Connection ID**, so the peer recognises the
   same logical connection on a new path.

## 2. Packet structure

QUIC has two header forms:

- **Long header** — used during the handshake; carries version, and can negotiate
  version/connection IDs, and carries a length field.
- **Short header** — used after the handshake. 1 byte of flags, then Connection ID, then
  packet number. Very compact.

What is **absent** compared to a TCP segment, and where each role went:

| TCP field | QUIC equivalent |
|---|---|
| source/dest port | Connection ID (demultiplexes) |
| sequence + ack number | Packet number (per-connection) |
| checksum | AEAD tag (covers header AND payload) |
| window field | MAX_DATA / MAX_STREAM_DATA frames |
| flags | Frame types inside the packet |

QUIC requires a minimum datagram payload of **1200 bytes** — partly for amplification
protection, partly so path MTU estimation works.

**Header protection** is a subtle and important feature: the packet number and some
reserved bits are encrypted, so intermediaries cannot read or modify them. This is
anti-ossification: TCP's visible header froze protocol evolution for years, and QUIC
prevents that from recurring.

## 3. Streams and multiplexing

A QUIC connection carries many **streams**. Each stream is an independent, ordered,
reliable byte sequence. Stream IDs encode direction and initiator, so a client-initiated
bidirectional stream gets IDs 0, 4, 8... — the low bits are fixed per stream type.

Because each stream is independent:
- A stalled stream does not block others (no HOL blocking).
- Each has its own flow control window.
- Data on one stream is irrelevant to another's reassembly.

This is the property HTTP/2 wanted but could not deliver, because HTTP/2 multiplexed
*requests* over a single *ordered* TCP byte stream.

## 4. Flow control

Like TCP, QUIC has flow control, but it is **per stream AND per connection**:

- `MAX_STREAM_DATA` grants a receiver's window for one stream.
- `MAX_DATA` grants a window for the whole connection.

The per-stream part is the practical win: a large asset download cannot consume the
entire connection window and delay many small requests behind it — the coupling that makes
TCP HTTP/2 head-of-line in practice.

Receivers grant credit as they **consume** data (auto-tuning the window), not merely as
they receive it; granting on receipt defeats throttling of a slow consumer.

## 5. Loss detection and congestion control

- **Packet threshold loss**: a packet is declared lost when 3 *later* packets are acked.
  More robust than TCP's duplicate-ACK heuristic, which is coupled to receiver behaviour.
- **Time threshold loss**: a packet is lost if a time threshold derived from max-RTT and
  latest-RTT passes without an ack.
- **PTO (Probe Timeout)**: the QUIC analogue of TCP's RTO, for when *all* acknowledgements
  are lost. The PTO is computed as `srtt + max(4·rttvar, granularity) + max_ack_delay`.
- Congestion control is **per connection** (not per stream), and BBR is a strong choice on
  lossy paths because it treats loss as a separate signal rather than proof of congestion.

## 6. TLS 1.3 in QUIC, and 0-RTT

Crypto is not a layer above QUIC; it is **inside** it (the `CRYPTO` frame carries handshake
data, protected with packet keys). Consequences:

- 1-RTT handshake; 0-RTT on **resumption** (the client sends application data in the first
  flight using a cached key).
- Because encryption is mandatory from packet 1, middleboxes cannot see QUIC's contents —
  which is also why QUIC deployment sometimes fails behind enterprise proxies that expect to
  inspect TLS.

**0-RTT replay risk**: data sent in the first flight, before the handshake completes, can
be captured and **resent** by an attacker; the server cannot distinguish a replay from the
original. So 0-RTT is safe for **idempotent** operations (GET, HEAD, cacheable reads) and
must be restricted to them for state-changing requests. A CDN in front mitigates it further,
because a replayed request is answered from cache with no side effect.

## 7. Connection migration and coalescing

Because a connection is identified by a Connection ID rather than a 4-tuple:

- **Migration**: the client can change networks (Wi-Fi → cellular) and keep the same
  connection, after **path validation** (a PATH_CHALLENGE to confirm the new path works).
- **Coalescing**: HTTP/3 connections are keyed by origin, not hostname, so a client that
  fetched `cdn.example.com` over h3 can reuse that connection for `img.example.com` if the
  server accepts the coalesced request and presents a certificate valid for both names.

## 8. HTTP/3 mapping

HTTP/3 maps HTTP semantics onto QUIC streams, with some simplifications that come from
having a better transport:

- **Header compression**: HPACK-like QPACK, static + dynamic tables, with per-stream
  blocked streams while a dynamic-table update propagates.
- **No connection-level head-of-line** for requests; each request is effectively its own
  stream flow.
- **Server push** was removed — with multiplexing, a client can simply open another stream,
  and push added complexity for little benefit.

## 9. Deployment reality

- Advertised via `Alt-Svc: h3=":443"; ma=86400` over HTTPS (or HTTP/3 advertised on the
  first response).
- **Fallback** to TCP + HTTP/2 is essential: some networks silently block UDP/443. The
  server must fall back transparently on a QUIC handshake failure, not fail closed.
- **MTU**: keep UDP payloads under the path MTU (commonly 1452 for a 1500 path) or IP
  fragmentation destroys QUIC's congestion control, causing a mysterious subset of slow users.
- **Capacity**: QUIC is in userspace, so CPU per connection is higher than kernel TCP —
  connection count per node becomes a capacity metric.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 9000 specifies QUIC transport: Connection ID, streams, flow control, packet
  numbering, and the loss-detection inputs.
  https://www.rfc-editor.org/info/rfc9000/
- RFC 9001 specifies how TLS 1.3 secures QUIC, including the 0-RTT (early data) model and
  its replay considerations.
  https://www.rfc-editor.org/info/rfc9001/
- RFC 9002 specifies QUIC loss detection and congestion control, including the packet and
  time thresholds and PTO.
  https://www.rfc-editor.org/info/rfc9002/
- RFC 9114 specifies HTTP/3 over QUIC, including the QPACK header compression and the
  Alt-Svc advertisement.
  https://www.rfc-editor.org/info/rfc9114/
