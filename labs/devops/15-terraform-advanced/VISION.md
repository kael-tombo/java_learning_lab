# Vision — Terraform Advanced

## Why this lab exists
Basic Terraform creates resources. Advanced Terraform manages
organizations: many accounts, many environments, safe changes at scale.

## What we are building toward
- Reusable modules consumed across teams.
- Policy-as-code gating every change.
- Workflows that scale from one env to hundreds.

## Principles
- Compose infrastructure from versioned modules.
- Separate state per blast radius.
- Policy gates in CI, not review checklists.
- Every apply traceable to a PR.

## Anti-patterns to retire
- One state file for everything.
- Modules that wrap entire environments.
- `-target` as a routine workflow.

## Success criteria
- Can structure a root module using shared modules and for_each.
- Can apply OPA/Sentinel-style policy checks in CI.
- Can use moved blocks and imports to refactor safely.

## Looking ahead
Packer baking and platform engineering labs depend on this discipline.
