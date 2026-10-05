# QUIZ — Lab 06: Production Deployment Rollback (15 questions)

1. What % of prod incidents are change-induced per Google SRE lore?
- A) ~10% B) ~70% C) ~5% D) ~99% — **B**

2. Correct first action on suspected bad deploy?
- A) Investigate 30 min B) Roll back / kill-switch first C) Restart DB D) Ignore — **B**

3. `maxUnavailable: 25%` means?
- A) 25% extra pods B) Up to 25% may be down during rollout C) 25% traffic canary D) 25% error budget — **B**

4. Why did 15-min canary miss the NPE?
- A) Too long B) Missed peak concurrency + cold-cache race C) Wrong region D) No logs — **B**

5. Kill-switch requires?
- A) Redeploy B) Runtime flag toggle, no redeploy C) DB restore D) DNS change — **B**

6. Automated rollback trigger example?
- A) Error >1% for 2 min B) CPU >10% once C) Any log line D) Manual only — **A**

7. `kubectl rollout undo` does what?
- A) Deletes cluster B) Reverts to previous ReplicaSet C) Scales to zero D) Restarts kubelet — **B**

8. Purpose of `terminationGracePeriodSeconds` + `preStop`?
- A) Faster crash B) Drain in-flight requests C) Increase CPU D) Skip probes — **B**

9. Deep readiness probe should?
- A) Return 200 always B) Exercise real dependency path C) Check disk only D) Sleep — **B**

10. SLO 99.95% monthly budget?
- A) 43.8 min B) 21.6 min C) 7 h D) 0 min — **B**

11. 47-min outage vs 21.6-min budget consumes?
- A) ~50% B) ~100% C) ~217% D) ~10% — **C**

12. Blue-green rollback is fast because?
- A) Rebuilds image B) LB flips traffic atomically C) Deletes data D) Restarts nodes — **B**

13. Expand-migrate-contract matters because?
- A) CSS B) Some DB migrations aren't reversible by deploy rollback C) Faster builds D) Cheaper — **B**

14. Deployment marker in dashboards helps?
- A) Decoration B) Correlate version change with metric shift C) Slow queries D) Billing — **B**

15. Blameless post-mortem focuses on?
- A) Who to fire B) Systemic gaps C) Hiding timeline D) Skipping actions — **B**
