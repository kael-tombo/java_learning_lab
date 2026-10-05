# Real-World Project — Cloud Deployment

## Scenario
Your startup's production runs on one VM someone set up on a Friday
night. It works, until it doesn't, and nobody is sure what it contains.

## Requirements
- Reference architecture: VPC, managed DB, autoscaling compute, TLS.
- Everything reproducible via IaC in under 30 minutes.
- Backups and a tested restore path.
- Budget alerts and tags on every resource.

## Phase plan
1. **Discover**: document what exists today (compute, data, DNS, IAM).
2. **Design**: target architecture diagram with failure domains noted.
3. **Build**: Terraform modules for network, compute, data, IAM.
4. **Migrate**: blue/green — new environment alongside the old, switch DNS.
5. **Harden**: private subnets, least-privilege IAM, encryption at rest.
6. **Operate**: backups, restore test, cost dashboard review.

## Deliverables
- Architecture diagram and IaC repo.
- Migration runbook executed once.
- Restore drill evidence.

## Risks & mitigations
- Data migration downtime → replication or snapshot-based move.
- Cost surprises → budgets and alerts before cutover.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- AWS Well-Architected Framework — reliability pillar:
  https://aws.amazon.com/architecture/well-architected/
- Google Cloud docs — resource hierarchy and IAM:
  https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy

## Definition of done
- Production rebuilt from code in a new account/region successfully.
- Restore drill passed.
- Monthly cost report reviewed.
