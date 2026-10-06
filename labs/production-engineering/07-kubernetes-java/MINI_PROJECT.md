# Lab 07: Kubernetes for Java Architects — Mini Project

## Project: `K8sLab` — Deploy, Break, and Fix a Spring Boot Service

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Docker, minikube or kind, kubectl, JFR/JMC, `jcmd`

Build a Java service, deploy it to a real cluster with deliberately imperfect configuration, reproduce each of the five production failure modes in this lab, and fix each one with measured evidence.

---

## Part 1 — The service

A Spring Boot 3 REST service (`orders-api`) with: HikariCP → PostgreSQL, a WebClient call to a stub `pricing` service, and a slow `/report` endpoint to give you a latency tail. Every knob is an env var so experiments need no rebuild:

```yaml
server:
  port: 8080
  shutdown: graceful
  tomcat:
    threads:
      max: ${TOMCAT_MAX:200}
    accept-count: ${TOMCAT_ACCEPT:100}

spring:
  lifecycle:
    timeout-per-shutdown-phase: ${SHUTDOWN_PHASE:30s}
  datasource:
    url: jdbc:postgresql://postgres:5432/orders
    hikari:
      maximum-pool-size: ${POOL_MAX:20}
      connection-timeout: 3000

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  endpoint:
    health:
      probes:
        enabled: true
      show-details: never

app:
  warmup-delay-ms: ${WARMUP:0}      # artificial cold-start delay for probe experiments
  dependency-check: ${DEP_CHECK:true}   # readiness optionally touches pricing
```

Container entrypoint so flags are injectable:

```dockerfile
FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app
COPY target/orders-api.jar app.jar
ENV JAVA_TOOL_OPTIONS="-XX:+UseContainerSupport"
ENTRYPOINT ["sh","-c","exec java $JAVA_OPTS -jar app.jar"]
```

---

## Part 2 — Baseline manifest

Write a manifest that is *deliberately* what most teams ship, so you have something to break and fix:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
spec:
  replicas: 3
  selector:
    matchLabels: { app: orders-api }
  template:
    metadata:
      labels: { app: orders-api }
    spec:
      containers:
      - name: orders-api
        image: orders-api:1.0.0
        env:
        - name: JAVA_OPTS
          value: "-Xmx1g -Xms1g"
        ports: [{ containerPort: 8080 }]
        livenessProbe:
          httpGet: { path: /actuator/health/liveness, port: 8080 }
          initialDelaySeconds: 60
        readinessProbe:
          httpGet: { path: /actuator/health/readiness, port: 8080 }
          periodSeconds: 5
        resources:
          requests: { memory: "1Gi" }
          limits:   { memory: "2Gi" }
```

**Deliverable**: `BASELINE_AUDIT.md` listing every defect, ranked by blast radius, with the fix for each. This is your "before" document.

---

## Part 3 — Failure reproduction

### Experiment 1 — OOM-kill without an OOM

```bash
kubectl apply -f baseline.yaml
kubectl get pod -l app=orders-api -w
# then drive direct-buffer pressure
kubectl exec deploy/orders-api -- sh -c 'WARMUP=0 APP_DIRECT_MB=900 java ... '
# or simpler: set -Xmx1400m against limits 2Gi and push heap + native together
kubectl patch deploy orders-api --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/env/1/value","value":"-Xmx1400m"}]'
```

Capture evidence:
```bash
kubectl get pod -l app=orders-api -o jsonpath='{.items[*].status.containerStatuses[*].lastState}'
kubectl exec -it <pod> -- jcmd 1 VM.native_memory summary
kubectl exec -it <pod> -- cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/memory.stat | grep -E 'anon|file'
```

**Measure**: peak `memory.current` vs `limits.memory`, NMT categories, and the gap between `-Xmx` and actual RSS. **Deliverable**: a memory budget table that explains the kill to within 5%.

### Experiment 2 — Probe cascade from a slow dependency

```bash
# make pricing slow, then watch every pod restart
kubectl run slow-pricing --image=nginx -- sh -c 'while true; do printf "HTTP/1.1 200 OK\r\nContent-Length: 1000000\r\n\r\n" ; sleep 0.2; done' &
# point readiness at it
kubectl patch deploy orders-api --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/actuator/health/readiness?deps=pricing"}]'
```

Watch: `kubectl get pods -w` showing all three pods going `1/0` simultaneously, and `kubectl get events` showing `Liveness probe failed` / `Unhealthy`.

**Deliverable**: a timeline showing the simultaneous restart, the number of pods restarting per minute, and the readiness/liveness split that prevents it. Prove the fix by separating the two probes and re-running.

### Experiment 3 — Rollout that cannot schedule

Scale the workload until a rollout stalls:

```bash
kubectl scale deploy orders-api --replicas=40
kubectl set image deploy/orders-api orders-api=orders-api:1.0.1
kubectl rollout status deploy/orders-api --timeout=60s    # expect: timed out
kubectl describe deploy orders-api | tail -30            # "unavailable: 3", pending pods
kubectl get pods | grep Pending
kubectl get events --sort-by=.lastTimestamp | tail -20   # "0/N nodes available: insufficient cpu"
```

Then measure the density:
```bash
kubectl get nodes -o custom-columns='NAME:.metadata.name,ALLOC:.status.allocatable.memory'
kubectl describe node <node> | grep -A3 "Allocated resources"
```

**Deliverable**: the density arithmetic showing why 41 pods × 1 Gi requests cannot schedule, and the three resolutions (lower requests with a measured NMT floor, fewer larger pods, more nodes) with the cost of each.

### Experiment 4 — Deploy-time 502s

```bash
# point at a slow endpoint with a long timeout, then roll
kubectl set image deploy/orders-api orders-api=orders-api:1.0.2 &
./k6-run.sh 200rps 60s            # hit /report with an 8s downstream timeout
# count non-2xx during the rollout window
```

Count 502s attributable to the rollout. Then fix with `preStop` sleep + `maxUnavailable: 0` + `terminationGracePeriodSeconds`, and re-run the same load.

**Deliverable**: a before/after 502 count per rollout, with the grace-period derivation from the drain math.

### Experiment 5 — HPA oscillation

```bash
kubectl autoscale deploy orders-api --min=2 --max=40 --cpu-percent=50
kubectl get hpa orders-api -w
```

Capture the sawtooth. Then fix: correct `requests.cpu`, add `stabilizationWindowSeconds`, and switch to a custom metric.

**Deliverable**: the oscillation plot described as a table of (time, replicas, CPU%), plus the stabilized version.

---

## Part 4 — The hardened manifest

Produce `hardened.yaml` that addresses every defect:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }
  minReadySeconds: 10
  progressDeadlineSeconds: 300
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels: { app: orders-api }
      securityContext:
        runAsNonRoot: true
        seccompProfile: { type: RuntimeDefault }
      containers:
      - name: orders-api
        image: orders-api:1.0.0        # pinned by digest in the real pipeline
        env:
        - name: JAVA_OPTS
          value: >-
            -Xms1200m -Xmx1200m -Xss512k
            -XX:+UseContainerSupport
            -XX:MaxMetaspaceSize=256m
            -XX:MaxDirectMemorySize=256m
            -XX:+ExitOnOutOfMemoryError
            -XX:+HeapDumpOnOutOfMemoryError
            -XX:HeapDumpPath=/dumps
            -XX:+NativeMemoryTracking=summary
            -Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags:filecount=5,filesize=50m
        volumeMounts:
        - { name: tmp,   mountPath: /tmp }
        - { name: dumps, mountPath: /dumps }
        - { name: logs,  mountPath: /logs }
        startupProbe:
          httpGet: { path: /actuator/health/startup, port: 8080 }
          periodSeconds: 5
          failureThreshold: 30
        readinessProbe:
          httpGet: { path: /actuator/health/readiness, port: 8080 }
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 2
        livenessProbe:
          httpGet: { path: /actuator/health/liveness, port: 8080 }
          periodSeconds: 10
          timeoutSeconds: 2
          failureThreshold: 3
        resources:
          requests: { cpu: "2",   memory: "2300Mi" }
          limits:   { cpu: "2",   memory: "2300Mi" }
          ephemeral-storage: "4Gi"
        lifecycle:
          preStop:
            exec: { command: ["sh","-c","sleep 15"] }
      volumes:
      - { name: tmp,   emptyDir: { sizeLimit: 256Mi } }
      - { name: dumps, emptyDir: { sizeLimit: 2Gi } }
      - { name: logs,  emptyDir: { sizeLimit: 512Mi } }
      terminationGracePeriodSeconds: 45
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: orders-api }
spec:
  minAvailable: 4
  selector:
    matchLabels: { app: orders-api }
```

**Deliverable**: a per-line diff (`baseline.yaml` → `hardened.yaml`) where every changed line cites the failure it prevents and the number behind it.

---

## Part 5 — A manifest linter that fails CI

```bash
#!/usr/bin/env bash
# usage: ./audit-manifest.sh hardened.yaml
set -euo pipefail
Y=$1; fail=0

check() { if eval "$2"; then echo "FAIL: $1"; fail=1; else echo "ok:   $1"; fi; }

LIM=$(grep -oP 'limits:\s*\{?[^}]*memory:\s*"?\K[0-9]+' "$Y" | head -1)
XMX=$(grep -oP '\-Xmx\K[0-9]+[gGmM]' "$Y" | head -1 || echo "")
[ -n "$XMX" ] && check "heap not over 70% of memory limit" "[ \$(echo \"scale=1; $XMX / $LIM\" | bc) -gt 0.70 ]"

check "liveness must not depend on a downstream" \
  "grep -A6 livenessProbe '$Y' | grep -qi 'downstream\\|dependency\\|pricing\\|/report'"

check "startupProbe required when initialDelaySeconds > 30" \
  "[ -z \"\$(grep -c startupProbe '$Y')\" ] && [ \"\$(grep -oP 'initialDelaySeconds: \K[0-9]+' '$Y' | head -1)\" -gt 30 ]"

check "requests and limits must both be set (no BestEffort/Burstable)" \
  "[ -z \"\$(grep -c 'requests:' '$Y')\" ]"

check "readOnlyRootFilesystem without writable /tmp mount" \
  "grep -q 'readOnlyRootFilesystem: true' '$Y' && ! grep -q 'mountPath: /tmp' '$Y'"

check "terminationGracePeriodSeconds must exceed longest timeout (30s default)" \
  "[ \"\$(grep -oP 'terminationGracePeriodSeconds: \K[0-9]+' '$Y' | head -1 || echo 30)\" -lt 45 ]"

exit $fail
```

**Acceptance**: fails on `baseline.yaml` with all five findings, passes on `hardened.yaml`.

---

## Part 6 — Diagnosis drills

Produce the *first three commands* and the interpretation for each, then verify against your cluster:

| Symptom | First move |
|---|---|
| Pod `Pending` for minutes | `describe` → Events → node capacity vs requests |
| `CrashLoopBackOff` | `describe` → `lastState.terminated.exitCode`, then `logs --previous` |
| `OOMKilled` | exit 137 + `Reason: OOMKilled`; compare NMT with cgroup `memory.current` |
| `Evicted` | eviction message names the resource; check node conditions |
| `Running` but `0/1` | readiness endpoint response; `curl` it from inside the pod |
| Rollout stuck | `describe deploy` → `unavailable` count; pending pods' Events |
| Intermittent 502s on deploy | in-flight requests exceeding the grace period |
| One pod slower than others | node, topology, its own NMT/GC log, its traffic share |

**Deliverable**: `DRILLS.md` with real captured output for each.

---

## Acceptance Criteria

- [ ] `BASELINE_AUDIT.md` lists every defect ranked by blast radius.
- [ ] OOM-kill reproduced and explained by an NMT-verified memory budget within 5%.
- [ ] Probe cascade reproduced, and the readiness/liveness split shown to prevent it.
- [ ] A rollout that cannot schedule reproduced, with the density arithmetic and three costed resolutions.
- [ ] Deploy-time 502 count measured before/after the drain fix.
- [ ] HPA oscillation captured and eliminated with a queue-depth signal.
- [ ] `hardened.yaml` + per-line rationale diff.
- [ ] `audit-manifest.sh` fails on baseline, passes on hardened.
- [ ] All eight drills answered with captured cluster output.

---

## Stretch

- Build a local registry and a digest-pinned multi-stage build; measure image size and pull time before/after.
- Run a kind cluster under memory pressure and watch the eviction order across QoS classes you deliberately created.
- Wire `jcmd`/JFR into a sidecar and produce a heap dump from a live pod without restarting it.
