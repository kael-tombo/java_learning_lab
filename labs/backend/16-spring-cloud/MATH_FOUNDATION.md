# Mathematical Foundation: Spring Cloud

## 1. Circuit Breaker Probability Model

The circuit breaker can be modeled as a Markov chain with three states (CLOSED, OPEN, HALF_OPEN).

### State Transition Probabilities

Let p = probability of failure for a single request.

**CLOSED → OPEN**: Occurs when failure count exceeds threshold in sliding window.

For a sliding window of size N with failure threshold F:
- P(open) = P(X â‰¥ F) where X ~ Binomial(N, p)
- P(open) = sum_{k=F}^{N} C(N,k) * p^k * (1-p)^{N-k}

### Expected Failures Before Open
E[requests before open] = N / p where N is the window size

## 2. Load Balancing Distribution

### Round-Robin Distribution
Requests are distributed evenly: R_i = R_total / N where N = number of instances.

### Weighted Distribution
For weights w_1, w_2, ..., w_n:
- P(i) = w_i / sum(w_j)
- Expected requests to instance i: E[R_i] = R_total * w_i / sum(w_j)

## 3. Eureka Heartbeat Timing

### Lease Renewal Probability
Given:
- Heartbeat interval: t_h (30s)
- Lease expiry: t_e (90s)
- Network failure probability: p_n

Probability of lease expiry within time T:
- P(expiry) = p_n^{t_e / t_h} = p_n^3

Mean time to evict: E[T] = t_h / (1 - p_n)

## 4. Consistent Hashing for Sticky Sessions

For requests distributed across N instances:
- Hash range: [0, 2^m - 1] where m is hash bit length
- Each instance responsible for range: (2^m / N) values
- When N changes, only K/N keys remap (where K = total keys)

## 5. Retry with Exponential Backoff

After failure, retry with delay:
- delay(n) = initial_delay * base^n + jitter
- where n = retry count, base = backoff multiplier (typically 2)

### Maximum Retry Time
Total = sum_{k=0}^{n-1} initial_delay * base^k = initial_delay * (base^n - 1) / (base - 1)

## 6. Bulkhead Pattern

Thread pool isolation divides resources into compartments.

For N compartments with capacity C each:
- Total capacity: N * C
- Probability all compartments full: (arrival_rate / (N * C))^N
- Mean wait time: E[W] = (C / arrival_rate) / (1 - utilization)

## 7. Rate Limiting (Token Bucket)

Token bucket with rate r tokens/sec, capacity b:

### Average Queueing Delay
E[delay] = b / (2 * r) for bursty traffic

### Probability of Packet Loss
P(loss) = max(0, 1 - r / arrival_rate)

## References
- Queuing Theory for Distributed Systems
- Probability and Stochastic Processes
- Resilience4J Circuit Breaker Mathematics
