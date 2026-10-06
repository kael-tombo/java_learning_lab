# Lab 01: EBS Multi-Tier Architecture — Vision

## Where this lab takes you
From sizing a single application-tier node to running a 5,000-user, three-region
EBS R12.2 estate with RAC, Data Guard, and rolling `adop` cutovers.

## The Arc
1. **Topology** — split-tier model: application tier (OHS, Forms, OAF, CM, Admin)
   separated from the database tier, with a desktop/tier-1 client edge.
2. **Capacity** — turn user counts into Forms processes, OAF threads, CM workers
   and RAC service goals.
3. **Resilience** — clustering, load balancing, RAC services, Data Guard, FAN.
4. **Change** — FS_CLONE dual file systems and region-by-region cutover.
5. **Operate** — monitoring queries that tell you which tier is actually hurting.

## Milestones (checkable)
- [ ] M1: Draw the three-region topology naming every service per node.
- [ ] M2: Size Forms/OAF/CM for 5,000 users and justify each ratio.
- [ ] M3: Configure F5 pools with the correct persistence per traffic type.
- [ ] M4: Create ONLINE and BATCH RAC services with distinct goals.
- [ ] M5: Write the Data Guard SYNC + Fast-Start Failover configuration.
- [ ] M6: Produce an `adop` rolling cutover plan with rollback steps.
- [ ] M7: Build the four monitoring queries (Forms, CM, OAF, DG lag).
- [ ] M8: Run a failover drill and record measured RTO/RPO against target.

## Anti-Goals
- Treating "the database is at 60%" as proof the app tier is healthy.
- TCP-only load balancer health checks on a Forms pool.
- Sizing CM workers from CPU alone, ignoring queue depth at month-end.
- Treating a single-queue Concurrent Manager as an acceptable steady state.

## The one-sentence thesis
EBS performance is a *tier* problem before it is a *SQL* problem — measure the
tier before you tune the statement.