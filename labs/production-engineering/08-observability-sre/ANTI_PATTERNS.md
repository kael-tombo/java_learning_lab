# ANTI-PATTERNS: Observability & SRE in Production
## Lab 08 | Production Engineering Academy

---

## Anti-Pattern 1: Alerting on Symptoms Instead of User-Impacting SLOs

### The Mistake
Setting up 200 PagerDuty alerts on internal machine metrics:
- "Host CPU > 80%"
- "Pod memory > 75%"
- "Tomcat thread count > 150"
- "Garbage collection count > 20/min"

### Why It Fails (Alert Fatigue)
1. CPU can run at 95% while users experience blazing 10ms latencies with 100% success.
2. Engineers get woken up at 3:00 AM for non-issues, leading to alert fatigue.
3. When a real catastrophic outage occurs, engineers ignore the pager.

### The Correct SRE Fix
Alert **only** on user-facing symptoms and SLO burn rates:
- Latency SLO: "p99 latency > 200ms for 5 minutes"
- Availability SLO: "Error budget burn rate > 14.4x"
CPU and memory alerts should be non-paging informational tickets.

---

## Anti-Pattern 2: Synchronous Blocking Remote Logging

### The Mistake
Configuring Logback or Log4j2 with a synchronous HTTP or TCP appender directly shipping logs to Logstash/Elasticsearch.

### Why It Fails
If Elasticsearch or the network experiences a 500ms delay, every `log.info()` statement in application business code blocks for 500ms! A logging hiccup halts all customer traffic across the entire enterprise.

### The Correct SRE Fix
Always use asynchronous appenders with bounded drop queues:
```xml
<appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
    <appender-ref ref="REMOTE_TCP" />
    <queueSize>4096</queueSize>
    <discardingThreshold>20</discardingThreshold> <!-- Drop TRACE/DEBUG/INFO if 80% full -->
    <neverBlock>true</neverBlock> <!-- Drop events rather than blocking application threads! -->
</appender>
```
Application throughput must never be held hostage by telemetry transport.
