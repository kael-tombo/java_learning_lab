# MATH FOUNDATION — Lab 06: Deployment Safety Math

## 1. SLO and Error Budget
- Budget = (1 − SLO) × window. SLO 99.95% monthly (30d=43,200 min): 0.0005×43,200 = **21.6 min**.
- Incident 47 min consumes 47/21.6 = **217%** → breach, freeze deploys.
- SLO 99.9%: 43.2 min/month. SLO 99.99%: 4.32 min/month.

## 2. Burn Rate
- BurnRate = observedErrorRatio / budgetRatio. BudgetRatio 0.0005.
- Observed 12% errors → 0.12/0.0005 = **240x burn** → page immediately.
- Alert tiers: fast-burn (>14x, 1h window) pages; slow-burn (>2x, 6h) tickets.

## 3. Canary Sample Size (Intuition)
- Baseline p=0.001 (0.1%). To detect rise to 0.005 with 95% confidence need ~2,000–5,000 req.
- Rule: standard error ≈ sqrt(p(1−p)/n); want SE ≪ effect size.
- Example: n=500, SE≈sqrt(0.001/500)≈0.0014 — noise swallows 0.4pp lift. n=5000, SE≈0.00045 — lift detectable.

## 4. Rolling-Update Capacity Math
- Desired 48, maxSurge 25% → up to 60 pods during rollout; maxUnavailable 25% → min 36 available.
- Rollback time ≈ (podsToReplace / parallelism) × (drain + readiness) + imagePull.
- 12 bad pods × 60s drain serial-ish → minutes; parallel + pre-pull cuts linearly.

## 5. Retry/Timeout Interaction
- Timeout 30s × 3 retries serially = 90s added p99; thread held entire time.
- Little's Law L=λW: W 0.1s→30s at λ=1000 rps → L 100→30,000 queued → pool exhaustion.
- Fix: timeout 3–5s + max 2 retries with backoff + jitter.

## 6. Availability Composition
- 3 regions each 99.9% in series via single Front Door config error → system <99.9%.
- Blue-green flip availability ≈ LB update propagation (~30–60s) vs rolling (~minutes).

## 7. Worked Examples
1. Budget 99.95%: 21.6 min. Used 47 → over by 25.4 min.
2. Error 12% for 47 min on 340k sessions → ~40,800 failed requests (order-of-magnitude).
3. Revenue $67k/h × 47/60 = **$52.5k** direct loss.
4. n=2000, p=0.001: SE≈0.0007; 0.4pp lift ≈ 5.7 SE → significant.

## 8. Takeaways
- Quantify budget before arguing "ship anyway".
- Size canaries by requests, not just minutes.
- Keep timeouts short; long timeouts are capacity multipliers.
