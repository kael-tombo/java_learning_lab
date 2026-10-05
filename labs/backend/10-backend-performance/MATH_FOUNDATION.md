# Math Foundation

Backend Performance is not pure math, but a few models sharpen judgement.

## queueing theory and percentiles over averages
For Backend Performance, reason with these quantities:
- throughput T (requests/sec)
- latency L (p50/p95/p99)
- concurrency C = T * L (Little's law)

## Consistency vs availability
- Stronger consistency narrows the window of divergence but hurts availability.
- Eventual consistency is a spectrum; measure the convergence window.

## Failure math
If each stage fails independently with probability p, end-to-end success is the product of (1 - p_i) across stages. Add redundancy to raise it.

## Little's law
L = lambda * W. If a dependency holds 200 in-flight calls at 50ms average, expect roughly 1000 rps of capacity.

## Rate limiting
Token bucket: allow r tokens/sec, burst b. Sustained rate <= r; bursts <= b.

## Checklist
- [ ] You can state L, T, C for the critical path.
- [ ] You know the consistency window you tolerate.
- [ ] You can estimate burst capacity with a token bucket.
