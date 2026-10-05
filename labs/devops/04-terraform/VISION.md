# Vision — Terraform

## Why this lab exists
Infrastructure by hand does not scale and cannot be reviewed. Terraform
turns infrastructure into code you can diff, test, and roll back.

## What we are building toward
- Environments described declaratively and reproducibly.
- `plan` as a reviewable artifact in every PR.
- State treated as a critical, protected asset.

## Principles
- Infrastructure is code: versioned, reviewed, retested.
- Small, composable modules over monolithic configs.
- Drift is detected, not discovered during an incident.
- Remote state, locked, and backed up.

## Anti-patterns to retire
- Clicking through the cloud console to "fix" something.
- Local state files on laptops.
- One giant `main.tf` for every environment.
- `terraform apply -auto-approve` in production by default.

## Success criteria
- `terraform plan` runs in CI for every change.
- A fresh workspace can reproduce an environment from zero.
- State loss is scary but recoverable — you have tested it.

## Looking ahead
Terraform advanced (lab 15) covers workspaces, remote backends, and
policy-as-code guardrails.
