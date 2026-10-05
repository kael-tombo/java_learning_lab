# Mini Project — Terraform Advanced

## Goal
Refactor a flat Terraform config into modules with for_each over
environments, plus a policy check in CI.

## Steps
1. Take lab 04's config and extract a VPC module.
2. Rewrite the root to instantiate it twice via `for_each` over dev/prod.
3. Add remote backend + state locking (local simulation OK).
4. Add `terraform validate` and `tflint` to a pre-commit script.
5. Add conftest/OPA check: cost-tag on every resource.
6. Use `moved` blocks to reorganize without a resource replacement plan.
7. Confirm `plan` shows only the intended diff.

## Acceptance criteria
- Module reused across two environments.
- Policy check blocks an untagged resource.
- No unintended replacements in plan.

## Stretch goals
- Add a workspaces-based variant and compare.
- Write a Sentinel policy instead of conftest.

## Estimated time
75 minutes.
