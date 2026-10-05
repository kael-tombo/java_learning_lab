# EXERCISES — Lab 06: Production Deployment Rollback

## Exercise 1: Identify the Canary Gap (15 min)
Given canary 15 min at 5% traffic missed an NPE that appears at 100% peak load:
- List 3 reasons the canary missed it (duration, traffic mix, cache-cold race).
- Propose canary 30 min + peak-cover + min 2000 requests rule.
- Success: written canary promotion criteria with stat test named.

## Exercise 2: Null-Guard the Cache Path (20 min)
Code has `prefs = client.getPreferences(id); prefs.getTheme();` where client may return null.
- Add `Optional` / null-check + fallback to defaults + metric increment.
- Write unit test for null, empty, exception cases.
- Success: no NPE; fallback returns safe defaults; test passes.

## Exercise 3: Add a Kill-Switch Flag (20 min)
Wrap new cache path in `pref-cache-v2` flag.
- Default OFF; enable for 1% of users; log flag evaluation.
- Practice kill: disable flag and confirm old path serves.
- Success: toggle changes path without redeploy; dashboard shows flag status.

## Exercise 4: Automated Rollback Trigger (20 min)
Write pipeline step: if error rate >1% for 2 consecutive minutes → `kubectl rollout undo`.
- Express as PromQL alert + pipeline YAML pseudo-step.
- Include cooldown and notification.
- Success: alert fires in staging simulation; rollback command logged.

## Exercise 5: Diagnose with kubectl (15 min)
Given 12/48 pods CrashLoopBackOff after deploy:
- Run `rollout history`, `describe pod`, `logs --previous`, `get events --sort-by`.
- Correlate image tag with error onset.
- Success: timeline pinpoints bad ReplicaSet revision.

## Exercise 6: Fix Connection Draining (20 min)
Rollback took 33 min due to drain misconfig.
- Set `terminationGracePeriodSeconds: 60`, `preStop: sleep 20`, correct readiness probe.
- Verify endpoints drain: watch `kubectl get endpoints` during rollout.
- Success: drain completes <90s; no stuck terminating pods.

## Exercise 7: Blue-Green vs Rolling Decision (15 min)
Compare rollback time and cost for this fleet (48 nodes, 3 regions).
- Fill table: time, capacity cost, DB-migration compatibility.
- Recommend blue-green for stateless web tier.
- Success: one-paragraph recommendation with numbers.

## Exercise 8: Error-Budget Gate (15 min)
SLO 99.95% (21.6 min/month); incident burned 47 min.
- Compute budget consumed (217%) and deploy-freeze rule.
- Draft freeze notice to stakeholders.
- Success: correct math + freeze/unfreeze criteria.

## Exercise 9: Blameless Post-Mortem Draft (20 min)
Write 5-Whys ending at pipeline gap, not individual blame.
- List 3 action items with owners + due dates.
- Success: no person named as cause; systemic fixes only.

## Exercise 10: Rollback Drill Tabletop (20 min)
Simulate: canary 5% shows 0.5% errors (baseline 0.1%), p95 +50%.
- Decide: promote / hold / rollback with rationale.
- List 2 extra signals needed (traffic volume, per-pod breakdown).
- Success: decision + rollback command stated in <5 min simulated.
