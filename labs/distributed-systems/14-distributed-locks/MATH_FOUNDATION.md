# Math Foundations — Distributed Locks

## 1. Redlock Majority

For N Redis nodes, quorum required: N/2 + 1
- N=5: quorum=3
- Probability of simultaneous failure: falls exponentially with N

## 2. Lease Duration

Minimum lease duration = max_clock_skew + max_message_delay + max_processing_time

## 3. Fencing Token Monotonicity

Token sequence: strictly increasing, no gaps guaranteed
Implementation: AtomicLong or ZooKeeper sequential counter

## 4. Probability of Lock Failure

For independent node failures with probability p:
P(quorum lost) = sum from k=quorum to N of C(N,k) * p^k * (1-p)^(N-k)

## 5. CAP Theorem Implications

- CP systems (ZooKeeper): sacrifice availability during partition
- AP systems (Redis): risk inconsistency during partition
- Choice depends on workload requirements
