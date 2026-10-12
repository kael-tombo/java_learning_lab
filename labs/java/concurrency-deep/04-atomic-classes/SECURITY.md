# Security: Atomic Classes

## Threat 1 — check-then-act on atomics mistaken for authorization
`get()` then `compareAndSet()` with a policy decision between them admits TOCTOU: the value changes after the check. Fold authorization into the CAS witness loop or guard with a lock so check and commit are one step.

## Threat 2 — ABA aliasing corrupting lock-free structures
Node reuse lets A->B->A fool bare CAS, resurrecting revoked/freed entries in pools and stacks. Use fresh allocation, stamps, or marks anywhere identity history affects safety.

## Threat 3 — fuzzy sums driving enforcement
`LongAdder.sum()` concurrent with updates is approximate; rate limits, quotas, or billing computed from it drift under load. Enforce from exact sources (AtomicLong/locked totals); use adder sums for dashboards only.

## Threat 4 — retry-burn as amplification vector
Attacker-paced contention on a single CAS word converts each request into many retries of CPU burn. Stripe hot atomics, bound retries, and shed load when CAS-failure rates spike.

## Checklist
- [ ] No check-then-act across CAS gaps on auth paths. [ ] ABA handled where identity matters. [ ] Enforcement totals exact. [ ] CAS-failure metrics alerted.

## Threat 5 — check-then-act across the CAS gap
- `get()`-then-decide-then-`compareAndSet()` admits TOCTOU: the value changes after the check, so authorization/validation computed on the read does not cover the commit.
- Fold the check into the CAS witness loop (re-validate per lap from the fresh read) or guard the span with a lock — check and commit must be one indivisible step on auth paths.
- Log CAS-gap windows on security decisions: any measurable gap between read and commit is an exploitation window until closed.

## Threat 6 — sequence/nonce reuse via torn or fuzzy reads
- Nonce/sequence issuance from fuzzy `sum()` or torn multi-word reads can repeat values — replayable nonces defeat exactly the protection they were issued for.
- Issue sequences from exact sources only (`AtomicLong.getAndIncrement`, locked counters); never derive issuance from metrics-grade striped sums.
- Monitor issuance for duplicates as a security signal: a repeated nonce is either ABA-class aliasing or an exactness bug — both are findings, not noise.

## Threat 7 — retry-burn amplification on attacker-paced keys
- Attackers that choose contended keys (hot accounts, single global counters) convert each request into E[A] ≈ N attempts of CPU burn — contention as a cost amplifier.
- Stripe hot security counters, shard by key, bound retries with timeouts, and shed load when CAS-failure rates spike — failure-rate metrics are the early warning.
- Rate-limit by post-commit outcomes, not by attempts: attempt-counted limits undercount real load by the retry multiplier.

## Detection
- Export CAS-failure rates per hot atomic (failure counters in hand loops or JFR-adjacent metrics): steps after deploys name the newly contended word.
- Alert on `sum()`-vs-quiescent divergence for enforcement-adjacent totals: persistent divergence means something enforces from fuzz.
- Review every `AtomicStampedReference` upgrade path for stamp overflow discipline and Pair-allocation pressure — stamps are monotonic assumptions with memory cost.
- Fuzz lock-free structures with randomized thread starts and node-reuse stress; ABA manifests under jitter while passing serene CI.

## Checklist additions
- [ ] No check-then-act across CAS gaps on auth/policy paths.
- [ ] Sequences/nonces issued from exact sources only.
- [ ] ABA handled everywhere identity history affects safety.
- [ ] Enforcement totals exact; adder sums dashboards-only.
- [ ] CAS-failure rates metered, alerted, and load-shedding wired.
