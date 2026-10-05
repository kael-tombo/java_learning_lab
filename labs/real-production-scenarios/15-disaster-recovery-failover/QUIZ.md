# Lab 15 — Quiz: DR Failover (15 Questions)

1. RPO vs RTO?
- [ ] A) RPO = max data loss; RTO = max downtime
- [ ] B) Same thing
- [ ] C) RPO = uptime; RTO = latency
- [ ] D) RPO = cost; RTO = team size
> Answer: A

2. Async replication lag directly risks?
- [ ] A) Exceeding RPO (data loss on failover)
- [ ] B) Faster reads
- [ ] C) Lower cost only
- [ ] D) Nothing
> Answer: A

3. First check before failover?
- [ ] A) Secondary lag within RPO + app verified in secondary
- [ ] B) Delete primary immediately
- [ ] C) Raise DNS TTL to 24h
- [ ] D) Skip verification to save time
> Answer: A

4. DNS TTL for failover records?
- [ ] A) ≤60s so cutover propagates fast
- [ ] B) 24h for stability
- [ ] C) Doesn't matter
- [ ] D) No DNS needed
> Answer: A

5. 3-2-1 backup rule?
- [ ] A) 3 copies, 2 media, 1 offsite
- [ ] B) 3 regions same AZ
- [ ] C) 2 backups yearly
- [ ] D) 1 copy is enough
> Answer: A

6. Backup green but restore never tested means?
- [ ] A) Assume restore fails — DR not proven
- [ ] B) DR is done
- [ ] C) RPO is zero
- [ ] D) No action needed
> Answer: A

7. Split-brain guard?
- [ ] A) Block writes on old primary after promotion
- [ ] B) Write to both primaries
- [ ] C) Ignore DNS
- [ ] D) Disable replication
> Answer: A

8. Warm standby vs pilot light?
- [ ] A) Warm = scaled-down live; pilot = core only, scale on failover
- [ ] B) Identical
- [ ] C) Warm is cheaper always
- [ ] D) Pilot is active-active
> Answer: A

9. Failback is?
- [ ] A) Planned return to primary with data-merge care
- [ ] B) Automatic and trivial
- [ ] C) Never needed
- [ ] D) Deleting secondary
> Answer: A

10. Hold (don't fail over) when?
- [ ] A) Lag exceeds RPO or secondary unverified
- [ ] B) Primary slow for 30s
- [ ] C) Always fail over instantly
- [ ] D) On any alert
> Answer: A

11. Schema drift across regions causes?
- [ ] A) Failed promotion / app errors post-cutover
- [ ] B) Faster failover
- [ ] C) Lower lag
- [ ] D) Nothing
> Answer: A

12. Best RTO evidence?
- [ ] A) Timed game-day total vs RTO
- [ ] B) Runbook page count
- [ ] C) Backup size
- [ ] D) Team seniority
> Answer: A

13. Connection strings must be?
- [ ] A) Parameterized per region, switched by config
- [ ] B) Hard-coded to primary
- [ ] C) In code comments
- [ ] D) Emailed during incident
> Answer: A

14. Incident commander role?
- [ ] A) Single failover decision-maker to avoid split-brain
- [ ] B) Takes notes only
- [ ] C) Restarts pods
- [ ] D) Optional
> Answer: A

15. DR readiness SLI?
- [ ] A) Restore fresh + lag within RPO + drill current
- [ ] B) Uptime of primary only
- [ ] C) CPU usage
- [ ] D) Ticket count
> Answer: A

Scoring: 13–15 excellent, 10–12 good, <10 review THEORY + CODE_DEEP_DIVE.
