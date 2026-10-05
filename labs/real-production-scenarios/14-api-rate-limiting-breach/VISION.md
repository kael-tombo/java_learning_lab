# Lab 14 — Vision: On-Call Excellence for Rate Limits

## The Standard
The limiter is a product feature, not a panic button. Every endpoint documents quotas + headers; clients back off gracefully; one bad key can never take down the many. 429s are routine, 5xx from overload are not.

## What Great Looks Like
- **Three layers always**: per-key fairness, per-IP abuse guard, global survival cap. Gaps are audited like security holes.
- **Data-tuned**: burst from p99 measurements, tiers from usage percentiles, top-K reviewed weekly.
- **Client empathy**: SDK parses Retry-After, docs show backoff snippet, status page explains 429 vs outage.
- **Abuse playbook**: penalty box → block → rotate, each one command, each logged for appeal.
- **Cache first**: repeat GETs served from edge; origin quota reserved for real work.

## Anti-Patterns
- Single global limit "to keep it simple" — one scraper starves everyone.
- Doubling quotas blindly during an incident without top-K check.
- Returning 500 for over-quota (clients retry harder, hiding the signal).
- No headers — clients guess, hammer, and amplify.

## Habits
1. Weekly top-K 429 review with product (upsell vs block decision).
2. Load test quotas every release; chaos-test with limiter off in staging.
3. Every new endpoint ships with limit + test + doc in same PR.
4. Game-day scraper replay quarterly.

## Interview Signal
Strong: token-bucket math, sliding-window trade-offs, top-K triage, backoff design. Weak: "we return 429 when busy (no headers, no tiers)."
