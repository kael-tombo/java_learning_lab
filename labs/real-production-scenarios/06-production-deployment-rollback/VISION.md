# VISION — Lab 06: On-Call Excellence in Deployments

## What Great Looks Like
- Deploys are boring: progressive, flagged, auto-guarded, reversible in minutes.
- On-call trusts the pipeline: alerts fire before customers tweet; rollback is one command.
- IC says "roll back first" without fear of blame.

## Habits
1. Check deploy markers before any error-rate alert triage.
2. Know the kill-switch name for your service by heart.
3. Test rollback monthly; record MTTR trend.
4. Keep runbook to one page: detect → decide → revert → verify.
5. Freeze when budget is red — no hero ships.

## Anti-Habits
- Lengthening canary by gut feel instead of request counts.
- Approving deploys during active SEV or depleted budget.
- Skipping flag for "tiny" changes — tiny changes cause SEV1s.

## Maturity Ladder
L0 manual kubectl → L1 pipeline + canary → L2 flags + auto-rollback → L3 blue-green + budget gates → L4 chaos-tested, <5-min MTTR.

## Interview Signal
Explain a rollback you owned: signal, decision time, command, verification, prevention. Numbers beat adjectives.
