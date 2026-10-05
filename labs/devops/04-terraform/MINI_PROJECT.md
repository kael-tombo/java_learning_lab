# Mini Project — Terraform

## Goal
Provision a small, real piece of infrastructure (e.g. a VPC + one VM,
or two Kubernetes namespaces) entirely with Terraform.

## Steps
1. Install Terraform (`terraform version`).
2. Create `main.tf`, `variables.tf`, `outputs.tf`.
3. Declare a provider block (AWS/GCP/Azure or local via `null`/`local`).
4. Provision one resource and output its identifier.
5. `terraform init` — download providers.
6. `terraform plan` — read the diff carefully.
7. `terraform apply` — confirm with yes.
8. Change an attribute, re-plan, apply the update.
9. `terraform destroy` — confirm everything is removed.

## Acceptance criteria
- `terraform plan` output reviewed before every apply.
- Outputs show the resource ID after apply.
- Destroy leaves zero orphaned resources.

## Stretch goals
- Use a remote backend (S3/GCS) with locking.
- Parameterize with a `.tfvars` file per environment.

## Estimated time
45–60 minutes.
