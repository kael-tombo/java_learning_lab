# Model Serving - Internals

## Percentiles
- Sort observed latencies; p50 and p99 come from rank interpolation, as the lab snippet computes.
- Percentiles resist outliers better than the mean but still need enough samples to be stable.
- Report the window length and sample count alongside any percentile.

## Batching math
- Per-request cost splits into fixed overhead plus per-item work; batching amortizes the fixed part.
- Doubling batch size less than doubles latency but increases every item's wait.
- The snippet table shows throughput climbing 181 to 640 items/sec while latency grows 5.5 to 100 ms.

## Canary comparison
- Compare error proportions with a z-statistic over the standard error of the difference.
- Small canary traffic means wide error bars; the snippet z of 0.88 is no signal.
- Predefine the traffic share and duration before judging; peeking early inflates false alarms.

## Warmup and sizing
- Cold instances fault pages in and fill caches; warmup absorbs this before traffic arrives.
- Memory sizing starts from weight size plus batch buffers and preprocessing scratch.
- Queueing delay dominates when utilization nears capacity, so provision headroom at peak.

## Percentile interpolation
- Rank for percentile p over n sorted samples is r = (p/100)(n-1), split
  between the entries at floor(r) and ceil(r) by the fractional part.
- A single 120 ms outlier among small latencies leaves p50 near the middle
  while p99 lands near the outlier: that gap is the tail lesson.
- Replacing the outlier with 20 ms collapses p99 toward the teens while
  p50 barely moves, which is exactly the exercise's expectation.

## Batching derivation
- From the snippet endpoints (5.5 ms at batch 1, 100 ms at batch 64 with
  181 and 640 items/sec), the per-item cost is 1.5 ms and overhead 4.0 ms.
- Check: 4.0 + 1 * 1.5 = 5.5 ms giving 181.8 items/sec; 4.0 + 64 * 1.5 =
  100 ms giving 640 items/sec. Throughput tends toward 1/1.5 ms as B grows.
- The cap inequality B <= (cap - overhead)/perItem inverts this: a 40 ms
  cap admits B <= 24, with throughput 24/40 ms = 600 items/sec.

## z-statistic reading
- The snippet z of 0.88 sits near 1, which is noise at the canary's sample
  size, not evidence of a difference between versions.
- Doubling canary traffic shrinks the standard error as 1/sqrt(n) but slow
  improvement is why duration, not just share, is predeclared.
- Peeking at repeated intervals without adjustment turns that slow noise
  into false alarms; the predeclared window is the guard.
