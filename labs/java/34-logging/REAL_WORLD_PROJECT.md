# REAL-WORLD PROJECT — Logging: Silent Failures + 40GB Disk-Full Outage

## Incident Scenario
Payments silently drop 2% of charges (only `DEBUG` logged, off in prod) while
a chatty `INFO`-per-byte uploader fills disks — Logback blocks, pods go
`DiskPressure`, and card numbers sit plaintext in 90 days of archives.

## Symptoms
- Missing-charge complaints with zero `ERROR` lines; root cause invisible.
- 40GB/day unstructured logs; `%d %msg` with no traceId — unjoinable.
- Sync file appender, no rotation; GC logs + app logs same disk.
- `MDC` set but never cleared — user A's `userId` appears on user B's lines.
- `logger.info("card=" + cardNumber)` across 6 call sites; PCI exposure.

## Investigation Tasks
1. Triage without restart: `jcmd <pid> Thread.print` — threads parked in
   `FileAppender/write` confirm logging backpressure, not business logic.
2. JFR: `jcmd <pid> JFR.start duration=120s filename=log.jfr settings=profile`;
   check `jdk.ThreadPark`, `jdk.FileWrite`, `jdk.JavaMonitorEnter` on appender
   lock + `jdk.ObjectAllocationInNewTLAB` for log-string churn.
3. Heap: `jcmd <pid> GC.heap_dump` — dominators for `char[]/String` from
   log statements; sample `logger.isDebugEnabled` guard misses.
4. Log forensics: `grep -c "traceId=null\|userId=" app.log`; quantify
   unjoinable lines; `grep -rn "card\|password\|token" logs/ | head` (careful:
   restrict, rotate out of PCI scope immediately).
5. Config audit: `logback-spring.xml` — appender type, rolling policy,
   async queue, level per package; `grep -rn "System.out\|printStackTrace\|+ \"" src/`.
6. Repro: 10k-request run showing MDC bleed (wrong userId) + disk growth
   rate; demonstrate async+cap fix flattening p99.
7. Access-log join: attempt traceId join checkout->payments — show failure.

## Root Cause
Level misuse (failures at DEBUG), printf-style string logs without context,
sync unbounded file logging, MDC leak, and secret-logging — observability
debt that hides errors and creates outages + compliance risk.

## Resolution
- Immediate: raise charge-failures to ERROR + alert, rotate+drain disk,
  scrub/redact card fields, quarantine archives under restricted ACL.
- Short-term: SLF4J `{}` + guards, MDC filter with clear, JSON layout,
  async bounded appender, size/time rotation, redaction decorator.
- Long-term: level contract + lint, ERROR-rate SLO, log pipeline (Loki/ELK)
  with retention, PCI log-review cadence, logging cost in perf tests.

## Runbook
```
1. Thread.print + JFR file-write capture; stop the bleeder (level up + cap).
2. Free disk (rotate, move GC logs); restrict archive ACL; scrub secrets.
3. Ship JSON+MDC+redaction canary; verify traceId join end-to-end.
4. Enable ERROR-rate alert; attach runbook link.
5. Postmortem: level guide + redaction tests + retention policy.
```

## Metrics
- Dropped-charge visibility 100% (ERROR + alert < 2 min); log volume -80%.
- traceId join success >= 99%; MDC bleed 0 in 10k sample.
- Secrets in logs = 0 (scan); p99 unaffected by logging at 10k req.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring Boot logging: https://docs.spring.io/spring-boot/reference/features/logging.html
- System.Logger API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/System.Logger.html
