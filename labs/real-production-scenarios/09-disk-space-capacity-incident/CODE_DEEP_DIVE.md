# CODE DEEP DIVE — Lab 09: Disk Runbook

## 1. Diagnose in 60 Seconds
```bash
df -h; echo ---; df -i
du -sh /var/log /tmp /var/lib/docker /data 2>/dev/null | sort -rh
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
kubectl describe node <node> | grep -A5 Pressure
kubectl get events -A --sort-by=.lastTimestamp | grep -i "evict\|pressure\|space" | tail -10
# log snippet:
# java.io.IOException: No space left on device (Write to /var/log/app.log)
# kubelet: The node had condition: [DiskPressure]
```

## 2. Safe Reclaim (No Data Loss)
```bash
: > /var/log/app/app.log            # truncate open log (frees now)
truncate -s 0 /var/log/app/*.log
journalctl --vacuum-size=1G --vacuum-time=7d
find /tmp -type f -atime +2 -delete
docker system df; docker system prune -a --filter "until=72h"
lsof +L1 | head -20                 # confirm deleted-open freed
```

## 3. Logback Rotation Fix
```xml
<appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
  <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
    <fileNamePattern>app.%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
    <maxFileSize>100MB</maxFileSize><maxHistory>30</maxHistory>
    <totalSizeCap>5GB</totalSizeCap>
  </rollingPolicy>
</appender>
```

## 4. K8s Guardrails
```yaml
resources:
  requests: { ephemeral-storage: "1Gi" }
  limits: { ephemeral-storage: "5Gi" }
volumes:
- name: scratch
  emptyDir: { sizeLimit: "2Gi" }
```

## 5. Forecast Alert
```promql
(node_filesystem_avail_bytes{mountpoint="/"} / rate(node_filesystem_size_bytes[1h]-node_filesystem_avail_bytes[1h])) < 24*3600
```

## 6. Grow After Reclaim
```bash
kubectl get pvc -A | grep -i data
# expand PVC (storageClass allowVolumeExpansion) then verify:
df -h /data; touch /data/.write-test && rm /data/.write-test
```

## 7. Anti-Patterns
- `rm -rf /var/lib/docker` on live node — kills running containers.
- Hand-deleting DB WAL — breaks PITR; use `pg_archivecleanup` / managed expiry.
