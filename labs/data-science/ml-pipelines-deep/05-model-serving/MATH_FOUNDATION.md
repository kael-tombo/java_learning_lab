# Model Serving - Math Foundation

## Percentile rank
- For sorted x of length n, rank r = (p/100)(n-1); interpolate between floor and ceiling entries.
- Standard linear interpolation; no distributional assumption.

## Batching model
- latency(B) = overhead + B * perItem; throughput(B) = B / latency(B).
- Throughput increases monotonically toward 1/perItem as B grows; latency grows linearly.
- Pick B from the latency cap: B <= (cap - overhead) / perItem.

## Difference of proportions
- Rates r1 = e1/n1, r2 = e2/n2; standard error SE = sqrt(r1(1-r1)/n1 + r2(1-r2)/n2).
- z = (r2 - r1)/SE; |z| near 1 is noise, larger values are signal at fixed sample size.
- Wider canary shares shrink SE as 1/sqrt(n).

## Queueing note
- When arrival rate nears service rate, waiting time grows steeply; headroom is the control.
- Tail latency, not the mean, sizes timeouts for interactive paths.

## Worked percentile example
- Illustrative sorted latencies in ms: [4, 5, 6, 7, 120]; n = 5.
- p50 rank r = 0.50 * 4 = 2.0, landing exactly on 6 ms.
- p99 rank r = 0.99 * 4 = 3.96, interpolating 7 + 0.96 * (120 - 7) = 115.5 ms.
- Replace 120 with 20: p99 becomes 7 + 0.96 * 13 = 19.5 ms while p50 stays 6 ms.

## Worked batching numbers
- Snippet endpoints: 5.5 ms at B = 1 (181 items/sec) and 100 ms at B = 64 (640 items/sec).
- Per-item cost = (100 - 5.5) / (64 - 1) = 1.5 ms; overhead = 5.5 - 1.5 = 4.0 ms.
- Throughput ceiling is 1 / 1.5 ms, about 667 items/sec, approached but never passed.
- A 40 ms cap admits B <= (40 - 4.0) / 1.5 = 24, moving 600 items/sec.

## Worked canary reading
- Snippet z of 0.88 means the observed rate gap is under one standard error.
- Quadrupling canary traffic halves SE, turning z near 0.9 into z near 1.8 at the same rates.
- The decision rule stays predeclared: share, duration, and bar set before traffic flows.

## Queueing shape
- Utilization rho = arrival rate / service rate; waiting grows steeply as rho nears 1.
- Doubling headroom near saturation cuts waits far more than doubling it at low load.
- Provision from peak rho, and let queue depth confirm the model in production.
- Timeout budgets use the tail of the wait distribution, not its mean.
