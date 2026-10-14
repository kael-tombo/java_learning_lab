# REAL_WORLD_PROJECT — Dynamic Programming Track
> Freight-loading planner: 0/1 knapsack packing per truck with edit-distance address dedup and LIS-based delay analysis on arrival sequences.

## System and inputs
- Parcel feed per depot (weight, volume, value, address text); truck capacity (weight + volume dual constraint handled by nested or scalarized capacity, documented).
- Address book for dedup via edit-distance threshold; arrival-time sequences per route for delay-trend analysis.
- Planner output per truck: pack list, fill rate, leftovers with reasons (overweight, oversize, low value density).

## Design
- Knapsack DP per truck at capped W (scalarized capacity units); instances above the cap fall back to value-density greedy with the gap logged.
- Address dedup pre-pass clusters near-duplicates (edit distance <= 2 on normalized text) so one parcel does not ship twice.
- LIS over on-time arrival flags per route surfaces the longest improving run for the weekly ops review.

## Metrics
- Fill rate per truck (weight and volume) with targets from the baseline month.
- Greedy-fallback rate and its value gap vs DP on shadow instances.
- Dedup precision sampled weekly (human review of 100 flagged pairs).
- Planner runtime vs parcel count for next-depot capacity planning.

## Failure modes
- Capacity-unit blowup (W 100x after unit change): cap guard diverts to greedy with an alert, never OOMs.
- Dual-constraint infeasibility masked by scalarization: volume overflow check post-packs; violations replan with adjusted scalarization.
- Dedup false merge (distinct addresses within distance 2): review queue plus apartment/suite-number guard rule.
- Stale address book: versioned book with weekly refresh; planner embeds the book version in outputs.

## Rollout
1. Shadow-plan one depot for a month; compare fill rate and leftovers vs human packers.
2. Live-plan one depot with the fallback armed; review dedup precision weekly.
3. Roll out per depot with capacity caps tuned from measured runtimes.

## Acceptance criteria
1. Reference knapsack instance solves through the service path with the documented optimum.
2. Cap-guard test diverts an oversized instance to greedy with a logged gap.
3. Dedup test merges true duplicates and spares the guarded distinct pair.
4. Volume-overflow test triggers replan with adjusted scalarization.
5. Rollback restores the previous planner version with identical outputs on the reference set.

## Cost and contract notes
- Planner runtime per depot sized from the parcel-count table; depots above the cap get pre-split feeds.
- Greedy-fallback value gap reported weekly in dollars of unfilled capacity, keeping the fallback honest.
- Dedup review labor (100 pairs/week) costed into the project; precision below target pauses auto-merge.
- Contract: pack lists embed address-book version and capacity-unit definition so plans stay comparable.
