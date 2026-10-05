# Lab 12 — Exercises: Pod CrashLoop

## Part A — Diagnose (1–15)
1. `kubectl get pods -n prod` — identify CrashLoop pod.
2. `kubectl describe pod <p> -n prod` — record Last State + exit code.
3. `kubectl logs <p> -n prod --previous --tail=100` — find root exception.
4. `kubectl get events -n prod --sort-by=.lastTimestamp | tail -30` — probe vs OOM?
5. Check `kubectl top pods` vs limits for OOM suspicion.
6. Decode exit 137 vs 1 vs 143 with one-line explanation each.
7. Inspect liveness/readiness probes: `kubectl get deploy X -o yaml | grep -A8 Probe`.
8. Correlate crash start with `kubectl rollout history deploy/X`.
9. Diff ConfigMap/Secret change: `kubectl rollout history` + git log.
10. Test image locally: `docker run --rm <image> | head -50`.
11. Reproduce missing-env crash by unsetting one var in staging.
12. Tune `startupProbe` for a 60s Spring Boot start; verify no premature kill.
13. Set memory limit from heap dump + 30% headroom; document math.
14. Write PromQL: `increase(kube_pod_container_status_restarts_total[15m]) > 3`.
15. Draft page-vs-ticket rule for crashloops (single pod vs whole deploy).

## Part B — Fix & Harden (16–30)
16. Add fail-fast config validation with actionable log line.
17. Split liveness (is process dead?) vs readiness (can serve?) probes.
18. Add `startupProbe: failureThreshold: 30, periodSeconds: 10` for JVM.
19. Pin image to digest, not `latest`.
20. Add `resources.requests/limits` + `HPA` sanity check.
21. Implement `/healthz` vs `/readyz` endpoints in Spring Actuator.
22. Add preStop hook `sleep 10` for graceful SIGTERM.
23. Configure log-to-stdout JSON so `--previous` is useful.
24. Build Grafana panel: restart rate by deployment.
25. Chaos: kill -9 one pod, verify self-heal <60s.
26. Rollback drill: `kubectl rollout undo deploy/X` in <5 min.
27. Post-mortem one-pager for a 15-min CrashLoop outage.
28. SLI proposal: `% deploys with zero crashloops in first 15 min`.
29. Peer-review probe timings for a slow-start service.
30. Write runbook: describe → logs --previous → events → rollback.

Stretch: OPA/Kyverno policy requiring probes + limits on every Deployment.
