# Mental Models for GitOps & ArgoCD

## The Git-Centric Model
Think of Git as the control plane for your infrastructure. Every change to the system is a commit. The Git repository is not just version control — it is the source of truth, the audit log, and the rollback mechanism all in one. When you understand GitOps, you start thinking in terms of commits, branches, and merges instead of deployments, rollouts, and rollbacks.

## The Desired State Model
Your infrastructure has a desired state (what you want) and an actual state (what you have). GitOps is the continuous process of making the actual state converge to the desired state. This is analogous to a thermostat: you set the temperature (desired state) and the system continuously works to maintain it.

## The Drift Model
Configuration drift is like entropy in physics — systems naturally tend toward disorder over time. Manual changes, failed automation, and partial deployments all contribute to drift. GitOps counteracts this by continuously applying negative feedback (reconciliation) to maintain order.

## The Pull vs Push Model
Traditional CI/CD is like a delivery service that brings packages to your door whether you are home or not. GitOps is like a refrigerator that you stock with groceries (configure in Git) and consume as needed. The pull model is more resilient because the cluster controls when and how changes are applied.

## The Infrastructure as Code Model
Your infrastructure configuration should be treated with the same rigor as application code: code reviews, automated testing, version tags, and release branches. Every environment (dev, staging, production) should be a branch or directory in the repository, with promotions happening through merges.

## The ApplicationSet Template Model
Think of an ApplicationSet as a factory that produces Applications from a template. The generators are the assembly line that determines what gets produced, and the template is the blueprint. This factory pattern reduces repetition and ensures consistency across environments and clusters.
