# Lab 08: Observability — Logs, Metrics, Traces — Math Foundation

Observability is mostly three computations: a rate, a quantile, and a budget. Do them by hand once and you will never again trust a misconfigured dashboard.

---

## 1. Error budget arithmetic

```
error_budget_fraction = 1 − SLO
error_budget_time     = (1 − SLO) × window
budget_remaining_pct  = (allowed − observed) / allowed × 100
```

| SLO | Allowed failure / 30 days | / 28 days | / 7 days |
|---|---|---|---|
| 99% | 7.2 h | 6.7 h | 1.7 h |
| 99.5% | 3.6 h | 3.4 h | 50.4 min |
| 99.9% | 43.2 min | 40.3 min | 10.1 min |
| 99.95% | 21.6 min | 20.2 min | 5.0 min |
| 99.99% | 4.3 min | 4.0 min | 1.0 min |

Worked: 99.9% over 30 days, outage of 30 minutes:
```
allowed = 43.2 min
used    = 30 min
remain  = 13.2 min = 30.6% of budget
```

**Design implication**: an SLO is only credible if a single incident cannot consume it. A 30-minute outage uses 70% of a three-nines budget — so three-nines services need either a shorter window, a higher SLO, or a budget split by tier.

---

## 2. Burn rate

```
burn_rate = observed_bad_fraction / allowed_bad_fraction
           = (1 − SLI_observed) / (1 − SLO)
time_to_exhaustion_days = 30 / burn_rate
```

`SLI_observed = 99.0%`, SLO 99.9%:
```
burn = 0.01 / 0.001 = 10×   →  30/10 = 3 days to exhaust
```

The standard multi-window configuration:

| Tier | Long window | Short window | Burn | Budget exhausted in | Action |
|---|---|---|---|---|---|
| Page | 1 h | 5 m | 14.4× | ~2 days | page |
| Page | 6 h | 30 m | 6× | ~5 days | page |
| Ticket | 3 d | 6 h | 1× | 30 days | ticket |
| Ticket | 14 d | 1 d | 0.5× | 60 days | ticket |

(Exact figures vary between the SRE workbook and vendor defaults — verify the thresholds you implement against your own window length. The *shape* — two windows ANDed, fast + slow — is the invariant.)

Why two windows ANDed: the short window gives fast detection, the long window prevents paging on a 5-minute blip that self-heals.

---

## 3. Rate and counter queries

```
rate(counter[window])      ≈ (Δ counter) / (window seconds), reset-aware
increase(counter[window])  ≈ Δ counter extrapolated to the window
```

Concretely for `http_requests_total` scraped every 15 s over 5 minutes:

```
samples    = 300 s / 15 s = 20
rate()     = (last − first) / 300        (after counter-reset correction)
irate()    = (last − previous) / 15      — too spiky for dashboards, use only for
                                          ultra-fresh "is it moving" checks
```

**Minimum window rule**: `window ≥ 4 × scrape_interval`. With 15 s scrapes, 1m is the floor for `rate()`; 5m gives 20 samples and stable percentiles.

---

## 4. Quantiles from a histogram

```
p_q = bucket_lower + (bucket_upper − bucket_lower) × ( q − c_{i-1} ) / ( c_i − c_{i-1} )
```

where `c_i` is the cumulative count in the bucket containing the quantile.

Buckets `[0.1, 0.2, 0.3, 0.5, 1, +Inf]`, cumulative counts `[200, 800, 950, 995, 1000, 1000]`:

```
p99 lies in the 0.5–1.0 bucket:  c_lower = 995, c_upper = 1000
p99 ≈ 0.5 + (1.0 − 0.5) × (990 − 995) / (1000 − 995)
```

Note `(990 − 995) = −5` is negative, which means the cumulative counts are inconsistent with the quantile — the interpolation is meaningless. This is exactly what happens when buckets are too coarse near the value you care about. Fix the buckets, not the query.

Bucket design rule:

```
required buckets ≈ 10–20, with at least one boundary strictly below the SLO threshold
SLO 200 ms  →  [.05 .1 .15 .2 .25 .3 .4 .5 .75 1 1.5 2 3 5 10 +Inf]
```

**Fractional-error sanity check**: if a bucket spans 0.5–1.0 s and holds 0.5% of traffic, your p99 estimate carries up to ±250 ms of error — larger than typical SLO headroom. Coarse buckets are an accuracy decision, not a style choice.

---

## 5. SLI ratio arithmetic and validity

```
SLI = good_events / valid_events
```

A 200 ms latency SLO with buckets `le=0.2` and `+Inf`:

```
good = count(le="0.2")
valid = count(le="+Inf") − excluded(4xx client errors, if the policy excludes them)
SLI = good / valid
```

Worked: 10,000 requests in 5 min, 250 with 5xx, 900 slower than 200 ms:
```
valid = 10,000 (excluding a documented set)
good  = 10,000 − 250 − 900 = 8,850
availability SLI = 8,850 / 10,000 = 88.5%     →  catastrophic; budget long gone
latency SLI      = 9,100 / 10,000 = 91.0%
```

**Guard against the empty denominator**: at 3 a.m. with 5 requests, one failure = 80% SLI = instant page. Fix: require `valid_events ≥ N` (e.g. 100) before evaluating the SLI, and alert on volume separately.

---

## 6. Little's Law applied to observability

```
L = λ × W        →  in-flight = rate × latency
```

`λ = 2,000 req/s`, p50 = 40 ms → `L_p50 = 80`. p99 = 900 ms → if that tail were uniform, `L = 1,800`. The gap between "80 concurrent at the median" and the saturated state is where queueing shows up, and it is invisible in a latency average. This is why concurrency/queue-depth is a *better* saturation metric than CPU for alerting on I/O services.

---

## 7. Trace sampling economics

```
recorded_spans/s = λ_trace × spans_per_trace × p_sample
storage_cost     ∝ recorded_spans/s × avg_span_size
```

`λ = 2,000/s`, 12 spans per trace, avg 1.5 KB/span:

```
full:      2,000 × 12 = 24,000 spans/s  →  36 GB/s of span data
1% head:      240 spans/s               →  360 MB/s   (and biased: drops all the slow ones)
tail-based:    ~500 spans/s (all errors + traces > 1 s + 1% of the rest)
               →  750 MB/s, and the errors are always in there
```

The tail-based number is higher in volume and dramatically better in value — a strong argument when justifying the cost of a Collector.

---

## 8. Cardinality math

```
series_per_metric = distinct(combination of all label values)
memory_per_series ≈ ~1–3 KB (head + WAL/chunk overhead) + series churn cost
```

`http_server_requests_seconds_count` with `service`, `env`, `uri`, `method`, `status`, `outcome`:
```
if uri is a raw path with an order id: 100,000 distinct values
series = 100,000 × 5 (method×status×outcome combos) ≈ 500,000 series
at ~2 KB/series  →  ~1 GB of RAM for ONE metric   →  OOM risk for the whole Prometheus
```

Fix: `http.route` as a Spring template (`/orders/{id}`) → ~40 routes → `40 × 5 = 200` series. **Always templatize URI labels in Java services.**

---

## 9. Log volume and cost

```
log_volume/day = requests/day × P(log this request) × avg_bytes/line × lines/request
```

`λ = 2,000/s = 172.8M/day`, 100% logged, 400 bytes/line, 3 lines/request:
```
172.8M × 1 × 400 B × 3 = 207 GB/day   →  ~6.2 TB/month, before index/replication
```

With 1% success sampling and 100% errors:
```
172.8M × 0.01 × 400 × 3 = 2.07 GB/day  →  ~62 GB/month
```

**Sampling is the only lever that matters** here — a 100× reduction for a small risk of missing a specific successful request, and zero risk on the failures you actually investigate.

---

## 10. Exemplar-based debugging path

```
metric bucket (slow)  →  exemplar.trace_id  →  trace (which span)  →  logs for that span
```

Value: this is the fastest path from "latency regression at 10:42" to the exact SQL statement. It only works if (a) histograms have exemplars enabled, (b) sampling retains slow traces, (c) logs carry `trace_id`. All three are configuration, and all three are usually missing.

---

## 11. Detection-time and budget-aware alerting

```
budget_consumed_over_window = burn_rate × window / budget_window
```

Design target for a paging alert on a three-nines service:
```
burn over 1 h should imply:  1 h consumed of a 43.2 min budget  →  page (over budget in one window)
```
So `burn_1h × 1h ≥ 43.2 min` → `burn_1h ≥ 0.72×` would page on the window alone; the 14.4× threshold is deliberately far more conservative because it also requires the 6h confirmation — it targets "we will be out of budget in 2 days", which is a real operational emergency, not a blip.

Trade-off in one line: **lower thresholds = faster detection + more noise; higher thresholds = fewer pages + later detection.** Choose with the error budget, not with taste.

---

## 12. Recording-rule cost model

```
raw_series_evaluated = series × windows_evaluated
rule_cost ∝ evaluations_per_rule / interval, charged against the query engine
```

Without recording rules, a 12-panel dashboard at 15 s refresh over 500k series re-evaluates ~4M series per panel. Pre-recording the dashboard's aggregations reduces each panel to a few series and cuts dashboard load by 1–2 orders of magnitude. This is a capacity-planning exercise, not an optimization nicety.

---

## 13. Quick drills

1. 99.9% over 30 days; 30-minute outage. Budget left? **Answer: 13.2 min (31%).**
2. `SLI = 99.0%` against a 99.9% SLO. Burn rate and time to exhaustion? **Answer: 10×, 3 days.**
3. `rate()` on a 15 s scrape interval — minimum window? **Answer: 1m (≥4 samples); use 5m for stability.**
4. Your SLO is 200 ms and buckets are `[0.5, 1, 2.5, 5]`. Usable? **Answer: no — no bucket below 0.2 s, so the latency SLI cannot be computed.**
5. 10,000 requests, 250 errors, 900 over 200 ms. Combined SLI? **Answer: (10000−250−900)/10000 = 88.5%.**
6. 3 requests/hour, one fails. SLI and should you page? **Answer: 66.7%, and no — enforce a minimum `valid_events` threshold.**
7. `L = λ × W` at λ=2,000/s, p99=900 ms. In-flight at the tail? **Answer: 1,800 vs 80 at the median — that gap is the queue.**
8. `uri` label is a raw path with 100k order ids, 5 status combos. Series? **Answer: ~500k → ~1 GB. Templatize `uri`.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `budget = (1 − SLO) × window` | error budget in minutes or failures |
| `burn = (1 − SLI_obs)/(1 − SLO)`, `exhaust = 30/burn` days | burn-rate alerts |
| `rate(counter[w])` with `w ≥ 4 × scrape_interval` | PromQL correctness |
| `p_q` histogram interpolation, buckets straddling the SLO | quantile accuracy |
| `SLI = good/valid` with `valid ≥ N` | SLO validity at low traffic |
| `L = λ × W` | why tails cause saturation |
| `series = distinct(label combos)` | cardinality budgeting |
| `log_volume = λ × P(log) × bytes × lines` | sampling ROI |
| `detection = burn_1h × 1h vs budget` | threshold selection with intent |
