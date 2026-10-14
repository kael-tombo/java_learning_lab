# REAL_WORLD_PROJECT — Bloom Filter Variants
> Compromised-token blocklist service: Bloom-filtered login path with measured FPR, rebuild pipeline, and saturation guard.

## System and inputs
- Blocklist of revoked token ids (up to 5M) published hourly as a versioned bit array plus (m, k, seed) manifest.
- Login path checks membership locally; positives fall through to the exact store, negatives skip it.
- Disjoint canary set of 50k never-issued ids ships with each build to measure live FPR.

## Design
- Builder sizes m from the FPR budget via the standard formula and picks k = round((m/n) ln 2); manifest records all three.
- Edge nodes atomically swap to the new version; exact store handles only filter positives.
- Saturation guard: estimated fill ratio tracked per build; builds past the design n trigger a resize recommendation.

## Metrics
- Measured canary FPR per version vs theoretical value from the manifest.
- Exact-store fall-through rate (should track the FPR) and added p95 login latency.
- Build time and bit-array bytes per version.
- Saturation: current n vs design n per build.

## Failure modes
- Saturated filter (n 3x design): FPR climbs; guard pages and recommends m doubling, served with the degraded filter meanwhile.
- Manifest/version skew (node serves old filter): version header on every check; mismatch forces refresh before serving.
- Hash-seed reuse across versions weakening rotation: seeds derived per version from a master plus version id.
- Exact-store outage: fail-open policy documented (negatives still skip, positives temporarily allowed with alert) — a product decision, logged.

## Rollout
1. Dark launch: build filters, measure canary FPR, serve zero traffic from them.
2. 10 percent of logins consult the filter; compare fall-through vs prediction.
3. Full rollout with hourly rebuilds and the saturation guard armed.

## Acceptance criteria
1. Reference sizing (m=1000, n=100, k=7) reproduces fpr 0.008194 in the builder's own calculator.
2. Canary FPR per version is dashboarded beside the theoretical value.
3. Saturation guard fires on a synthetic 3x-n build in staging.
4. Version skew test: stale node refreshes before serving.
5. Rollback pins the previous filter version in one config change.

## Cost and contract notes
- Exact-store cost avoided per negative: fall-through rate times lookup cost, reported monthly against filter build cost.
- Filter bytes per version tracked against the m budget; growth beyond 2x triggers the resize recommendation automatically.
- Manifest (m, k, seed, version, n-design) is immutable per version and archived with the bit array for audits.
- Login-path contract: membership check contributes at most the agreed microsecond budget at p99, measured per deploy.
