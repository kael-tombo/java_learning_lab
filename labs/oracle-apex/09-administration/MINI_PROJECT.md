# Lab 09: Administration — Mini Project

## Goal
Take an APEX instance from default configuration to a managed platform state in
90 minutes — isolated workspaces, hardened posture, monitoring, and a tested
restore.

## Requirements
- R1: A new workspace with its own schema and no cross-schema access.
- R2: An instance password policy with complexity and lockout, verified.
- R3: Session limits and an HTTPS requirement enforced.
- R4: An outbound allow-list restricting external calls to approved hosts.
- R5: A monitoring view over the APEX activity log.
- R6: A declarative application export and a database backup, both restored.
- R7: A pre-upgrade checklist.
- R8: A diagnostic query locating a slow page from the activity log.

## Steps
1. Create a schema and a workspace pointing at it.
2. Create two workspaces and prove neither can read the other's schema.
3. Set the password policy; attempt repeated login failures and confirm lockout.
4. Set the session limit and an HTTPS requirement.
5. Restrict outbound access to two approved hosts.
6. Build the activity log monitoring view.
7. Export an application declaratively and re-import it to a new workspace.
8. Take a database backup and restore it to a test schema.
9. Write the pre-upgrade checklist and locate a slow page from the log.

## Acceptance criteria
- Neither workspace can read the other's objects.
- Lockout triggers after the configured attempt count.
- HTTPS is required and HTTP is refused.
- Outbound calls to a non-allow-listed host are blocked.
- The exported application re-imports and runs.
- The restore completes and the data is verified.

## Stretch
- Produce a report of the top ten slowest pages over the last week.
- Demonstrate recovery of the full instance from backup plus export.