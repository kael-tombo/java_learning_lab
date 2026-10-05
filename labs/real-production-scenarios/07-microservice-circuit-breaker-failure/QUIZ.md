# QUIZ — Lab 07: Circuit-Breaker Failure (15 questions)

1. Breaker states? — A) open/closed only B) closed/open/half-open C) up/down D) hot/cold — **B**
2. OPEN means? — A) Pass all B) Fail fast + fallback C) Retry forever D) Crash — **B**
3. Sane failureRateThreshold? — A) 80–90% B) ~50% C) 5% D) 100% — **B**
4. Bulkhead purpose? — A) Faster CPU B) Isolate pools per dep C) Bigger DB D) Cache — **B**
5. Why 30s timeout is dangerous? — A) Too fast B) Holds threads, explodes queue (L=λW) C) Cheap D) Secure — **B**
6. Retry storm fix? — A) More retries B) Backoff+jitter, max 2, skip if OPEN C) No timeout D) Sync all — **B**
7. HALF_OPEN does? — A) Floods service B) Probes with N calls then decides C) Shuts down D) Ignores metrics — **B**
8. First triage step? — A) Restart all B) Trace to slowest leaf origin C) Delete data D) Add threads blindly — **B**
9. Fallback must? — A) Throw B) Never throw, return degraded + metric C) Call sick service again D) Block — **B**
10. Shared pool risk? — A) None B) One slow dep starves all C) Faster D) Cheaper — **B**
11. waitDuration controls? — A) Build time B) Time OPEN before half-open probe C) Log retention D) CPU — **B**
12. Monitor what beyond errors? — A) Nothing B) Breaker state + pool saturation + fallback rate C) Disk only D) Billing — **B**
13. Little's Law? — A) L=λW B) E=mc² C) P=NP D) CAP — **A**
14. Graceful degradation example? — A) 500 everything B) Cached catalog when live fails C) Delete orders D) Hang — **B**
15. Force-open used to? — A) Break prod B) Shed load from sick dep fast C) Slow recovery D) Hide metrics — **B**
