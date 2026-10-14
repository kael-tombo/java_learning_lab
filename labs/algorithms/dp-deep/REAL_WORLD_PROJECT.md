# REAL_WORLD_PROJECT — DP Deep Track
> Territory-realignment service: tree-DP districting over an adjacency tree with digit-DP quota validation and bitmask-DP exact checks on small zones.

## System and inputs
- Zone adjacency graph (spanning tree extracted per run) with population per node; district count K and population tolerance band.
- Quota rules expressed as digit/property constraints on district codes validated by digit DP.
- Small zones (<= 14 units) solved exactly by bitmask DP as the correctness anchor for the heuristic on large zones.

## Design
- Tree DP partitions the spanning tree into K balanced connected districts; rerooting pass scores all-root variants for the capital-placement subquery.
- Digit-DP validator checks every emitted district code against quota rules before publish.
- Large-zone heuristic (local swaps from the tree-DP start) must match bitmask-DP optima on all small-zone nightly checks.

## Metrics
- Population imbalance (max deviation from ideal) per published plan.
- Heuristic-vs-exact agreement rate on small zones (must stay 100 percent).
- Validator rejection rate with rule-level breakdown.
- Runtime vs node count for next-census capacity planning.

## Failure modes
- Non-tree adjacency (cycles from new roads): spanning-tree extraction logged with dropped edges listed; plan notes the approximation.
- Infeasible tolerance band: solver reports the nearest feasible band instead of an empty plan.
- Validator rule change mid-cycle: versioned rules; plans embed the rule version.
- Heuristic drift on small zones: nightly exact check pages on first mismatch and freezes publishing.

## Rollout
1. Re-district last census data; compare imbalance vs the adopted plan.
2. Publish one advisory (non-binding) plan with the agreement dashboard.
3. Binding use with frozen rules and the exact-check gate armed.

## Acceptance criteria
1. 7-node reference tree solves through the service path matching brute force.
2. Small-zone nightly check compares heuristic vs bitmask DP with zero tolerance.
3. Infeasible-band test returns the nearest feasible band, not an empty plan.
4. Rule-version test rejects stale-rule plans at publish time.
5. Rollback restores the previous published plan with its rule version intact.

## Cost and contract notes
- Plan reviews costed per cycle; exact-check compute on small zones is the cheapest insurance in the pipeline.
- Imbalance deviations priced per district against the tolerance band for public reporting.
- Rule-version changes trigger revalidation billing; plans embed versions so reruns are comparable.
- Contract: published plans carry (snapshot hash, rule version, imbalance, agreement receipt).
