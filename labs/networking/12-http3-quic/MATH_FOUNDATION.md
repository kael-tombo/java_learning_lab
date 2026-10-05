# HTTP/3 & QUIC - MATH FOUNDATION

## 1. Handshake cost — where the RTT savings come from

The claim "QUIC is faster" is really a claim about **round trips to first byte**.

```
  TLS 1.2 over TCP:      TCP SYN/SYN-ACK (1 RTT)  +  TLS handshake (1-2 RTT)  -> 2-3 RTT
  TLS 1.3 over TCP:      TCP handshake (1 RTT)    +  TLS 1-RTT handshake    -> 2 RTT
  QUIC + TLS 1.3:        1-RTT handshake (crypto in parallel)              -> 1 RTT
  QUIC 0-RTT resumption: 0-RTT (cached keys, data in first flight)        -> 0 RTT
```

Savings on a cold connection to a 200 ms RTT mobile client:

```
  Cold:   2 RTT -> 1 RTT   saves 1 x 200 ms = 200 ms
  Resumed: 2 RTT -> 0 RTT  saves 2 x 200 ms = 400 ms
```

But: **connections are rarely cold.** With HTTP/2 today, a returning visitor reuses a
warm TCP+TLS connection and pays **zero** handshake RTTs. So the handshake saving applies
to *new* connections only. If only 10% of requests open a new connection:

```
  average saving = 0.10 x 400 ms = 40 ms
```

Compare that honestly against the per-request HOL win (below). A correct business case
leans on the second effect, not the first — a point worth internalising before claiming
a performance win.

## 2. Head-of-line blocking: the expected stall from a loss

With a single TCP connection carrying `N` streams, one lost segment stalls the entire
connection until retransmission completes.

Assume a loss probability `p` per packet, MSS of 1400 bytes, and an average of 2 packets
in flight per stream across `N` streams. When a packet is lost, the connection stalls for
one retransmission timeout, whose duration under fast retransmit approximates:

```
  RTO ≈ RTT + deviation term   ~ roughly 1.5 x RTT at steady state
```

Expected per-connection stall rate from loss:

```
  stall frequency = p x (packets in flight per RTT) = p x (BDP / MSS)
  expected stall time per RTT = p x (BDP / MSS) x 1.5 x RTT
```

Worked example — 1 Mbit/s, 200 ms RTT, 1% loss, 6 parallel streams:

```
  BDP = 1_000_000 x 0.2 = 200_000 bit = 25_000 bytes ≈ 18 packets
  stall frequency = 0.01 x 18 = 0.18 stalls per RTT
  expected stall time per RTT = 0.18 x 1.5 x 0.2 s = 0.054 s = 54 ms per 200 ms RTT
```

So ~27% of wall-clock time is spent stalled — **and all six streams wait for every stall.**
In QUIC, only the stream that lost data stalls:

```
  stall affecting one stream of six = 0.054 / 6 ≈ 9 ms, and only that stream pays it
```

Effective latency improvement for the other five streams ≈ 45 ms per RTT. This is the
dominant, repeatable win, and it scales with the number of parallel streams and the loss
rate — which is exactly the lossy-mobile-network profile where HTTP/3 is worth deploying.

## 3. 0-RTT and the replay budget

0-RTT saves a round trip but accepts a replay risk. Let `R` be the fraction of resumed
connections where an attacker can capture and replay early data, and `D` the damage of one
replayed state-changing request (duplicate payment, duplicate shipment):

```
  expected harm per resumed connection = R x D
```

If 30% of connections resume and an attacker replays 0.1% of them:

```
  expected replayed harmful requests = 0.30 x 0.001 x (requests per resumed connection)
```

The reason this arithmetic is worth doing explicitly: it shows the mitigation is not
"reduce R" but **make the replayed request harmless**. Two standard mitigations:

1. **Only allow 0-RTT for idempotent requests** — the replay just refetches cacheable data.
2. **Make 0-RTT conditional on cache presence** — if the request would be served from an
   edge cache, a replay has no side effect, so accept it; otherwise reject early data.

Neither requires reducing replay probability; both change the consequence.

## 4. Flow control window sizing

A receiver advertises a window; the sender may not exceed it. To fill a path of
bandwidth `B` and RTT `R`, the window must be at least the BDP:

```
  window >= B x R
```

Example — 100 Mbit/s, 150 ms RTT:

```
  BDP = 100e6 x 0.15 = 15e6 bit = 1_875_000 bytes ≈ 1.8 MB
```

QUIC sets a **per-connection** window (`MAX_DATA`) and a **per-stream** window
(`MAX_STREAM_DATA`). Sizing them is a two-sided decision:

- **Per-stream window**: large enough for the biggest single response, small enough that
  one large download cannot starve other streams. For a web page, a few hundred KB per
  stream is typical; a large stream is allowed to grow via auto-tuning.
- **Per-connection window**: roughly the sum of what concurrently active streams need —
  `per_stream x expected_concurrent_streams`. A page with 30 assets: 30 x 512 KB ≈ 15 MB.

Window scaling itself: if the window is too small, throughput is capped at `window / RTT`:

```
  throughput cap = window / RTT = 1_875_000 / 0.15 ≈ 12.5 MB/s = 100 Mbit/s   (matches BDP)
```

If we set the per-stream window to 64 KB with 150 ms RTT, each stream caps at
`65_536 / 0.15 ≈ 437 KB/s` — so a page of 30 assets delivers `30 x 437 KB/s` aggregate,
but any *single* large asset is capped at 437 KB/s regardless of link capacity. That is
the tuning mistake this section exists to prevent.

## 5. Loss detection thresholds

QUIC declares loss on a **packet threshold** (3 acked packets beyond) or a **time
threshold**. The time threshold from RFC 9002:

```
  kTimeThreshold = max(kGranularity, kPacketThreshold x max_ack_delay + max_ack_delay)
                  = max(1ms, 3 x 25ms + 25ms) = 100 ms   (with kPacketThreshold=3, max_ack_delay=25ms)
```

A packet is declared lost if unacked for longer than:

```
  time_threshold = kTimeThreshold + max(latest_rtt, smoothed_rtt)
```

On a 200 ms path, that is `100 + 200 = 300 ms` of unacked time before the time threshold
fires — comfortably more than one RTT, so it does not fire spuriously on a delayed but
healthy network. The packet threshold usually fires first, which is the intent.

PTO:

```
  PTO = smoothed_rtt + max(4 x rtt_variation, kGranularity) + max_ack_delay
```

With `srtt = 200 ms`, `rttvar = 20 ms`, `max_ack_delay = 25 ms`:

```
  PTO = 200 + max(80, 1) + 25 = 305 ms
```

PTO must exceed `srtt` substantially; if PTO is close to RTT, a single delayed ACK triggers
a spurious retransmit, which itself causes congestion — the reason the `4 x rttvar` term
dominates the formula.

## 6. Loss rate and algorithm choice (Mathis)

```
  throughput ≈ (MSS / RTT) x sqrt(1.5 / p)
```

Same 1400-byte MSS, 200 ms RTT, at three loss rates:

```
  p = 0.001:  (1400/0.2) x sqrt(1500)  = 7000 x 38.7   ≈ 271 KB/s ≈ 2.2 Mbit/s
  p = 0.010:  (1400/0.2) x sqrt(150)   = 7000 x 12.25  ≈  86 KB/s ≈ 0.7 Mbit/s
  p = 0.030:  (1400/0.2) x sqrt(50)    = 7000 x 7.07   ≈  49 KB/s ≈ 0.4 Mbit/s
```

Loss-based control loses a factor of ~5.5 going from 0.1% to 3% loss. BBR's premise is
that on a path where loss is *random* (radio, congested Wi-Fi) rather than
congestion-driven, treating it as a congestion signal destroys throughput for no reason —
which is why the mini project's BBR implementation reaches several times the Reno
throughput at 2% loss, and why a lossy mobile network is the clearest case for BBR.

## 7. Exercises

1. A page loads 20 assets over h2 on a 250 ms path with 1.5% loss. Using §2, estimate the
   per-RTT stall time under HTTP/2 and under HTTP/3, and state which assets are affected in each.
2. Compute the BDP for 50 Mbit/s at 300 ms RTT, then the throughput cap with a 128 KB
   per-stream window. What window is needed to reach full rate?
3. A client opens 1000 h3 connections/sec against a 16-core node. QUIC costs ~20% more CPU
   per connection than kernel TCP. Estimate the CPU-bound connection ceiling and state
   the metric you would alert on.
4. Using §3, evaluate a policy allowing 0-RTT for POST: at 30% resumption and a replayable
   0.1% of sessions, how many duplicate-payment risks per 1e6 resumed sessions, and what
   policy change removes the risk entirely?
5. With `srtt = 150 ms`, `rttvar = 5 ms`, `max_ack_delay = 10 ms`, compute PTO and confirm
   it is safely above RTT. Then find the `rttvar` at which PTO would fall below 1.5x RTT.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 9002 §6 defines the packet threshold, the time threshold, and the PTO computation
  used in §5, including the `kGranularity` and `kPacketThreshold` constants.
  https://www.rfc-editor.org/info/rfc9002/
- The Mathis et al. equation for TCP throughput under loss is applied in §6 as the baseline
  that motivates BBR's loss-tolerance on lossy paths.
  https://www.rfc-editor.org/info/rfc2923/
