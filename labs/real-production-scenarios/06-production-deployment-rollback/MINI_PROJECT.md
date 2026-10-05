# MINI PROJECT — Lab 06: Reproduce, Detect, Fix a Bad Deploy

## Objective
Reproduce an NPE-gated bad rollout in Docker/K8s-kind, detect via metrics, fix with flag + rollback.

## Part A — Reproduce (30 min)
1. Run provided Spring Boot demo with `BAD_DEPLOY=true` env on 1 of 4 replicas.
2. Send load: `curl` loop or k6 hitting `/profile/{id}` for missing users → observe 500s on ~25%.
3. Collect: pod logs showing NPE at `UserPreferenceCache.java:87`.

## Part B — Detect (20 min)
1. Add deployment marker (timestamp) to your log/dashboard notes.
2. Compute error rate: `5xx / total` over 2-min window; confirm >1%.
3. Run `kubectl rollout history` + `get events` to attribute to bad revision.

## Part C — Fix (30 min)
1. Kill-switch: set `PREF_CACHE_V2=false` (env/flag) → confirm errors drop without redeploy.
2. Null-guard code + test (null → defaults).
3. Roll back: `kubectl rollout undo` (or flip compose image tag); verify endpoints healthy + error <0.1%.

## Deliverables
- Timeline (deploy → detect → mitigate → verify with timestamps).
- Before/after error-rate numbers + log excerpts.
- One-paragraph prevention: canary + flag + auto-rollback rule.

## Stretch
- Add Prometheus alert + readiness probe exercising cache path.
- Measure drain time with/without preStop sleep.

## Grading
Detect (30%), mitigate without redeploy (30%), verified rollback (25%), prevention note (15%).
