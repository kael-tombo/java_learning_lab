# Vision — CI/CD Pipelines

## Why this lab exists
CI/CD is the nervous system of a delivery team. When it is slow or
untrusted, every other practice (small batches, safe deploys) degrades.

## What we are building toward
- Every push is built, tested, and packaged automatically.
- Deployments are routine, reversible, and boring.
- Feedback arrives in minutes, not after a standup.

## Principles
- Trunk-based development with small merges.
- Fail fast: lint and unit tests before heavy integration stages.
- Pipelines as code, versioned with the app.
- Gates for risk, not bureaucracy: automated checks beat approvals.

## Anti-patterns to retire
- "Works on my machine" test runs done manually before merge.
- Pipelines that take 45 minutes and nobody waits.
- Deploy scripts on a Jenkins node nobody documents.
- Clicking through a GUI to release.

## Success criteria
- A merge to main always triggers a green or loudly-red pipeline.
- Rollback is a pipeline run, not an SSH session.
- Pipeline YAML lives next to application code.

## Looking ahead
Advanced CI/CD (lab 18) and GitOps (lab 12) extend this into progressive
delivery and declarative deploys.
