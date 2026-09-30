
# RUNBOOK: JVM Memory & GC Incidents
## Lab 01 | On-Call Runbook | Production Engineering Academy

---

## 🚨 RUNBOOK: OOM — Java Heap Space

**Severity**: P1 (Service Down or Degraded)  
**ETA to Mitigate**: 5-15 minutes

### Step 1: Immediate Assessment (0-2 min)
```bash
# Check if process is still running
ps aux | grep java
# Check container status (K8s)
kubectl get pods -n <namespace> | grep <service>
kubectl describe pod <pod-name> -n <namespace>

# Check recent logs for OOM
kubectl logs <pod-name> -n <namespace> --tail=100 | grep -i "outofmemory\|OOM\|heap"
```

### Step 2: Preserve Evidence (2-5 min) — BEFORE restarting
```bash
# If pod is still alive, trigger heap dump
kubectl exec -it <pod-name> -n <namespace> -- bash
jcmd $(pgrep java) GC.heap_dump /tmp/heapdump-$(date +%Y%m%d-%H%M%S).hprof

# Copy heap dump out
kubectl cp <namespace>/<pod-name>:/tmp/heapdump.hprof ./heapdump-$(date +%Y%m%d).hprof

# Capture thread dump too
jcmd $(pgrep java) Thread.print > /tmp/threaddump.txt
```

### Step 3: Restore Service (5-10 min)
```bash
# Restart pod (K8s will restart automatically if OOM-kill)
kubectl rollout restart deployment/<service-name> -n <namespace>

# Verify health
kubectl rollout status deployment/<service-name> -n <namespace>
kubectl get pods -n <namespace> | grep <service>
```

### Step 4: Short-Term Mitigation
- Increase heap temporarily: `kubectl set env deployment/<service> JAVA_OPTS="-Xmx8g -Xms8g"`
- Add pod memory limit: update `resources.limits.memory` in deployment YAML

### Step 5: Root Cause (post-incident, 24-48h)
```bash
# Analyze heap dump with Eclipse MAT
# 1. Open heapdump.hprof in Eclipse MAT
# 2. Run "Leak Suspects" report
# 3. Check "Dominator Tree" for largest retained objects
# 4. Find GC root path: right-click object → "Path to GC Roots"
```

---

## 🚨 RUNBOOK: Full GC — Service Freezing

**Severity**: P1 (All requests timing out during Full GC)  
**ETA to Mitigate**: 2-10 minutes

### Immediate Diagnosis
```bash
# Check GC logs for Full GC events
grep "Pause Full" /var/log/app/gc.log | tail -20

# Check GC overhead (should be < 5%)
grep "GC time" /var/log/app/gc.log | tail -5

# Real-time GC monitoring
jstat -gcutil $(pgrep java) 1000 20  # Print every 1s, 20 times
# Output: S0  S1   E     O      M    CCS  YGC YGCT   FGC  FGCT   CGC CGCT   GCT
#          0  36  89.2  94.5   97.8  94.3  342  4.231    3  12.456  0  0.000  16.687
#                       ↑ 94.5% old gen utilization = Full GC imminent!
```

### If Full GC is Continuous
```bash
# Old Gen too full, GC can't keep up
# Option 1: Trigger manual GC attempt (usually doesn't help but worth trying)
jcmd $(pgrep java) GC.run

# Option 2: Rolling restart (keeps some capacity online)
kubectl rollout restart deployment/<service> -n <namespace>

# Option 3: Scale out to distribute load during incident
kubectl scale deployment/<service> --replicas=<current+2> -n <namespace>
```

### Tuning Response for Old-Gen Pressure
```bash
# Tune G1 to start concurrent marking earlier
# Deploy with these additional flags:
-XX:InitiatingHeapOccupancyPercent=35    # Was 45, now start earlier
-XX:G1ReservePercent=15                  # Keep buffer for evacuation failures

# Verify change took effect
jcmd $(pgrep java) VM.flags | grep -i "InitiatingHeapOccupancy\|G1Reserve"
```

---

## 🚨 RUNBOOK: OOM — Metaspace

**Severity**: P2 (Service will OOM-restart periodically)

### Diagnosis
```bash
# Check current metaspace usage
jcmd $(pgrep java) VM.native_memory | grep -A3 "Class"

# Count active ClassLoaders
jcmd $(pgrep java) VM.classloaders 2>/dev/null | grep "ClassLoader:" | wc -l

# Check for class loader growth over time (compare snapshots)
jcmd $(pgrep java) VM.native_memory baseline
# ... wait 10 minutes ...
jcmd $(pgrep java) VM.native_memory detail.diff
```

### Short-Term Fix
```bash
# Increase metaspace (if just undersized)
kubectl set env deployment/<service> JAVA_OPTS="... -XX:MaxMetaspaceSize=512m"

# If leak confirmed, restart is only mitigation until fix deployed
kubectl rollout restart deployment/<service>
```

---

## 🔍 Key JVM Monitoring Commands

```bash
# Full JVM health snapshot
jcmd $(pgrep java) VM.info
jcmd $(pgrep java) VM.flags
jcmd $(pgrep java) GC.heap_info
jcmd $(pgrep java) VM.native_memory summary

# Thread analysis
jcmd $(pgrep java) Thread.print | grep -c "java.lang.Thread"  # Thread count

# Real-time heap monitoring
watch -n2 "jstat -gcutil $(pgrep java)"

# Check JVM version and startup args
jcmd $(pgrep java) VM.version
jcmd $(pgrep java) VM.command_line
```

---

## 📊 Escalation Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Heap usage | > 70% | > 85% | Alert SRE |
| Old Gen usage | > 60% | > 80% | Page on-call |
| Full GC frequency | > 1/hour | > 1/10min | P1 incident |
| GC pause duration | > 500ms | > 2000ms | P1 incident |
| Metaspace growth | > 10MB/hr | > 50MB/hr | Investigate CL leak |
| GC overhead | > 5% | > 15% | Tune or scale |
