# Vision — GitOps

## Why this lab exists
If git is where the truth lives, deployments should read from git too —
not from someone's laptop with kubectl.

## What we are building toward
- Cluster state that always converges to a git repo.
- Drift detected and corrected automatically, not by a meeting.
- Every change to prod is a reviewed commit.

## Principles
- Git as the single source of truth for declarative state.
- Operators watch git and apply; humans don't touch prod directly.
- Reconciliation loops over push scripts.

## Anti-patterns to retire
- `kubectl apply` from laptops in prod.
- Deploy logs living in chat instead of commit history.
- Manual hotfixes that never get committed.

## Success criteria
- A PR merge to the config repo triggers a cluster change.
- Hand edits to cluster state self-heal.
- Can explain the reconciliation loop and when it runs.

## Looking ahead
Lab 13 (gitops-argocd) goes deep on Argo CD; advanced labs cover
progressive delivery on top.
