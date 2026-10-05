# Vision — Helm

## Why this lab exists
Raw Kubernetes manifests don't scale across environments. Helm gives
packaging, versioning, and templating to cluster config.

## What we are building toward
- One chart deploys any environment with a values overlay.
- Releases are versioned, auditable, and reversible.
- Charts are tested like code, not clicked together.

## Principles
- Charts are artifacts: published, versioned, immutable.
- Values files per environment; never edit templates per env.
- `helm template` output reviewed before install.
- Rollback is a first-class operation.

## Anti-patterns to retire
- Hand-editing deployed manifests with kubectl.
- Different charts per environment with divergent logic.
- No version pinning — charts upgraded by surprise.

## Success criteria
- `helm install` works from a clean machine.
- `helm history` shows every release and its chart version.
- Same chart + different values yields dev vs prod correctly.

## Looking ahead
Helm advanced (lab 14) adds subcharts, hooks, and chart testing.
