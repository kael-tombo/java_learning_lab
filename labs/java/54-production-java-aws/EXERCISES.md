# EXERCISES — AWS

## 1. IRSA proof (beginner)
Deploy a debug pod with the annotated ServiceAccount; `sts
get-caller-identity` must show the role. Break the OIDC trust (wrong
issuer), record the exact error, restore. *Reflection: why is this better
than env-baked keys in three specific failure modes?*

## 2. Readiness-gated rollout (beginner)
Point readiness at a black-holed DB; roll; show ALB keeping old pods +
new pods OutOfService. Fix; watch the batch flip. Explain why liveness
alone would have caused an outage here.

## 3. PITR drill (intermediate)
Snapshot timestamp T; write canary rows; delete them; restore-to-point
(T+5 min) into a *new* cluster; diff. Record RPO achieved vs the ≤5 min
claim. Document every click for the runbook.

## 4. HPA under queue saturation (intermediate)
Load-test with slow downstream (parked threads, low CPU, rising p99).
Show CPU-only HPA flatlining while latency-HPA scales. Derive the
per-pod concurrency number your targets assume.

## 5. Graviton verdict (advanced)
Run the lab-53 benchmark (throughput + p99 + $/M-req) on m7g vs m7i
nodes at equal pod specs. Publish the table + node recommendation with
the crypto-path caveat quantified.
