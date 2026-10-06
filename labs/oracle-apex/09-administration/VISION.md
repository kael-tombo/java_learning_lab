# Lab 09: Administration — Vision

## Where this lab takes you
From building in APEX to running it: workspace provisioning, instance security
posture, activity monitoring, backup strategy, and upgrade lifecycle.

## The Arc
1. **Workspaces** — provisioning, schemas, and isolation between teams.
2. **Security posture** — password policy, session limits, HTTPS, outbound rules.
3. **Monitoring** — the activity log and what it can tell you.
4. **Backup** — declarative export plus database backup, and why both.
5. **Lifecycle** — patching, upgrading, and the pre-upgrade checklist.
6. **Troubleshooting** — a repeatable path from symptom to cause.

## Milestones (checkable)
- [ ] M1: Provision a workspace and schema for a new team with least privilege.
- [ ] M2: Set and verify an instance password policy and session limits.
- [ ] M3: Enforce HTTPS and restrict outbound access to an allow-list.
- [ ] M4: Build a monitoring view over the APEX activity log.
- [ ] M5: Perform a declarative export and a database backup; restore both.
- [ ] M6: Write the pre-upgrade checklist and apply a patch.
- [ ] M7: Diagnose a performance issue using the activity log.

## Anti-Goals
- Giving every workspace schema access to every other schema.
- Relying on the default password policy without testing lockout.
- Treating an application export as a backup of the database.
- Upgrading without a tested restore point.

## The one-sentence thesis
Running APEX is a different skill from building in it — isolation, posture,
observability, and a restore you have actually tested.