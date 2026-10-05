# Mini Project — Cloud Deployment

## Goal
Deploy a small app to a managed cloud service (e.g. a VM, App Service,
or Cloud Run equivalent) with infrastructure as code.

## Steps
1. Choose a provider and free-tier-friendly option.
2. Define the infrastructure in Terraform or a provider-native template.
3. Provision network, compute, and a managed database (or SQLite).
4. Deploy the app artifact built in lab 01.
5. Verify HTTPS endpoint and logs.
6. Tear down with `terraform destroy` and confirm zero billable resources.

## Acceptance criteria
- Infrastructure defined in code, not console clicks.
- App reachable over HTTPS.
- `destroy` leaves no lingering resources.

## Stretch goals
- Add autoscaling rules and trigger a scale event.
- Deploy to a second region.

## Estimated time
60–90 minutes (most of it cloud provisioning).
