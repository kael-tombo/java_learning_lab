# Monitoring: Kubernetes Pod CrashLoop Detection

## Monitoring Architecture

A multi-layered monitoring approach to detect pod crashlooping at the earliest possible moment, differentiate between transient and persistent failures, and trigger automated rollback when appropriate.

## 1. Prometheus Metrics

### Core Metrics

| Metric | Type | Source | Description |
|--------|------|--------|-------------|
| `kube_pod_container_status_restarts_total` | Counter | kube-state-metrics | Total container restarts |
| `kube_pod_container_status_waiting_reason` | Gauge | kube-state-metrics | 1 if pod in waiting state (CrashLoopBackOff) |
| `container_memory_working_set_bytes` | Gauge | cAdvisor | Current memory usage |
| `container_cpu_cfs_throttled_seconds_total` | Counter | cAdvisor | Total CPU throttling time |
| `container_oom_events_total` | Counter | cAdvisor | Total OOM events |
| `container_last_seen` | Gauge | cAdvisor | Last container observation |
| `kube_deployment_status_replicas_unavailable` | Gauge | kube-state-metrics | Unavailable replicas |
| `kube_deployment_metadata_generation` | Gauge | kube-state-metrics | Deployment generation |

### Alert Rules

```yaml
groups:
  - name: kubernetes_pods
    interval: 30s
    rules:
      - alert: KubePodCrashLooping
        expr: |
          max_over_time(kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"}[5m]) == 1
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Pod {{ $labels.pod }} is in CrashLoopBackOff"
          description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been restarting repeatedly"
          runbook: "https://runbook.acmecorp.com/crashloop"

      - alert: KubePodOOMKilled
        expr: |
          max_over_time(kube_pod_container_status_terminated_reason{reason="OOMKilled"}[5m]) == 1
        for: 0m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Pod {{ $labels.pod }} OOMKilled"
          description: "Container {{ $labels.container }} in pod {{ $labels.pod }} was OOMKilled"

      - alert: KubeContainerHighRestartRate
        expr: |
          rate(kube_pod_container_status_restarts_total{namespace="production"}[10m]) > 1
        for: 2m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "High restart rate for {{ $labels.pod }}"
          description: "Pod {{ $labels.pod }} is restarting {{ $value | humanize }} times per 10 minutes"

      - alert: KubeDeploymentReplicasUnavailable
        expr: |
          kube_deployment_status_replicas_unavailable{namespace="production"} > 0
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Unavailable replicas in deployment {{ $labels.deployment }}"
          description: "{{ $value }} replicas unavailable in {{ $labels.deployment }}"
```

### CPU Throttling Alerts

```yaml
groups:
  - name: kubernetes_cpu
    rules:
      - alert: ContainerCPUThrottlingHigh
        expr: |
          sum(increase(container_cpu_cfs_throttled_seconds_total{container!=""}[5m]))
          / sum(increase(container_cpu_cfs_periods_total{container!=""}[5m]))
          > 0.25
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU throttling > 25% for {{ $labels.container }}"

      - alert: ContainerMemoryPressure
        expr: |
          container_memory_working_set_bytes{container!=""} /
          container_spec_memory_limit_bytes{container!=""} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.container }} memory usage > 85%"
```

## 2. Grafana Dashboard

### Pod CrashLoop Overview Dashboard

**Panel 1: CrashLoop Status** (Stat)
- Query: `count(kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"})`
- Thresholds: green=0, yellow=1-5, red=>5

**Panel 2: Restart Rate** (Timeseries)
- Query: `rate(kube_pod_container_status_restarts_total{namespace="production"}[5m])`
- Display by: deployment, pod

**Panel 3: OOM Events** (Stat)
- Query: `sum(rate(container_oom_events_total{namespace="production"}[5m]))`
- Thresholds: green=0, red=>0

**Panel 4: Memory Usage by Pod** (Bar Gauge)
- Query: `container_memory_working_set_bytes{namespace="production"} / container_spec_memory_limit_bytes`
- Display: percentage of limit

**Panel 5: CPU Throttling** (Timeseries)
- Query: `rate(container_cpu_cfs_throttled_seconds_total{namespace="production"}[5m])`
- Warning line: 0.25, Critical line: 0.50

**Panel 6: Deployment Availability** (Table)
- Query: `kube_deployment_status_replicas{namespace="production"}`
- Columns: deployment, desired, available, unavailable, updated

## 3. Prometheus Recording Rules

```yaml
groups:
  - name: kubernetes_recording
    rules:
      - record: pod:restart_rate:5m
        expr: rate(kube_pod_container_status_restarts_total{namespace="production"}[5m])
      
      - record: deployment:unavailable_ratio
        expr: |
          kube_deployment_status_replicas_unavailable{namespace="production"} 
          / kube_deployment_status_replicas_available{namespace="production"}
      
      - record: namespace:crashloop_count
        expr: count(kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"})
```

## 4. Synthetic Monitoring

```yaml
# kubernetes/probes/proactive-check.yaml
apiVersion: v1
kind: Pod
metadata:
  name: deployment-health-checker
  namespace: monitoring
spec:
  containers:
    - name: checker
      image: bitnami/kubectl:latest
      command:
        - /bin/sh
        - -c
        - |
          while true; do
            for NS in production staging; do
              CRASHLOOPS=$(kubectl get pods -n $NS --field-selector=status.phase=Running -o json | \
                jq '[.items[] | select(.status.containerStatuses[].state.waiting.reason=="CrashLoopBackOff")] | length')
              if [ "$CRASHLOOPS" -gt 0 ]; then
                echo "WARNING: $CRASHLOOPS crashlooping pods in $NS"
                curl -X POST -H "Content-type: application/json" \
                  --data "{\"text\":\"CRASHLOOP: $CRASHLOOPS pods crashlooping in $NS\"}" \
                  $SLACK_WEBHOOK
              fi
            done
            sleep 60
          done
  restartPolicy: Always
```

## 5. Alert Escalation Matrix

| Alert | Severity | Notification | Response Time | Auto-Rollback |
|-------|----------|-------------|---------------|---------------|
| Single pod CrashLoop | Warning | Slack #ops-alerts | 15 min | No |
| Multiple pods CrashLoop | Critical | PagerDuty + Slack | 5 min | Yes (>25% pods) |
| OOMKilled | Critical | PagerDuty + Slack | 5 min | Yes |
| >25% CPU throttling | Warning | Slack #ops-alerts | 30 min | No |
| >50% CPU throttling | Critical | PagerDuty + Slack | 10 min | Yes |
| >85% memory usage | Warning | Slack #ops-alerts | 15 min | No |
| Deployment unavailable | Critical | PagerDuty + Phone | Immediate | Yes |

## 6. Dashboards and Observability

```bash
# Quick health check commands
kubectl get pods -n production | grep -E "CrashLoop|OOM"
kubectl get events -n production --sort-by='.lastTimestamp' | tail -20
kubectl top pods -n production
kubectl describe nodes | grep -A 5 "Conditions"
```

### PromQL Queries for Ad-Hoc Investigation

```promql
# Find crashlooping pods
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1

# Memory pressure by container
container_memory_working_set_bytes{namespace="production"} / container_spec_memory_limit_bytes > 0.8

# CPU throttling rate
rate(container_cpu_cfs_throttled_seconds_total{namespace="production"}[5m])

# OOM events per hour
rate(container_oom_events_total{namespace="production"}[1h])

# Deployment rollback rate
rate(kube_deployment_metadata_generation{namespace="production"}[30m])
```

## 7. Runbook Automation

```yaml
# alertmanager.yml — Automated rollback route
routes:
  - match:
      severity: critical
      auto_rollback: "true"
    receiver: auto-rollback
    repeat_interval: 5m

receivers:
  - name: auto-rollback
    webhook_configs:
      - url: http://argocd-server.argocd.svc.cluster.local/api/rollback
        send_resolved: true
```

## References

- Google SRE Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
- Prometheus Kubernetes Mixin: https://github.com/prometheus-community/helm-charts
- cAdvisor Documentation: https://github.com/google/cadvisor
- Datadog Kubernetes Monitoring: (link removed)
