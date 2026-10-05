# REAL-WORLD PROJECT — Abstraction & Interfaces: Notification Vendor Lock-in

## Incident Scenario
SMS vendor outage 14:00 — alerts unsent for 3h because `SmsVendor` concrete class is new'd across 40 call sites. No swap possible.

## Symptoms
- `new TwilioSms(...)` hardcoded; 22-method `Notifier` god-interface forces Email to stub `setSmsSender()`.
- `default sendAll()` overridden to send duplicates (contract unclear); ticket dispatcher `if-else` misses new `Escalated` event (silent drop).
- No seam to inject fake for load test.

## Investigation Tasks
1. Coupling: `grep -rn "new TwilioSms" | wc -l`; interface method count audit.
2. Logs: count unsent/duplicate sends; `grep "Escalated.*ignored"`.
3. JFR/thread: `jcmd Thread.print` shows sender threads blocked on vendor socket timeout (no fallback).
4. Repro: dispatch `Escalated` event — assert no notification (proves gap).
5. Design: map call sites to minimal capability set (send/schedule only).

## Root Cause
Dependence on concretions; fat interface violating ISP; unsealed event model; missing default-method contract + timeout policy.

## Resolution
- Immediate: adapter `SmsNotifier implements Notifier` + secondary vendor failover; dedupe guard; replay missed alerts.
- Short-term: slim `Notifier` (≤5 methods), `BaseNotifier` retry/backoff, sealed `TicketEvent` + exhaustive dispatch, DI wiring.
- Long-term: provider SPI + per-vendor circuit breaker, template registry, SLO (99.9% dispatch < 30s) with paging.

## Runbook
```
1. Switch vendor flag; drain retry queue.
2. Deploy slim-interface adapter; dry-run duplicates check.
3. Replay missed window; verify receipts.
4. Enable breaker + SLO alert.
```

## Metrics
- Vendor swap < 15 min (config only); duplicates = 0; missed events = 0; dispatch p99 < 10s.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Interfaces & default methods: https://docs.oracle.com/javase/tutorial/java/IandI/defaultmethods.html
- Spring DI reference: https://docs.spring.io/spring-framework/reference/core/beans.html
