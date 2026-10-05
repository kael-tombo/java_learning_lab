# REAL-WORLD PROJECT — Class Loading: Duplicate Jar Freezes Deploy

## Incident Scenario
After a dependency bump, payments deploy throws `NoSuchMethodError:
FeeTable.get(int)` in prod only. Same artifact passed CI. Rollback
works; re-deploy fails again. Two versions of `pricing-core` ride
along — one shaded in an uber-jar, one transitive — and loader order
decides which wins per environment.

## Symptoms
- `NoSuchMethodError` on a method present in source; `javap` on CI jar
  vs prod jar differs (one has old signature).
- `-verbose:class` shows `FeeTable loaded from uber.jar` on prod but
  `pricing-core-2.4.jar` on staging — order-dependent winner.
- Identical-name `ClassCastException`: `Pricer cannot be cast to
  Pricer` with same FQN (plugin loader vs app loader both bundle it).
- Metaspace grows 180MB → 420MB across redeploys (old loaders pinned
  by a static cache + surviving thread).
- Agent (APM) rewrites the class at load; disabling agent changes the
  stack — retransformation suspected in one variant.

## Investigation Tasks
1. Class origin: restart with `-verbose:class` to file; `grep FeeTable
   verbose.log`; record exact jar per env. Confirm with `jcmd <pid>
   GC.class_stats` / heap dump class-loader view.
2. Dependency forensics: `mvn dependency:tree -Dincludes=:pricing-core`
   (or gradle equivalent); find duplicate; `unzip -l uber.jar | grep
   FeeTable` proves shading duplication.
3. JFR: `jcmd <pid> JFR.start name=cls settings=profile duration=120s
   filename=cls.jfr`; inspect `jdk.ClassLoad`, `jdk.ClassDefine`,
   `jdk.JavaExceptionThrow` (the NoSuchMethod site) in JMC.
4. Loader identity: heap dump → dominator of `FeeTable` class object;
   print `classLoader.toString()` hash for both copies; reproduce CCE
   with explicit cross-loader cast in jshell/test.
5. Leak: two redeploys → heap dumps; path-to-GC-root of old
   `URLClassLoader` (static map + non-daemon thread + JDBC registration).

## Root Cause
Diverged compile/runtime classpaths (shaded + transitive duplicates)
plus cross-loader type leakage and a static/thread leak pinning old
loaders. Environment-specific jar ordering made CI green, prod red.

## Resolution
- Immediate: pin `pricing-core` to single version, exclude transitive
  copy; deploy with `-verbose:class` assertion in smoke test; move
  shared `Pricer` API to parent loader only.
- Short-term: enforce `maven-enforcer requireUpperBoundDeps +
  banDuplicateClasses`; shade-relocate (not bundle) internals;
  agent allowlist for transform targets.
- Long-term: plugin contract (host API vs impl split), closeable
  loaders, unload soak in CI, SBOM + jar-diff on every release.

## Runbook
```
1. Capture verbose:class + JFR + heap dump BEFORE rollback (evidence).
2. Roll back; diff CI vs prod jars (javap + unzip -l) to name the dup.
3. Patch POM (pin + exclusion + enforcer) to canary; verify origin line single-sourced.
4. Redeploy; assert FeeTable origin + 0 CCE; watch metaspace flat 24h.
5. Unload soak: 5 deploy cycles, loader weak-refs cleared each time.
6. Land enforcer + verbose:class smoke + SBOM gate.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| NoSuchMethodError | 100% deploys | 0 (20 deploys) | Smoke greps origin |
| Duplicate classes | 2 copies | 1 (enforcer) | Build fails on dup |
| Metaspace (3 redeploys) | 420MB | 190MB flat | Alert +50MB |
| CCE incidents | 34/day | 0 | Loader-boundary test |
| Deploy MTTR | 55 min | <10 min | Runbook drill |

## Prevention Checklist
- [ ] Enforcer bans duplicate classes/upper-bound violations
- [ ] Host/plugin API split, never bundle API in plugin
- [ ] Loaders closeable + unload test in CI
- [ ] Jar-diff + SBOM on release

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Class loading / verifier docs: https://docs.oracle.com/en/java/javase/21/docs/api/
- OpenJDK class-loading / JSR infrastructure: https://openjdk.org/projects/jdk/21/
