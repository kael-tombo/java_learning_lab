# Distributed Locks - Math Foundation

## Mutual Exclusion Requires Agreement

A lock is a consensus problem in disguise: electing "who holds the lock" must
agree across nodes, so it inherits consensus's safety and availability
properties.

```
  lock is mutual exclusion  =>  needs agreement  =>  needs quorum  =>  needs 2f+1
```

### Lock service availability

With a Raft-backed lock of `n` nodes tolerating `f = (n-1)/2` failures:

| n | f tolerated | Available iff | Availability under f failures |
|---|-------------|---------------|------------------------------|
| 3 | 1 | >= 2 alive | 1 - C(3,2)/8 = 62.5% |
| 5 | 2 | >= 3 alive | 50% |
| 7 | 3 | >= 4 alive | 50% |

If the *critical section* tolerates only a small fraction of time being locked,
the lock must be far more available than the operation it protects — which is
usually impossible. Hence the industry conclusion: **prefer not to need a
distributed lock at all.**

## Lease Safety (the Fencing Requirement)

A lease with TTL `T` is only safe if the holder finishes its work before `T`
expires. Define:

```
  required_lease_TTL  >  work_duration_p99 + clock_drift_bound + network_RTT
  safe_margin_ratio   =  TTL / work_duration_p99     (want > 3)
```

### Probability of lease expiry per acquisition

With work duration `W ~ Exp(rate = 1/mean)` and lease `T`:

```
  P(W > T) = e^(-T / mean_work_duration)

  mean = 1 s, T = 5 s  ->  P(expiry) = e^-5 = 0.67%   (~1 in 150 acquisitions)
  mean = 1 s, T = 10 s ->  P(expiry) = e^-10 = 0.0045% (~1 in 22,000)
```

Over a day at 10,000 acquisitions/s:

```
  T =  5 s:  864,000,000 * 0.0067  = 5.8 MILLION unsafe windows per day
  T = 10 s:  864,000,000 * 0.000045 = 39,000 unsafe windows per day
```

**This is the number that ends the "just use a TTL" discussion.** Expiry is not
an edge case at scale; it is the common case.

### GC pauses

If the holder can pause for `G` (stop-the-world):

```
  TTL must cover:  G_p99 + W_p99 + network_RTT + clock_skew
  T_lease >= sum of the above * safety_factor

  W_p99 = 2 s, G_p99 = 1.5 s, RTT = 0.05 s, skew = 0.5 s
  T_lease >= 4.05 s * 3  =  ~12 s
```
Composing the p99s of independent quantities is conservative, but it is the
only defensible choice. Always publish the assumed pause budget, and take a
lease timeout as a *derived* value, not a magic constant.

## Fencing Tokens

A monotonically increasing token makes an expired-then-resumed holder
*detectable*:

```
  token_i = i, strictly increasing per acquisition
  storage rejects writes with token < highest_seen_token
```

### Retries and fencing

```
  expected_retries = attempts / (1 - f)
  max_attempts     = ceil(ln(1 - p_success)) / ln(1 - f)
```

For per-attempt failure probability `f = 0.1` and required success `p = 0.999`:

```
  attempts = ln(0.001) / ln(0.9) = 6.58 / 0.105 = ~63 attempts
```

**Fencing tokens are strictly better than Redlock-style reasoning** because
safety is enforced *at the storage layer* and does not depend on timing
assumptions at all. Cost: every write carries a token, and the store must keep
a high-water mark. That is a small price for removing a whole class of
unprovable argument.

### TTL refresh and renewal races

If the holder renews every `T/3`, at most `T/3` of the lease is un-renewed when
the holder dies:

```
  effective_TTL_after_crash = T - T/3 = 2T/3
  worst-case lock hold time after holder death = 2T/3
```
So recovery time is bounded by `2T/3`, not `T`. A naive "never renewed" lock
takes up to `T`. If your SLA needs faster recovery, you must renew more often,
which costs more network traffic and exposes you to more renewal races — state
the trade-off rather than picking silently.

## Redlock: What the Arithmetic Says

Redlock acquires `N` independent locks with expiry `T`, tolerating `f` crashes,
and claims success if `N - f` grants arrive within `T`:

```
  success iff  N - f  nodes granted AND all responses within T
```

### Clock assumption

Redlock's safety argument depends on bounded clock drift `e`:

```
  if  T >  2 * elapsed + 2 * e + request_latency   =>  no two clients overlap
```

Take `elapsed = 4 ms`, `e = 1 ms`, `latency = 3 ms`:

```
  T must exceed  2*4 + 2*1 + 3 = 15 ms
```
Many real deployments use a lease of 10-30 s, which makes this condition
trivially satisfiable — but it also means a crashed holder blocks the resource
for 10-30 s. That is why Redlock-with-TTL is usually paired with fencing in
practice.

### Contention and retry cost

```
  n_contenders = N
  expected_winners_per_window = 1 / (1 + N * work/T)
  throughput ~= (N / T) * work_seconds

  N = 10, T = 0.1 s, work = 0.01 s -> ~1 op/s serialized
```
Short leases plus short critical sections produce **queue collapse**: the lock
becomes the bottleneck and throughput falls as contention rises. Measure
`acquire_wait_time` separately from `hold_time`; a lock with a long queue is a
design smell, not a tuning problem.

## Local (JVM) Locks: Why They Are Safe but Insufficient

```java
synchronized / ReentrantLock  ->  correct within one JVM
```

A JVM lock is exact — it has a global ordering and no clock. The problem is
purely scope: it cannot order two processes. The failure mode is not
"unpredictable", it is deterministic: **two instances both enter**.

Use a JVM lock *inside* each node to protect per-node state, and a distributed
lock *around* the shared resource. They solve different problems and compose:

```
  total_protection = JVM_lock(local_state) + distributed_lock(shared_resource)
```

## Quorum Read/Write for Lock State

If lock state is stored in a quorum store rather than a consensus log:

```
  R + W > N  required for linearizable lock state
  N = 5, W = 3, R = 3  -> 6 > 5  OK
```

But lock acquisition needs **test-and-set**, not plain read/write. Two
concurrent `W`s can both succeed at different replicas and both believe they
hold the lock. You therefore need either:

- a **linearizable compare-and-set** (real consensus), or
- a **single designated primary** for lock state (cheap, SPOF), or
- **Redlock** (probabilistic, needs bounded clocks + fencing for safety).

Choose deliberately; the third is not equivalent to the first.

## Availability Cost of the Conservative Option

```
  lock_availability = P(quorum reachable)
  with 3 replicas on 3 different hosts, p_indep = 0.99:
    P(all 3 alive) = 0.99^3 = 0.970
  with 3 replicas, 1 shared switch (correlated failure), p_switch = 0.99:
    P(all reachable) = 0.99          <-- shared fate dominates
```
Independent-failure maths on infrastructure with shared fate is self-deception.
Always multiply by a correlation factor for the shared layer, or admit the
number is optimistic.

## Throughput of a Coarse Lock

A lock serialising a 50 ms operation:

```
  max_throughput = 1 / hold_time = 20 ops/s
```

No amount of hardware changes this. **The most important optimisation is to
make the critical section smaller, not the lock faster.** Shrink the critical
section by moving work outside it (prepare-then-commit, or an idempotent
staging step), which is usually the real answer.