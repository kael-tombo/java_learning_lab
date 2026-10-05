# Lab 14 — Mini Project: Reproduce + Detect + Fix Rate Breach

## Objective
Build a limited API + abusive client locally, detect the breach, and harden — ~60 minutes.

## Part 1 — Reproduce (20 min)
1. Start a Flask/Spring `GET /catalog` with a 10/s token bucket (any lib or 20-line filter); return 429 + Retry-After.
2. Write `good_client.py` (2/s, honors Retry-After) and `bad_client.py` (50/s tight-loop, ignores 429).
3. Run both; capture: good gets mostly 200, bad gets 429s, server p99 flat (limiter holding).
4. Disable limiter; rerun bad client; show latency spike / errors (unprotected baseline).

## Part 2 — Detect (20 min)
1. Log `key, ip, path, status`; script `topk.sh` printing top-5 429 keys + 429 share.
2. Classify: which client is scraper vs legit from shape (rate, UA, pages)?
3. Build 429-rate chart (log → CSV → plot) annotated with mitigation time.
4. Write alert rule: `rate(429[5m]) by key > threshold` in pseudo-PromQL.

## Part 3 — Fix (20 min)
1. Add per-key (10/s) + per-IP (20/s) + global (50/s) layers; retest — show which fires.
2. Implement penalty box: key >5× quota in 1 min → block 5 min; verify good unaffected.
3. Add 60s cache on `/catalog`; measure origin QPS drop with bad client running.
4. Rotate abused key; document runbook: headers → top-K → classify → block/raise/cache.

## Deliverables
- Limiter code + configs, both clients, `topk.sh`, chart, runbook.
- Success: abuser contained (429/blocked), legit green, origin protected, all with logs.

## Grading
- Reproduce (30%), Detect/top-K (35%), Fix + runbook (35%).
