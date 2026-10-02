# Terraform Theory

## Core Concepts
- **Infrastructure as Code (IaC)**: Managing infrastructure through machine-readable definition files.
- **HCL**: HashiCorp Configuration Language — declarative language for defining resources.
- **Provider**: Plugin that interacts with cloud/API (AWS, GCP, Azure, Kubernetes, etc.).
- **Resource**: Infrastructure object (EC2 instance, DNS record, S3 bucket).
- **Data Source**: Read-only query of existing infrastructure.
- **State**: Snapshot of managed infrastructure stored in `terraform.tfstate`.
- **Module**: Reusable collection of resources with inputs and outputs.

## Terraform Workflow
1. **Write**: Define infrastructure in `.tf` files.
2. **Init**: Initialize working directory (`terraform init`).
3. **Plan**: Preview changes (`terraform plan`).
4. **Apply**: Execute changes (`terraform apply`).
5. **Destroy**: Remove resources (`terraform destroy`).

## Key Features
- **Execution Plans**: Show what will happen before applying.
- **Resource Graph**: Dependency graph determines parallel/sequential operations.
- **Change Automation**: Minimal changes to reach desired state.
- **State Management**: Track resource metadata across runs.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Learn Terraform recommended practices — HashiCorp Developer (living guide, accessed Oct 2026) — https://developer.hashicorp.com/terraform/cloud-docs/recommended-practices — Takeaway for write/init/plan/apply exercises: adopt collaborative infrastructure-as-code — one workflow with versioned configs and HCP Terraform workspaces to bound team ownership.
- Part 1: Overview of recommended workflow — HashiCorp Developer (2025-05-27) — https://developer.hashicorp.com/terraform/cloud-docs/recommended-practices/part1 — Takeaway for module/state exercises: one workspace per component-environment (config × environment), sharing only required outputs via remote-state/data sources to limit blast radius.
- Configuration Language Style Guide — HashiCorp Developer (2026-03-18) — https://docs.hashicorp.com/terraform/language/style — Takeaway for HCL exercises: run `terraform fmt` + `terraform validate` pre-commit, pin binary/provider/module versions, type+describe every variable/output.
- Workspace best practices — HashiCorp Developer (2026-02-02) — https://docs.hashicorp.com/terraform/enterprise/workspaces/best-practices — Takeaway for state-splitting exercises: group by volatility, stateful vs stateless, and team responsibility; keep dependency graphs small instead of raising parallelism.
