# Lab 12 — Flashcards: Pod CrashLoop

| # | Front | Back |
|---|-------|------|
| 1 | CrashLoopBackOff | Repeated start→exit non-zero with backoff |
| 2 | First command | kubectl describe pod (Last State + Events) |
| 3 | Second command | kubectl logs --previous (why it died) |
| 4 | Exit 1 | App error — read stack trace |
| 5 | Exit 137 | OOMKilled — raise limit or fix leak |
| 6 | Exit 139 | Segfault — native lib / arch mismatch |
| 7 | Exit 143 | SIGTERM — probe/scale race |
| 8 | 126/127 | Permission / command not found |
| 9 | ImagePullBackOff | Never started — registry/auth/tag |
| 10 | Backoff sequence | 10s,20s,40s… capped 5 min |
| 11 | restartPolicy Deploy | Always (retries forever) |
| 12 | Liveness | Restarts dead container |
| 13 | Readiness | Removes from Service, no restart |
| 14 | startupProbe | Tolerates slow JVM start |
| 15 | Spring slow start | initialDelay + startupProbe 30×10s |
| 16 | Events command | kubectl get events --sort-by=.lastTimestamp |
| 17 | Restart metric | kube_pod_container_status_restarts_total |
| 18 | Waiting reason metric | kube_pod_container_status_waiting_reason |
| 19 | Rollback | kubectl rollout undo deploy/X |
| 20 | History | kubectl rollout history deploy/X |
| 21 | Top pods | kubectl top pods (memory pressure?) |
| 22 | OOM confirm | describe → Last State: OOMKilled |
| 23 | Missing env | Fail-fast validation + CI check |
| 24 | latest tag | Avoid — pin digest |
| 25 | Config diff | Compare ConfigMap/Secret revision |
| 26 | Local repro | docker run --rm <image> |
| 27 | Actuator endpoints | /healthz (live) vs /readyz (ready) |
| 28 | preStop | sleep 10 for graceful SIGTERM |
| 29 | Log format | JSON to stdout for --previous |
| 30 | Single vs fleet crash | One pod = node/app; all pods = bad deploy |
| 31 | Correlate deploy | Crash time ≈ rollout time |
| 32 | Canary | Catch crash before 100% rollout |
| 33 | Auto-rollback | On crash-rate SLO burn |
| 34 | requests vs limits | Request for scheduling, limit for kill |
| 35 | HPA + crash | Crashing pods skew CPU → thrash |
| 36 | exec format error | arm64 vs amd64 image mismatch |
| 37 | Port bind crash | Address already in use — wrong port/probe |
| 38 | Migration crash | Failed DB migrate on boot — gate in CI |
| 39 | Secret missing | Mount/env absent → NPE on start |
| 40 | SLI | % deploys with zero crashloop in 15 min |
| 41 | Page rule | Whole deploy crashing = page; single = ticket |
| 42 | Describe sections | State, Last State, Events, Probes, Limits |
| 43 | --previous flag | Shows last crashed container logs |
| 44 | --tail | Limit log lines for speed |
| 45 | Node pressure | Eviction looks like crash — check node |
| 46 | Kyverno/OPA | Enforce probes + limits policy |
| 47 | Digest pin | image@sha256:… reproducible |
| 48 | Chaos drill | kill -9 → self-heal <60s |
| 49 | Runbook order | describe → logs-prev → events → rollback |
| 50 | Post-mortem Q | Why didn't canary catch it? |
| 51 | JVM heap vs limit | Limit = heap + metaspace + 30% headroom |
| 52 | NPE at PostConstruct | Missing DB/secret — fail with message |
| 53 | Probe timeout | Too low → false Unhealthy kills |
| 54 | failureThreshold | Retries before probe declares failure |
| 55 | periodSeconds | Probe interval |
| 56 | Mitigation target | Rollback <5 min |
| 57 | Detection target | <2 min via restart alert |
| 58 | Log driver | Ensure previous logs retained |
| 59 | On-call habit | Check rollout history first |
| 60 | Lesson | Describe=how, logs-prev=why |
