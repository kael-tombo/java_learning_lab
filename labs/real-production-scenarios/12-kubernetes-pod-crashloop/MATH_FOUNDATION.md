# Lab 12 — Math Foundation: CrashLoop & Backoff

## 1. Exponential Backoff Series
- Delays: 10s, 20s, 40s, 80s, 160s, 300s (cap). Sum of first `n` uncapped: `10×(2^n − 1)`.
- After 5 crashes: waited ~310s. Effective restart rate drops from 6/min to ~0.2/min — buys time but delays recovery if auto-fixable.
- Alert before backoff hides signal: fire on `restarts > 3 in 15 min`, not on phase alone.

## 2. Restart-Rate Detection
- `rate(kube_pod_container_status_restarts_total[15m])`: 3 restarts/15 min = 0.0033/s. Set alert `increase(...) > 3`.
- Fleet-wide: if deploy has `R=10` replicas all crashing, total restart rate 10× single — page immediately.
- Distinguish: single-pod restarts = node/app flake (`p≈1/R`); all-pod = bad rollout (`p≈1`).

## 3. Probe Timing Math
- Time-to-first-kill = `initialDelay + period × failureThreshold`. Example: 5 + 10×3 = 35s.
- JVM start `S=60s` with kill at 35s → guaranteed CrashLoop. Fix: `startupProbe` window `≥ S + 2σ` (e.g., 30×10s=300s).
- Readiness period 5s × threshold 3 = 15s to remove bad pod from Service — bounds bad-traffic window.

## 4. Memory Limit Sizing
- `limit = heap_max + metaspace + direct + OS_headroom`. For `-Xmx1g` Spring: limit ≈ 1.5–1.7Gi.
- Headroom 30%: `limit = 1.3 × p99(rss)`. If p99 rss 1.2Gi → limit 1.56Gi.
- OOM probability falls exponentially with headroom but cost rises linearly — 25–30% is the sweet spot.

## 5. Rollout Blast Radius
- `maxUnavailable=1, maxSurge=1` on 10 replicas: at most 1 pod crashing at a time during canary.
- Without canary (Recreate): all 10 crash → 100% outage. RollingUpdate bounds impact to `maxUnavailable/R`.
- Auto-rollback trigger: crash rate >5% of pods for 5 min → `rollout undo`.

## 6. Worked Example
- Deploy 6 replicas, bad image: all crash 4× in 12 min → `increase = 24` → fleet alert fires at min 3.
- Rollback takes 90s; total bad window ~5 min with canary vs 12+ min without. Math favors small surge + fast rollback.
