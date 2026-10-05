# REAL-WORLD PROJECT — Reflection: Mapper Upgrade Breaks Startup + Leaks

## Incident Scenario
After adding "just one more generic field," service startup jumps 40s → 4 min and OldGen grows weekly until Full GC pauses hit 5s. Framework upgrade blocked.

## Symptoms
- Mapper does `getDeclaredFields` + `setAccessible` per object (millions/day) → CPU hotspot in `getDeclaredFields0` (JFR `jdk.ExecutionSample` top frame).
- `URLClassLoader` per plugin reload never `close()`d → metaspace/loader leak; `ClassLoader` count grows in heap histogram.
- JPMS: `--illegal-access` removed on JDK 21 → `InaccessibleObjectException: Unable to make field accessible` for JDK-internal DTO.
- `InvocationTargetException` logged without cause → on-call chases mapper instead of the real NPE in a setter.

## Investigation Tasks
1. JFR: 60s `profile` — top methods `Class.getDeclaredField/getMethod`; `jdk.ClassLoad` rate spike; `jdk.JavaMonitorEnter` on mapper cache miss path.
2. Heap: `jcmd <pid> GC.heap_dump`; histogram by classloader — duplicate `PluginClassLoader` + retained `Class` count climbing.
3. Threads: `jcmd <pid> Thread.print` — startup threads parked in reflective lookup; request threads in mapper sync block.
4. Logs: `grep "InaccessibleObject\|InvocationTarget" app.log | head -30`; unwrap one chain to true cause.
5. Repro: map 100k objects uncached vs cached — wall-time ratio; loader open/close count test.

## Root Cause
Per-call reflective lookup without cache, unclosed URLClassLoaders pinning classes, illegal-access assumption broken by modules, cause-swallowing error logging.

## Resolution
- Immediate: static `ConcurrentHashMap` BeanInfo cache, `close()` loaders (try-with-resources) + single shared child loader, `--add-opens` documented stopgap with exported-API migration ticket, unwrap `getCause` in logs.
- Short-term: startup-time budget test, loader-count metric, codegen spike for top-5 DTOs.
- Long-term: annotation-processor mapper (zero runtime reflection), plugin isolation + version contract.

## Runbook
```
1. JFR + heap dump + loader histogram before restart.
2. Deploy cached-mapper + loader-close hotfix.
3. Verify startup < 60s, loader count flat over 24h.
4. Fix module access properly (export API, drop add-opens).
5. Land startup/perf gates in CI.
```

## Metrics
- Startup back < 60s; mapping CPU −80%; loader count flat; Full GC pauses < 500ms; error logs point at true cause 100%.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.lang.reflect API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/reflect/package-summary.html
- Reflection tutorial: https://docs.oracle.com/javase/tutorial/reflect/
