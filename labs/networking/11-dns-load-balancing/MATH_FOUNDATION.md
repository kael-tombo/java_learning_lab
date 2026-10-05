# DNS & Load Balancing - MATH FOUNDATION

## 1. Bytes, bits, and the confusion that causes bad capacity numbers

```
  bytes = bits / 8

  1 Gbps = 1000^3 bits/s = 125 * 10^6 bytes/s = 125 MB/s
  1 GiB = 2^30 bytes
```

Throughout this lab: **SI units for link rates (Gbit/s), binary units for storage
(GB vs GiB)**. Mixing them is a 7% error at the GiB boundary, which is small enough to
hide inside other uncertainty and large enough to explain a missed capacity target.

## 2. The Bandwidth-Delay Product

The single most important number in transport tuning:

```
  BDP = bandwidth * RTT
```

Worked example — a 1 Gbit/s link with 40 ms RTT:

```
  BDP = 1_000_000_000 bit/s * 0.040 s = 40_000_000 bit = 5_000_000 bytes ≈ 4.77 MiB
```

**Why it matters:** a TCP sender can only have one BDP of data in flight. If the socket
buffers together hold less than the BDP, the pipe cannot be filled, no matter how fast
the disks or the CPU are:

```
  max throughput ≈ (sendBuffer + receiveBuffer) / RTT

  With 64 KiB each side, 40 ms RTT:
    131_072 bytes / 0.040 s = 3_276_800 bytes/s ≈ 3.2 MB/s ≈ 26 Mbit/s
```

So a "10 Gbit link with 64 KiB buffers" delivers ~26 Mbit/s. Throughput is capped at
**buffer / RTT**, not by bandwidth. This is the arithmetic behind a very common
"mysterious" performance ceiling.

## 3. TTL, propagation, and the probability distribution of a failover

A failover is not one delay; it is a **distribution** over caches with different ages.

Model: with TTL `T`, a cached entry's remaining life is uniform on `[0, T]`. So the
fraction of clients that have already expired the entry after time `t` is:

```
  P(expired by t) = t / T        for 0 <= t <= T
```

Time for 95% of clients to see the change:

```
  t_95 = 0.95 * T
```

So the requirement "fail over within 5 minutes at p99" implies:

```
  T <= 5min / 0.99 ≈ 303 s
```

and to have any margin at all, a **30 s TTL** is the usual choice. Check the arithmetic on
a 1-hour TTL: `t_99 = 3564 s ≈ 59 minutes` — the objective is missed by an order of
magnitude, while the configuration looks perfectly reasonable.

There is a second-order effect. If a region's answers come as a *set* of A records, a
client that cached the set keeps trying the dead address first and only fails over on its
own retry policy. Effective propagation is then:

```
  t_effective ≈ P(TTL expiry) * T + client_retry_delay
```

which is why weighted, multi-record answers degrade gradually rather than instantly.

## 4. Load distribution fairness

Round robin over N backends with request sizes that vary is unfair by construction.

Let sizes arrive as a random variable with mean `μ`. With round robin, each backend gets
the same share of *requests*, so the load share is exactly 1/N. But the **variance** of
per-backend load is the problem: a backend that happens to receive the large requests
ends up with far more than its share of work.

Expected squared deviation for a backend under random assignment:

```
  Var(load_i) = (σ² / N) + (1/N)(μ - μ)²    (size variance dominates the imbalance term)
```

The practical consequence: round robin is fine for uniform requests and degrades quickly
when a small fraction of requests are expensive. A report endpoint next to a health check
is enough. This is the argument for least-connections balancing, which self-corrects:

```
  p(select backend i) = active_i / Σ active_j      (power of two choices, or least-connections)
```

With the *power of two choices*, sampling two backends and picking the less loaded reduces
expected maximum load to:

```
  E[max load] ≈ ln(2) / ln(N) + ln(ln(N)) / ln(N) + O(1/ln N)
```

versus `ln(N)/ln(N) = 1` for pure random choice — a substantial improvement from choosing
two, and the reason the two-choice heuristic is universal in production balancers.

## 5. Queueing, bufferbloat, and why bigger buffers are worse

A bottleneck link with a finite buffer is an M/M/1 queue. Utilisation `ρ = λ/μ`, where λ
is the arrival rate and μ the service rate. Queueing delay grows without bound as ρ → 1:

```
  M/M/1 mean queue length:    Lq = ρ² / (2(1-ρ))
  M/M/1 mean waiting time:   Wq = ρ / (μ(1-ρ)) = ρ·RTT / (1-ρ)
```

Substituting `μ = BW / L` for a buffer of `L` bytes into a full link, `Wq` reduces to
`L / BW` — **queueing delay equals the time it takes to drain the buffer at link rate**.

That single line explains bufferbloat. Double the buffer and the standing queue delay
doubles, while throughput barely improves (the link was already saturated). Concretely,
a 64 MB buffer on a 1 Gbit/s link:

```
  L / BW = 64 MiB / 125 MB/s ≈ 0.54 s of standing queue
```

Your p99 latency becomes 540 ms on a link whose baseline RTT is 40 ms — a 13× inflation
from a change that was meant to improve throughput.

There is a second, subtler effect. Loss-based congestion control (Reno/CUBIC) *infers*
congestion from loss, and loss only occurs at a buffer tail-drop. A larger buffer means:

1. higher queueing delay, and
2. a **later** loss signal, so the controller over-fills the queue before reacting.

This is the mechanism behind the plateau in transfer jobs: a "larger buffer makes it
faster per megabyte" but the total job takes longer once the ramp-down is included.

## 6. Goodput and utilisation

```
  goodput   = useful bytes delivered per second
  efficiency = goodput / link capacity
  utilisation = time link was busy / elapsed
```

TCP efficiency drops with loss, and the drop is steeper than a naive
`(1 - loss)` estimate, because each loss also costs a congestion-window reduction:

```
  throughput ≈ (MSS / RTT) * sqrt(1.5 / p)     (Mathis formula, loss p as a fraction)
```

Example: 1460-byte MSS, 40 ms RTT, 0.1% loss:

```
  sqrt(1.5 / 0.001) = sqrt(1500) ≈ 38.7
  throughput ≈ (1460 / 0.040) * 38.7 ≈ 36_500 * 38.7 ≈ 1.41 MB/s ≈ 11.3 Mbit/s
```

On a 1 Gbit/s link that is about 1% efficiency — and the fix is not a bigger buffer, it
is either a shorter path (lower RTT), a better path (less loss), or a loss-tolerant
protocol. This is the arithmetic that makes BBR's premise clear: if loss is random rather
than congestion-induced, treating it as a congestion signal destroys throughput for no
reason.

## 7. Exercises

1. A 10 Gbit/s link has 30 ms RTT. Compute the BDP. What socket buffer size is needed to
   fill it, and what is the ceiling with 256 KiB buffers on each side?
2. A service has a 3-minute failover objective. Derive the maximum TTL at p99, and explain
   what changes if the answers contain three A records rather than one.
3. Using M/M/1, compute the p99 standing-queue delay on a 1 Gbit/s link with a 32 MiB
   buffer, and state the resulting end-to-end p99 with a 25 ms base RTT.
4. Two backends, request sizes `{1ms, 1ms, 500ms}`. Compute load share under round robin
   and under least-connections, and explain which is fairer and at what cost.
5. Using the Mathis formula, find the loss rate at which a 1460-byte/40 ms flow achieves
   50% of a 100 Mbit/s link.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 5681 documents the congestion window growth and the variables these formulas
  (slow start, congestion avoidance) are derived from.
  https://www.rfc-editor.org/info/rfc5681/
- The Mathis et al. equation is the standard analytical model for TCP throughput as a
  function of RTT and loss rate, used in §6.
  https://www.rfc-editor.org/info/rfc2923/
