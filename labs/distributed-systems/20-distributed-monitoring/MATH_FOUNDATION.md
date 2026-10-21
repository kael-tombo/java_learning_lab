# Math Foundations — Distributed Monitoring

## 1. Time Series Model

A time series is: (metric_name, labels) -> [(t1, v1), (t2, v2), ...]

Storage: n * (timestamp_bytes + value_bytes + label_overhead)

## 2. Downsampling Resolutions

Typical tiers:
- Raw: full resolution (10-30s), retained 7-30 days
- 5-minute: aggregated, 1-6 months
- 1-hour: aggregated, 1-3 years
- 1-day: aggregated, indefinite

## 3. Quantile Estimation (T-Digest)

T-Digest estimates percentiles with bounded error:
- Merges nearby centroids based on quantile
- Error: ~1% for common percentiles (p50, p99)
- Memory: ~100 centroids regardless of data size

## 4. Alert Burn Rate

For SLO of 99.9% over 30 days:
- Error budget: 0.1% * 30 days = 43.2 minutes
- Burn rate of 10: consuming budget 10x faster
- Alert when budget consumed in < 3 hours

## 5. Cardinality

High cardinality = many unique label combinations
Memory: cardinality * metric_size * retention_period

Bad: request_latency{user_id=UUID} (millions of series)
Good: request_latency{endpoint="/api", status="200"} (hundreds)
