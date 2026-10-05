# Cloud Cost Optimization - Real World Project

## Project: A FinOps Programme That Survives Contact With Developers

### Objective
Establish cost visibility and ownership across the estate, execute the largest optimisations,
and build the guardrails and review cadence that prevent the savings from being spent again
within a quarter.

### Why This Matters
Cost programmes fail for organisational reasons, not technical ones. If a team sees their
spend and cannot influence it, they disengage; if savings are not visible to the team that
earned them, the next architecture change undoes them. Governance is the actual deliverable.

### Architecture Overview
```
  Billing data ─▶ daily ingest ─▶ cost model ─▶ attribution by tag
                                            ├──▶ per-team dashboard + budget alerts
                                            ├──▶ anomaly detection (day-over-day)
                                            └──► optimisation pipeline (FinOps-as-code)
                                                      │
  IaC plan ──▶ cost estimate ──▶ policy check ──▶ deploy blocked if over budget
```

### Phase 1: Visibility and Attribution (Week 1)
1. Enable detailed billing export with tags; confirm tags reach the cost report
2. Build attribution to cost centre and service; **measure untagged spend** — this is your
   first real number and it is usually uncomfortable
3. Split the bill into the four categories that drive everything: compute, storage, data
   transfer, managed services
4. Publish a dashboard per team, showing last month, this month, and budget
5. Set budget alerts at 50%, 80%, and 100% of forecast — a single 100% alert is too late to
   act on

### Phase 2: Find the Large Money (Week 2)
Rank by size, not by ease. For each of the top five categories:
1. **Compute:** utilisation percentiles per instance family; find underused and idle capacity
2. **Storage:** orphaned volumes, unattached snapshots, over-provisioned IOPS, missing
   lifecycle rules on logs and backups
3. **Data transfer:** cross-AZ chatter from a chatty client, cross-region replication of
   data nobody reads, NAT gateway processing fees
4. **Managed services:** idle non-production environments, unused load balancers, forgotten
   log retention
5. **Commitment:** current coverage ratio against the measured steady-state baseline

Produce one table: category, current monthly, addressable amount, effort, risk. Share it
before optimising anything, so nobody argues about which change is "fairest".

### Phase 3: Execute the Changes (Weeks 3-4)
1. Start with the zero-risk items: idle resources, orphaned storage, lifecycle rules
2. Rightsize in batches with a soak period and an automatic rollback on latency regression
3. Schedule non-production environments, with an exception process for release windows
4. Purchase commitments only for the measured p5 baseline of steady-state families
5. Move batch and CI to spot **with checkpointing** — without it, spot is not usable
6. Track realised savings weekly against the forecast; the gap is the real work

### Phase 4: Prevent Regression (Week 5+)
This is where the durable value is.
1. Cost estimates in the IaC plan: an engineer sees the monthly cost of a change before
   merging it
2. A policy gate: changes that increase projected spend above a threshold require an
   explanation and an approval — an exception process, not a wall
3. Per-service budgets with alerts that reach the owning team, not a shared inbox
4. Anomaly detection: day-over-day variance beyond a threshold pages the owner with the
   likely cause, since most spikes are one team's mistake rather than an attack
5. Monthly review with each team: their spend, what changed, what they are doing about it

### Phase 5: Make It a Practice (Week 6+)
1. Tagging standards enforced at deploy; untagged resources fail the pipeline
2. Quarterly right-sizing review using the previous quarter's percentiles
3. Commitment coverage reviewed as a ratio, with the p5 baseline as the target
4. Publish realised savings per team so the benefit is visible to the people who produced it
5. Document the FinOps operating model: who owns what, and what happens when a budget is hit

### Deliverables
1. Attribution model and dashboard per team, with the untagged-spend number stated plainly
2. Ranked opportunity table: category, size, effort, risk
3. Executed optimisations with realised-versus-forecast savings reported weekly
4. Cost-estimate policy gate in IaC plus budget alerts and anomaly detection

### Success Criteria
- Untagged spend below 1%, enforced at deployment
- Realised savings within 10% of forecast after two quarters
- No cost regression on any service for two consecutive months
- Every team can explain its own bill line by line

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon EC Spot Instances —
  https://aws.amazon.com/ec2/spot/
  Use for: interruption behaviour and the checkpointing requirement that makes spot usable for
  batch workloads. Verify current interruption notice characteristics for your instance types.
- Amazon CloudWatch pricing and cost metrics —
  https://aws.amazon.com/cloudwatch/pricing/
  Use for: which metrics and logs are billed, and the volume tiers that drive ingestion cost.
  Verify current tier pricing before modelling a logging architecture.

### Estimated Time
8-10 weeks part-time