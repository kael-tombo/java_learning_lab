# VISION — Lab 16: Cost Engineering & Cloud Optimization

> From "the cloud bill is high" to "here is our cost per order, here is the 40% we wasted, and here is what we will not cut."

---

## The Arc

1. **Where the money actually goes** — compute, egress, storage, managed services, and idle waste, measured not assumed.
2. **Utilisation versus allocation** — the only dashboard that matters for rightsizing.
3. **Node density** — why memory footprint, not CPU, drives node count.
4. **The billing model** — requests vs usage, and how it changes the whole strategy.
5. **Idle environments** — the largest and easiest recoverable category.
6. **Spot and commitment strategy** — which workloads tolerate interruption, priced against the interruption cost.
7. **JVM-specific levers** — heap vs live set, allocation rate, native footprint, GC trade-offs.
8. **Traffic-shaped costs** — egress, ingress, logging, metrics cardinality.
9. **Managed services and storage growth** — right-sizing, read replicas you do not use, lifecycle policies.
10. **Process and attribution** — tags, unit economics, anomaly alerting, and the sequence that does not cut reliability.

---

## Why this lab exists

Cloud cost is the one engineering budget that is large, variable, and mostly invisible until the invoice arrives. Most teams respond to a bill by cutting something arbitrary — usually headroom — rather than by removing measured waste.

The specific goal here: **you can produce a per-unit cost metric, quantify waste before optimising anything, and sequence savings so that reliability is improved rather than traded away.**

---

## Milestones (checkable)

- [ ] M1: Produce a cost breakdown for a real platform, with a per-service and per-environment attribution, and the shared-cost allocation rule stated.
- [ ] M2: Compute cost per unit of business volume and show how it differs from month-over-month spend.
- [ ] M3: Build the `actual / requested` distribution for every service, and quantify the total waste in vCPU-hours and GiB.
- [ ] M4: Rightsize one real service end to end (JVM heap → pod request → node count), measure the node and cost reduction, and prove the SLO is unchanged under load.
- [ ] M5: Shut down (or scale to zero) a non-production environment and measure the saving and the developer's cost of the change.
- [ ] M6: Classify every workload as spot-safe or not, with the expected-interruption-cost arithmetic for each class.
- [ ] M7: Add cost anomaly alerts and per-service budgets, and verify they catch an injected runaway.

---

## Anti-Goals

- Cutting headroom first.
- Right-sizing without peak-window measurement.
- Treating monthly spend as the success metric.
- Spot for singletons, databases, or latency-critical singletons.
- Cross-region traffic nobody intended.
- Verbose logging at full retention.
- Over-requested memory because "the heap might need it".
- A cost change with no measured before/after.
- Cutting observability, backups, or failover to save money.

---

## Interview Lens

- "Our bill went up 20%. How do you find out why?"
- "How do you attribute cost to a team?"
- "What is the first thing you would optimise, and why?"
- "When would you use spot for a Java workload?"
- "How do you know a cost optimisation did not hurt reliability?"

---

## 30-Day Plan

- **Week 1** — THEORY + `FINOPS_SPOT_INTERRUPTION_DAEMON`: cost drivers, utilisation vs allocation, attribution, billing models. M1–M2.
- **Week 2** — EXERCISES: density math, egress math, log-volume math, spot decision arithmetic; QUIZ to 13/15; FLASHCARDS daily. M3.
- **Week 3** — MINI_PROJECT: rightsize a service, shut down an environment, classify spot workloads, add anomaly alerts. M4–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a cost plan for a real platform; teach-back: "our cost per order, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A cost breakdown with per-service and per-environment attribution and a stated allocation rule.
2. A `actual / requested` distribution chart with the waste quantified.
3. A rightsizing proposal with the node-count and dollar delta and a load test proving the SLO is unchanged.
4. A spot classification table with interruption-cost arithmetic.
5. Cost anomaly alerts and per-service budgets, demonstrated catching an injected runaway.
6. A cost-per-unit metric with three months of trend.

---

## Done = You Can

- Say where the money goes, with numbers, and what fraction is waste.
- Explain why memory rightsizing is often the biggest structural lever.
- Distinguish waste removal from headroom reduction, and sequence them correctly.
- Justify a spot decision per workload rather than as a blanket policy.
