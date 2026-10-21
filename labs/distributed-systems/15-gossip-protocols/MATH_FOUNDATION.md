# Math Foundations — Gossip Protocols

## 1. Epidemic Spreading Model

In the susceptible-infected (SI) model:
- dI/dt = beta * I * (N - I)
- I(t) = N / (1 + (N-1) * e^(-beta*N*t))

Time to infect all nodes: O(log N)

## 2. Fan-out and Round Analysis

If each node contacts f random peers per round:
- Infected after r rounds: N * (1 - (1 - f/N)^(N*r))
- Rounds to reach all nodes: log_f(N)

## 3. Failure Detection Bounds

SWIM detection time:
- Protocol period: T
- Suspicion timeout: k * T
- Expected detection: T * (1 + k)

## 4. Message Complexity

Per round:
- Push: O(N * f) messages
- Pull: O(N * f) messages
- Push-Pull: O(N * f) messages

## 5. False Positive Rate

For SWIM with suspicion:
- False positive probability: depends on suspicion multiplier
- Can be tuned by adjusting k in the suspicion timeout
- Trade-off: higher k reduces false positives but increases detection time
