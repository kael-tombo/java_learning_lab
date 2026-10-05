# Mini Project — Argo CD

## Goal
Deploy three services via Argo CD with automated sync, prune, and
self-heal, using separate dev/prod applications.

## Steps
1. Install Argo CD via the official manifest.
2. Create an AppProject limiting allowed repos/dest namespaces.
3. Add two Applications against the same chart, different values files.
4. Enable automated sync with prune + selfHeal.
5. Push a values change; watch automatic rollout.
6. Edit a live resource with kubectl; watch it revert.
7. Introduce a bad image; observe sync failure and health status.

## Acceptance criteria
- Both environments sync from one repo.
- Self-heal reverts out-of-band edits.
- A bad change surfaces as OutOfSync/Degraded with clear events.

## Stretch goals
- Add a sync-wave ordered DB migration job.
- Configure notifications (Slack/webhook) on sync failure.

## Estimated time
60–90 minutes.
