# REAL_WORLD_PROJECT — MST Variants
> Fiber-build planner: MST primary layout plus second-best backup links, costed and phased for construction crews.

## System and inputs
- Surveyed segment file: (site A, site B, build cost, terrain tag); costs versioned per survey round.
- Crew constraints: max segments per phase and terrain tags requiring specialist crews.
- Output: phased build plan with per-phase cost, backup-link list from second-best swaps, and total.

## Design
- Kruskal primary MST (union-find, deterministic tie-break by segment id for stable plans across runs).
- Second-best swap table converted to ranked backup links: each backup annotated with (added segment, replaced segment, delta cost).
- Phasing packs MST edges into crew-feasible phases; terrain tags filter which crew each phase needs.

## Metrics
- Total primary cost and backup delta per link (from the swap table, never hand-edited).
- Phase count and per-phase cost vs crew budget.
- Plan stability: diff against previous survey version (edge churn count).
- Compute time vs segment counts for the next survey round.

## Failure modes
- Disconnected survey (isolated site): planner refuses with the component list instead of a partial tree.
- Cost update mid-phase: versioned surveys; active phase keeps its version, next phase re-plans with a churn report.
- Tied weights causing plan flapping: deterministic tie-break by id; churn metric proves stability.
- Backup link sharing a trench with its primary (correlated failure): terrain-tag rule flags same-trench backups for review.

## Rollout
1. Re-plan last year's build from archived surveys; compare cost and phases vs what was built.
2. Plan one live region; crews work from phased output with the backup list on standby.
3. Adopt as the standard planner with versioned surveys mandatory.

## Acceptance criteria
1. Reference graph through the planner yields primary 8 and top backup delta +1 with the swap named.
2. Disconnected input is rejected with component details (test with an isolated vertex).
3. Tie-break test: shuffled input order gives the identical plan.
4. Churn report quantifies edge changes between two survey versions.
5. Rollback restores the previous versioned plan byte-identically.

## Cost and contract notes
- Build budget sums phased MST costs plus a contingency per terrain tag; backup deltas priced as options, not commitments.
- Survey versions diffed edge-by-edge; churn above threshold re-opens the plan review automatically.
- Crew-day estimates per phase derived from segment counts times the measured segments-per-day rate.
- Contract: planner input manifest carries survey version; outputs embed it so plans never float free of data.
