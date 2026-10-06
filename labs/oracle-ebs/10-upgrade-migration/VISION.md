# Lab 10: Upgrade & Migration — Vision

## Where this lab takes you
From 12.1 to 12.2 with `ADOP`, from on-prem to cloud, and from 11g to 19c —
three production cutovers executed inside a fixed window.

## The Arc
1. **Baseline** — know the current version, patch level, and custom footprint.
2. **Pre-req** — minimum versions and prerequisite patches, in order.
3. **Upgrade** — database upgrade, then application upgrade.
4. **Editioning** — `ADOP` phases, dual file systems, rolling cutover.
5. **Migrate** — DMS replication to cloud, cutover under 2 hours.
6. **Database** — 11.2 to 19c on RAC within an 8-hour outage.
7. **Prove it** — smoke tests, data validation, rollback readiness.

## Milestones (checkable)
- [ ] M1: Produce a customisation inventory — custom objects, forms, reports.
- [ ] M2: Build a version compatibility matrix for every component.
- [ ] M3: Execute the `ADOP` phases and explain what each one changed.
- [ ] M4: Run a rolling cutover with a written rollback for each phase.
- [ ] M5: Execute a DMS replication cutover in under 2 hours.
- [ ] M6: Complete an 11g to 19c RAC upgrade in an 8-hour window.
- [ ] M7: Run pre- and post-upgrade data validation with zero unexplained diff.
- [ ] M8: Produce the cutover runbook with named decision points.

## Anti-Goals
- Discovering custom code after the database upgrade has already run.
- Cutting over without a tested restore point.
- Treating the upgrade window as the whole plan; testing is most of the work.
- Combining a database upgrade, an app upgrade, and a migration in one window.

## The one-sentence thesis
An upgrade is a project with a database change at the end of it — the cutover
is the cheapest five percent of the work.