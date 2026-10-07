# Monitoring and Alerting: ReDoS and High CPU Detection

**Incident**: INC-2024-0610-REDOS
**Category**: CPU / Regex Observability
**Author**: Meta SRE + Content AI Team

## Overview

This document specifies the monitoring, metrics, and alerting rules required to detect ReDoS attacks, high CPU from regex evaluation, and thread starvation before they cause P0 incidents. These monitors would have caught the ReDoS attack within seconds of the first exploit attempt.

## Metrics Collection

### 1. CPU Metrics (Critical)

```
Per-process:
  ├── cpu.utilization.percent      — Overall JVM CPU usage (% of core)
  ├── cpu.system.percent           — System CPU usage
  └── cpu.user.percent             — User-space CPU usage

Per-thread (via JFR / async-profiler):
  ├── thread.cpu.time              — CPU time per thread
  ├── thread.cpu.utilization       — CPU utilization per thread
  └── thread.regex.time            — Time spent in java.util.regex methods
```

### 2. Regex Performance Metrics (Critical)

```
For each regex pattern evaluation:
  ├── regex.evaluation.time.max    — Max evaluation time (ms)
  ├── regex.evaluation.time.p99    — P99 evaluation time (ms)
  ├── regex.evaluation.count       — Evaluations per second
  ├── regex.timeout.count          — Number of regex timeouts
  ├── regex.backtrack.count        — Estimated backtracking steps
  └── regex.input.length           — Input length distribution

JFR events (jdk.JavaMonitorEnter for lock contention):
  ├── regex.thread.interrupted     — Threads interrupted during regex
  └── regex.stackOverflow          — Stack overflow from deep backtracking
```

### 3. Thread Pool Metrics (High)

```
For each thread pool:
  ├── thread.pool.active           — Active thread count
  ├── thread.pool.queue.depth      — Task queue depth
  ├── thread.pool.rejected.count   — Rejected task count
  ├── thread.pool.completion.time  — Task completion time
  └── thread.state.blocked         — Blocked thread count
```

## Alerting Rules

### P0/Critical Alarms (Page On-Call)

| Alert Name | Condition | Duration | Runbook |
|------------|-----------|----------|---------|
| CPUUsageCritical | `cpu.utilization.percent >= 90` | 2 min | Collect flame graph, check regex |
| RegexEvaluationTime | `regex.evaluation.time.p99 >= 1000ms` | 1 min | Potential ReDoS attack |
| RegexTimeoutRate | `rate(regex.timeout.count[1m]) >= 10` | 1 min | Active ReDoS attack |
| ThreadPoolExhausted | `thread.pool.active >= maxPoolSize` for 30s | 0 min | Scale or mitigate attack |

### P1/Warning Alarms (Alert during business hours)

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| CPUUsageWarning | `cpu.utilization.percent >= 70` | 5 min | Profile CPU with async-profiler |
| RegexEvaluationWarning | `regex.evaluation.time.p99 >= 200ms` | 5 min | Check which pattern is slow |
| UnusualInputLength | `avg(regex.input.length) > 500` for 10 min | 10 min | Investigate input patterns |
| HighBacktrackRate | `regex.backtrack.count > 10000` per eval | 5 min | Potential ReDoS probe |

### P2/Info Alarms (Dashboard / Report)

| Alert Name | Condition | Action |
|------------|-----------|--------|
| RegexPatternChange | New or modified regex pattern detected | Review for ReDoS |
| StackOverflowError | `regex.stackOverflow > 0` | Immediate investigation |
| ThreadInterrupted | `regex.thread.interrupted > 10` | Check if watchdog is working |

## Dashboard: Regex Health Overview

### Panel 1: CPU Utilization (Time Series)
```sql
SELECT
  cpu.utilization.percent{instance="$instance"}
AS "CPU %"
FROM metrics
WHERE $__timeFilter
```
Visual: Area chart with warning line at 70%, critical at 90%

### Panel 2: Regex Evaluation Time (Heatmap)
```sql
SELECT
  regex.evaluation.time{pattern_id="$pattern"}
AS "Evaluation Time (ms)"
FROM metrics
```
Visual: Heatmap with threshold line at 100ms

### Panel 3: ReDoS Detection (Single Stat)
```sql
SELECT
  rate(regex.timeout.count{instance="$instance"}[5m])
AS "Regex Timeouts / 5min"
FROM metrics
```
Threshold: > 0 indicates potential attack

### Panel 4: Thread Pool State (Time Series)
```sql
SELECT
  thread.pool.active{instance="$instance"} AS "Active",
  thread.pool.queue.depth{instance="$instance"} AS "Queue"
FROM metrics
```

## JFR Configuration for Regex Monitoring

```bash
# JFR recording with CPU and lock profiling
jcmd <pid> JFR.start name=cpu_profile \
  settings=profile \
  dumponexit=true \
  filename=/data/jfr/cpu_profile.jfr

# Key JFR events for regex/CPU analysis:
#   jdk.ExecutionSample — CPU samples (for flame graphs)
#   jdk.NativeMethodSample — Native method CPU
#   jdk.ThreadAllocationStatistics — Thread allocation info
#   jdk.JavaMonitorEnter — Lock contention
#   jdk.ActiveRecording — Recording metadata

# Custom event for regex evaluation (if available via bytecode instrumentation)
# -XX:StartFlightRecording=name=regex_monitoring
```

## async-profiler Integration

```bash
# Real-time CPU flame graph
profiler.sh -d 60 -e cpu -f /tmp/flame_$(date +%s).html <pid>

# Alloc profiling (to detect GC pressure from regex)
profiler.sh -d 60 -e alloc -f /tmp/alloc_$(date +%s).html <pid>

# Wall-clock profiling (to detect blocked threads)
profiler.sh -d 60 -e wall -f /tmp/wall_$(date +%s).html <pid>
```

## Automated Response

When regex evaluation time exceeds thresholds:

1. **Collect CPU flame graph via async-profiler**
2. **Identify the hot regex pattern** from stack traces
3. **Disable the pattern via feature flag** (emergency mitigation)
4. **Rate-limit requests** containing the suspicious input pattern
5. **Block the attacking IP** at the load balancer level (if identifiable)
6. **Trigger JFR dump** for the affected node

## Real-Time Monitoring Setup

### Step 1: Configure Continuous JFR Recording

```bash
# Add to JVM startup arguments for continuous monitoring
-XX:StartFlightRecording=name=realtime_monitor,\
  settings=profile,\
  maxage=24h,\
  maxsize=500M,\
  dumponexit=true,\
  filename=/data/jfr/realtime.jfr
```

### Step 2: Integrate async-profiler for On-Demand Profiling

```bash
# Install as a systemd service
cat > /etc/systemd/system/async-profiler.service << 'EOF'
[Unit]
Description=async-profiler continuous CPU sampling
After=network.target

[Service]
Type=simple
ExecStart=/opt/async-profiler/profiler.sh -e cpu -i 999ms \
  -f /var/log/profiler/cpu.html --loop 3600 $(pgrep -f java)
Restart=always
User=nobody

[Install]
WantedBy=multi-user.target
EOF

systemctl enable async-profiler
systemctl start async-profiler
```

### Step 3: Create Prometheus Alerting Rules

```yaml
groups:
  - name: regex_alerts
    rules:
      - alert: RegexEvaluationTimeCritical
        expr: regex_evaluation_time_ms{quantile="0.99"} > 1000
        for: 1m
        labels: { severity: critical }
        annotations:
          summary: "Regex evaluation P99 > 1000ms for {{ $labels.pattern_id }}"

      - alert: RegexTimeoutRateHigh
        expr: rate(regex_timeout_total[5m]) > 10
        for: 1m
        labels: { severity: critical }
        annotations:
          summary: "High rate of regex timeouts — active ReDoS attack likely"

      - alert: CPUSpikeRegexCorrelation
        expr: |
          (rate(process_cpu_seconds_total[1m]) > 0.8)
          and
          (rate(regex_evaluation_time_ms_sum[1m]) > 100000)
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "CPU spike correlated with regex activity — ReDoS suspected"
```

## Implementation Guide

### Step 1: Deploy async-profiler as a Sidecar

Deploy async-profiler as a sidecar process on each application instance:

```bash
# Install async-profiler
wget (link removed)
tar -xzf async-profiler-*.tar.gz -C /opt/

# Run continuous CPU profiling with low overhead
/opt/async-profiler/profiler.sh -e cpu -i 999ms -f /var/log/profiler/cpu_$(date +%s).html \
  --loop 3600 <pid> &
```

### Step 2: Configure JMX Metrics Export

```yaml
# /etc/prometheus/jmx_exporter.yaml
rules:
  - pattern: 'java.lang<type=Threading><>ThreadCount'
    name: jvm_threads_total
  - pattern: 'java.lang<type=OperatingSystem><>ProcessCpuLoad'
    name: jvm_cpu_load
```

### Step 3: Create Grafana Dashboard Panels

Panel 1: CPU Utilization by thread state (stacked area)
Panel 2: Regex evaluation time histogram (heatmap)
Panel 3: Thread pool active vs waiting (time series)
Panel 4: ReDoS alert status (single stat)

### Step 4: Set Up Automated Response

When regex timeout events exceed threshold:

1. Auto-disable the offending pattern via feature flag
2. Collect JFR dump for post-mortem analysis
3. Send alert to on-call with flame graph attached
4. Log the attack payload for security team analysis

## References

- async-profiler: https://github.com/async-profiler/async-profiler
- Prometheus: "JMX Exporter for JVM Metrics" — https://github.com/prometheus/jmx_exporter
- Grafana: "JVM Flame Graph Plugin" — https://grafana.com/grafana/plugins/
- Netflix: "Flame Graphs for Production Profiling" — Netflix Tech Blog
- Oracle: "JFR Event Reference" — Oracle JDK Documentation
- Datadog: "Monitoring ReDoS Attacks" — Datadog Security Labs
- Elastic: "Regex Performance Monitoring with APM" — Elastic Documentation

