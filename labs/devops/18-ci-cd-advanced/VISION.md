# Vision — CI/CD Advanced

## Why this lab exists
Basic pipelines build and deploy. Advanced pipelines reduce risk with
progressive delivery, security gates, and reliable feedback loops.

## What we are building toward
- Canary and blue/green releases as standard.
- Supply-chain checks (signing, SBOM, scan) in every build.
- Releases that can roll back in seconds.

## Principles
- Every deploy ships with a rollback plan.
- Trust artifacts, not processes: sign everything.
- Progressive exposure over big bangs.

## Anti-patterns to retire
- "We'll just deploy on Friday and fix forward."
- Unsigned images pulled from anywhere.
- Monolithic pipelines with no stages to reuse.

## Success criteria
- Can configure a canary with automatic rollback on error rate.
- Can emit an SBOM and verify a signature.
- Can explain staging vs production gate parity.

## Looking ahead
Service mesh and Argo Rollouts slot in naturally as the traffic plane.
