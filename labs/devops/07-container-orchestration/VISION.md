# Vision — Container Orchestration

## Why this lab exists
Packaging containers is step one. Orchestration is what keeps them
scheduled, networked, and self-healing at scale.

## What we are building toward
- Declarative scaling and placement of workloads.
- Rolling, blue/green, or canary rollouts as routine.
- Cluster health visible and actionable.

## Principles
- Let the scheduler decide placement; express intent, not hosts.
- Design for failure: every node can disappear.
- Use built-in controllers before writing your own.

## Anti-patterns to retire
- SSH-ing to nodes to restart things.
- Fixed replica counts for spiky traffic.
- Custom restart scripts instead of liveness probes.

## Success criteria
- Can scale a deployment and watch the scheduler react.
- Can explain scheduling, rescheduling, and eviction.
- Knows when a PodDisruptionBudget is required.

## Looking ahead
Service mesh (lab 08) shifts traffic concerns out of apps; advanced labs
cover autoscaling deep dives.
