# Vision — GitOps with Argo CD

## Why this lab exists
Lab 12 covered GitOps in concept; Argo CD is the tool we run it with.
This lab makes the operator concrete and operable.

## What we are building toward
- Fluency with Applications, AppProjects, and sync waves.
- RBAC-aware multi-team setups.
- Debugging sync failures as a daily skill.

## Principles
- Application CRs are also code — version them.
- Separate app-of-apps for platform vs workloads.
- Use sync waves and health checks; don't rely on timing luck.

## Anti-patterns to retire
- One giant Application with everything attached.
- Ignoring OutOfSync warnings for weeks.
- Hand-editing resources Argo CD owns.

## Success criteria
- Can read an Application CR and predict its sync behavior.
- Can explain sync policy options (automated, prune, self-heal).
- Can debug a failing sync from the UI and the CLI.

## Looking ahead
Argo Rollouts and progressive delivery extend this into canaries.
