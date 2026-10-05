# Vision — Cloud Deployment

## Why this lab exists
Every cloud offers a thousand knobs; this lab builds judgment about
which ones matter for reliability, cost, and speed.

## What we are building toward
- Environments that can be rebuilt from code.
- Clear boundaries between ephemeral and durable resources.
- Cost and reliability treated as first-class requirements.

## Principles
- Automate everything beyond the first manual run.
- Design for region/zone failure from day one.
- Managed services by default; self-managed by exception.
- Tag everything for cost allocation.

## Anti-patterns to retire
- Snowflake VMs nobody can rebuild.
- Single-zone deployments "for now".
- Console clicks as the deployment process.

## Success criteria
- Can describe a reference architecture for a small service: VPC, compute,
  database, IAM, logging.
- Can reason about where data lives and how it's backed up.
- Knows the blast radius of a region outage.

## Looking ahead
Terraform (lab 04/15) is the workhorse here; secrets and config labs
finish the picture.
