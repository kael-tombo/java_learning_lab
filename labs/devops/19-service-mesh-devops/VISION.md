# Vision — Service Mesh (DevOps Focus)

## Why this lab exists
Lab 08 introduced meshes; this lab treats the mesh itself as production
infrastructure that needs operations, upgrades, and care.

## What we are building toward
- A mesh you can upgrade without drama.
- Clear ownership between app teams and platform.
- Runbooks for the failure modes only meshes have.

## Principles
- The mesh is production software — version, test, stage it.
- Start simple (observability), earn complexity (L7 policy).
- Measure proxy overhead as a budget line.

## Anti-patterns to retire
- "Set it and forget it" mesh upgrades.
- L7 rules that nobody owns.
- Debugging timeouts by restarting pods.

## Success criteria
- Can explain sidecar vs sidecarless/ambient modes.
- Can tune retries/timeouts without causing cascades.
- Can upgrade the control plane with a rollback plan.

## Looking ahead
Platform engineering (lab 20) productizes self-service mesh features.
