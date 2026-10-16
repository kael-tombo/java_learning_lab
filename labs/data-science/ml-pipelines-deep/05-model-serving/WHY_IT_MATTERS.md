# Model Serving - Why It Matters

Latency behavior is product behavior: tail spikes become timeouts, retries, and abandoned sessions on interactive paths.

Version discipline decides incident cost. Teams with shadow/canary practice and routing rollback recover in minutes; teams without them redeploy under pressure.

Schema stability decides velocity. Versioned contracts let model and client teams evolve independently instead of in lockstep deploys.

Reproducible prediction logs decide whether incidents are diagnosable or merely regrettable.

Batching discipline decides unit economics. Right-sized batches multiply throughput on the same hardware; unbounded waits destroy interactivity.

Warmup decides deploy safety. The first minutes after a release carry the highest risk, and warmup absorbs exactly that risk.

Preprocessing parity decides quality. The best model underperforms a weaker one when its serving features drift from training.

Capacity headroom decides peak survival. Queueing theory is unforgiving near saturation; provisioned slack is the shock absorber.

## Latency as contract

A p99 budget is a promise written in percentiles: 99 of 100 requests answer inside
the cap at peak, and the hundredth is bounded by timeout plus fallback. Promises
compose downward into per-leg slices, each owned and alerted, so a slip names its
culprit instead of starting a search.

Per-version budgets matter because blended metrics forgive regressions: a canary at
small share barely moves fleet p99 while its own users suffer. Version-tagged
histograms keep each version's promise separate until the shift completes.

## Rollout economics

Shadow scoring buys comparison without exposure: full production input against a
version that cannot act. The price is compute headroom, which is why shadow load
is capped and shed first when budgets tighten.

Canary buys live evidence at bounded blast radius: real traffic, real tail, small
share. The price is patience — predeclared duration while error bars shrink as
1/sqrt(n) — and teams that skip the wait buy noise at full price.

Blue-green buys instant reversal: two warm stacks and a routing decision. The price
is doubled capacity during the shift plus the discipline of keeping the old stack
warm until the new one is declared stable. Rollback drills protect that purchase.

## Quality plumbing

Preprocessing parity is the cheapest quality control in the building: one shared
code path, diffed on identical inputs, catching silent feature shifts before any
user does. Every divergence caught in a diff is an incident that never pages.

Prediction logs are the building's memory: version-tagged inputs, outputs, and
latencies that replay any window on demand. Incidents without logs are settled by
confidence; incidents with logs are settled by evidence.

## Capacity honesty

Headroom measured at peak-like load is the only headroom that counts: averages
understate queues, cold instances understate tails, and hope understates both.
Queue depth watched per version turns saturation from a surprise into a schedule.
