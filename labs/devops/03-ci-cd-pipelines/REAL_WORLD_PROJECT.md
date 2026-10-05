# Real-World Project — CI/CD Pipelines

## Scenario
A fintech team deploys monthly because releases are scary: manual
checklists, weekend windows, and frequent failed rollouts.

## Requirements
- Any commit can be deployed to staging automatically.
- Production deploys behind an explicit gate.
- Mean time to recovery under 15 minutes.
- Audit trail of who deployed what, when.

## Phase plan
1. **Map the current path**: document every manual step from commit to prod.
2. **Automate the happy path**: build, test, package, deploy to staging
   on every merge.
3. **Add quality gates**: unit tests, SAST scan, image vulnerability scan.
4. **Version artifacts**: every artifact immutable and traceable to a SHA.
5. **Deploy strategy**: start with rolling; plan canary for riskier services.
6. **Rollback rehearsal**: prove rollback is one command / one click.

## Deliverables
- Pipeline YAML committed to the repo.
- Deployment handbook with rollback instructions.
- Metrics dashboard: lead time, deploy frequency, failure rate.

## Risks & mitigations
- Flaky tests block everyone → quarantine list + retry policy.
- Big-bang migration → move one service first, iterate.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- GitHub Actions docs — workflow syntax:
  https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- GitLab CI/CD docs — pipelines:
  https://docs.gitlab.com/ee/ci/pipelines.html

## Definition of done
- Staging deploy on every merge.
- Prod deploy gated, logged, and reversible.
- Lead time for changes reduced and measured.
