# GCP Fundamentals - Vision

## The Big Picture
GCP organises around projects, and almost every permission question reduces to "which project,
which service account". Resource hierarchy, IAM, and service accounts are the spine; compute,
storage, and Kubernetes are the services hanging off it.

## Why This Matters
GCP's default posture is safer than most — compute instances have no external IP by default
and service accounts replace SSH keys — but only if you keep those defaults. The labs are
about keeping them.

## The Vision for This Lab
This lab builds a GCP service from Java using the project hierarchy and service accounts,
deploys to Compute Engine, Cloud SQL, and GKE, and covers the IAM model that makes it all
auditable.

## Learning Philosophy
1. Project is the unit of isolation, quota, and billing
2. Service accounts, not SSH keys or static API keys
3. The default-deny network posture is worth preserving deliberately
4. Least privilege at the resource level, not just the project level

## Future Path
- 14-multi-cloud — the portable subset across all three clouds
- 15-cloud-cost-optimization — committed use and budget controls
- 07-kubernetes — GKE specifics

## Success Metrics
You have mastered GCP fundamentals when you can:
- [ ] Create a project with labels and explain what labels control
- [ ] Provision a Compute Engine instance with no external IP and reach it via IAP or bastion
- [ ] Grant roles at the resource level and justify the choice
- [ ] Deploy a workload to GKE with workload identity

## The Cloud Mindset
> GCP's best habits are its defaults: no external IPs, service-account auth, least-privilege
roles. The engineering work here is resisting the urge to make things convenient.