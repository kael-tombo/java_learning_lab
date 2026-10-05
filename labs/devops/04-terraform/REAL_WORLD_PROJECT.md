# Real-World Project — Terraform

## Scenario
Your company runs infrastructure across three environments (dev, staging,
prod) created by different teams with different conventions. New hires
can't stand up a dev environment without tribal knowledge.

## Requirements
- One shared module library, versioned.
- Per-environment stacks using workspaces or directories.
- CI runs `plan` on PRs and posts the diff.
- State is remote, locked, encrypted, and backed up.

## Phase plan
1. **Inventory**: list every environment and how it was created.
2. **Module extraction**: VPC, cluster, and database modules in a
   `modules/` repo with semantic version tags.
3. **Environment stacks**: `envs/dev`, `envs/staging`, `envs/prod`
   each with its own backend config and tfvars.
4. **CI/CD**: `terraform init -backend-config=...`, `plan`, manual
   approval, `apply` with logging.
5. **Drift detection**: scheduled `plan -refresh-only` job.
6. **Disaster drill**: restore state from backup, verify `plan` is clean.

## Deliverables
- Module repo with CHANGELOG and examples.
- Environment stacks that each produce a working environment.
- Runbook for state recovery and drift response.

## Risks & mitigations
- Module sprawl → require PR reviews and version bumps.
- Big refactors → import existing resources with `terraform import`.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Terraform docs — state and remote backends:
  https://developer.hashicorp.com/terraform/language/state
- Terraform docs — modules:
  https://developer.hashicorp.com/terraform/language/modules

## Definition of done
- New dev environment provisioned in under 15 minutes.
- `plan` clean on all environments.
- State recovery drill passed.
