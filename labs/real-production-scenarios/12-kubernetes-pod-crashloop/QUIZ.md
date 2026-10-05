# Lab 12 — Quiz: Pod CrashLoop (15 Questions)

1. CrashLoopBackOff means?
- [ ] A) Container repeatedly starts then exits non-zero, kubelet backs off
- [ ] B) Image cannot be pulled
- [ ] C) Node is NotReady
- [ ] D) Service has no endpoints
> Answer: A

2. First two commands?
- [ ] A) describe pod + logs --previous
- [ ] B) delete namespace + reboot node
- [ ] C) scale to zero + apply latest
- [ ] D) cordon node + drain
> Answer: A

3. Exit 137 means?
- [ ] A) OOMKilled (memory limit / node pressure)
- [ ] B) Success
- [ ] C) Config typo
- [ ] D) DNS failure
> Answer: A

4. Exit 143 commonly?
- [ ] A) SIGTERM (probe kill / scale-down race)
- [ ] B) Segfault
- [ ] C) Permission denied
- [ ] D) Image missing
> Answer: A

5. Which probe should tolerate slow JVM start?
- [ ] A) startupProbe
- [ ] B) No probes at all
- [ ] C) Liveness with 1s delay
- [ ] D) ServiceMonitor
> Answer: A

6. Liveness vs readiness?
- [ ] A) Liveness restarts dead process; readiness removes from service
- [ ] B) Same thing
- [ ] C) Readiness restarts pods
- [ ] D) Liveness adds to service
> Answer: A

7. Best restart metric?
- [ ] A) increase(kube_pod_container_status_restarts_total[15m])
- [ ] B) container_cpu_usage
- [ ] C) kube_node_status_ready
- [ ] D) http_requests_total
> Answer: A

8. `latest` tag risk?
- [ ] A) Non-reproducible rollouts, surprise crashes
- [ ] B) Faster pulls always
- [ ] C) Better security
- [ ] D) No risk
> Answer: A

9. `ImagePullBackOff` differs because?
- [ ] A) Container never started; registry/auth issue
- [ ] B) App panicked
- [ ] C) OOM
- [ ] D) Probe failed
> Answer: A

10. Correlate crash with deploy via?
- [ ] A) kubectl rollout history
- [ ] B) kubectl top nodes
- [ ] C) docker login
- [ ] D) helm list only
> Answer: A

11. Aggressive liveness on slow starter causes?
- [ ] A) Premature kills → CrashLoop
- [ ] B) Faster startup
- [ ] C) Lower memory
- [ ] D) Better caching
> Answer: A

12. Fix for missing env crash?
- [ ] A) Fail-fast validation + required-env check in CI
- [ ] B) Delete probes
- [ ] C) Use hostNetwork
- [ ] D) Bigger nodes only
> Answer: A

13. Graceful shutdown needs?
- [ ] A) preStop + SIGTERM handling
- [ ] B) Always kill -9
- [ ] C) No probes
- [ ] D) Privileged pods
> Answer: A

14. Fastest safe mitigation for bad deploy?
- [ ] A) kubectl rollout undo
- [ ] B) Edit code in prod pod
- [ ] C) Delete cluster
- [ ] D) Wait hours
> Answer: A

15. Prevention gate?
- [ ] A) Require probes + limits + pinned digest in CI/policy
- [ ] B) Allow any YAML
- [ ] C) Disable monitoring
- [ ] D) Deploy Fridays manually
> Answer: A

Scoring: 13–15 excellent, 10–12 good, <10 review THEORY + CODE_DEEP_DIVE.
