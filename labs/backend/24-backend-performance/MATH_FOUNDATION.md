# Mathematical Foundation: Performance

## Little's Law
L = λ * W (number of requests in system = arrival rate * response time)
For 100 req/sec with 200ms response: L = 100 * 0.2 = 20 concurrent requests

## Amdahl's Law
Speedup = 1 / ((1-P) + P/N) where P = parallel portion, N = processors
If 80% parallel, 8 cores: speedup = 1 / (0.2 + 0.8/8) = 1 / 0.3 = 3.33x

## Cache Hit Ratio for LRU
For cache of size C and working set size W:
- If C >= W: hit ratio approaches 1.0
- If C < W: hit ratio = C/W (approximate)
