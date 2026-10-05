# REAL-WORLD PROJECT — Modules: Illegal-Access Outage After JDK 21 Upgrade

## Incident Scenario
Monolith upgraded JDK 17 -> 21; checkout pods crash-loop with
`IllegalAccessError: class com.shop.impl.Pricing cannot access...` and
`InaccessibleObjectException` from Jackson. Rollback image missing; traffic
50% on broken pods.

## Symptoms
- `ExceptionInInitializerError` + `Unable to make field accessible` at boot.
- `--add-opens` flags copied from StackOverflow mask half the errors.
- Image still ships full JDK (380MB); startup 22s, OOM on small nodes.
- `jdeps` never run; duplicate `util` package in two jars (split package).

## Investigation Tasks
1. Triage: `kubectl logs` / `journalctl`; collect first 50 stack traces,
   classify `IllegalAccessError` vs `InaccessibleObjectException`.
2. JFR + threads: `jcmd <pid> JFR.start duration=60s filename=boot.jfr`;
   `jcmd <pid> Thread.print` to catch boot deadlock vs fast-fail.
3. Heap: `jcmd <pid> GC.heap_dump` only if OOM suspected; else focus on
   module graph: `jdeps --multi-release 21 --class-path 'libs/*' app.jar`.
4. Repro: `java --show-module-resolution --module-path mods -m shop.app`
   captures readability errors; `jdeps --check` flags split packages.
5. Flags audit: `grep -rn "add-opens\|add-exports" Dockerfile k8s/ scripts/`.
6. Size audit: `jimage list` / `du -sh image`; `time image/bin/shop --help`
   vs full-JDK launch for startup baseline.
7. Service wiring: confirm `ServiceLoader` vs classpath-scan breakage.

## Root Cause
Classpath app relied on deep reflection into JDK internals and duplicate
packages; JDK 21 strong encapsulation turned warnings into errors. Bloated
`--add-opens` hid the graph; split packages blocked modular `jlink` fix.

## Resolution
- Immediate: cordon broken pods; minimal scoped `--add-opens` (per-package)
  hotfix to restore boot; pin good image tag.
- Short-term: carve `shop.api/impl` modules, `exports` API only, `opens`
  one Jackson package, `provides/uses` services, merge split package.
- Long-term: `jdeps` + `jlink` in CI, module-boundary tests, JDK upgrade
  train (EA testing), full-JDK images banned by policy.

## Runbook
```
1. Cordon + capture logs, JFR boot recording, jdeps graph.
2. Scoped add-opens hotfix; verify boot on canary.
3. Land modules (exports/opens/services); jdeps --check green.
4. Ship jlink image; compare size/startup; promote.
5. Postmortem: CI gates + upgrade-runbook update.
```

## Metrics
- Boot success 100%, startup <= 8s, image <= 120MB (from 380MB).
- `add-opens` count <= 2 scoped packages; split-package violations = 0.
- Mixed-JDK canary error rate < 0.01% during next upgrade.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Module system API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/module/package-summary.html
- Jigsaw / JPMS spec: https://openjdk.org/projects/jigsaw/spec/
