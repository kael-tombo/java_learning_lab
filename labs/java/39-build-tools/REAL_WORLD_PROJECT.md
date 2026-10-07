# REAL-WORLD PROJECT — Build Tools: Unreproducible Release + Poisoned Dependency

## Incident Scenario
Friday release built on a laptop ships a `SNAPSHOT` + range-resolved Jackson
with a CVE; prod NoSuchMethodErrors at midnight, SBOM absent, and nobody can
rebuild the tag — CI takes 28 min and fails offline.

## Symptoms
- `NoSuchMethodError: ObjectMapper.readValue` on 20% pods (mixed Jackson).
- `grep SNAPSHOT pom.xml` hits; version ranges (`[2,)`) resolve differently
  per machine; `dependency:tree` differs laptop vs CI.
- CI no cache, serial tests, downloads plugins every run; Docker `COPY .`
  before deps invalidates cache each commit.
- Compromised transitive dep (typosquat) merged without scan; no signature.
- Release = manual `package` + SCP; rollback artifact missing.

## Investigation Tasks
1. Diff the graphs: `mvn dependency:tree -Dverbose` (or
   `gradle dependencies --scan`) on laptop vs CI vs prod image — record
   Jackson divergence + typosquat entry path.
2. Runtime: `jcmd <pid> VM.command_line` + `jcmd <pid> Thread.print` on a
   crashing pod; `jcmd <pid> JFR.start duration=60s filename=build.jfr`
   only to rule out perf red herring (incident is supply-chain, stay focused).
3. Heap (optional): `jcmd <pid> GC.heap_dump` only if OOM also present;
   else prioritize `jimage`/jar listing (`unzip -l app.jar | grep jackson`).
4. Cache audit: CI timings per stage (checkout/deps/compile/test/image);
   `du -sh ~/.m2` history; Docker layer list showing cache miss.
5. Repro: clean-clone + `--offline` build (fails = non-hermetic proof);
   rebuild tag twice, `sha256sum` artifacts (differ = unreproducible).
6. Scan: run `dependency-check` + CycloneDX on the tag; list criticals and
   the typosquat coordinates + which PR introduced it.
7. Release audit: who built, from which commit, with what JDK
   (`java -version` vs CI image digest).

## Root Cause
Floating versions + unpinned plugin/JDK + cache-hostile CI + no scan/SBOM/
signing + manual releases — every build a snowflake, every dep implicitly
trusted.

## Resolution
- Immediate: pin Jackson (BOM), kill ranges/SNAPSHOTs, purge typosquat,
  rebuild from CI tag, redeploy known-good previous image.
- Short-term: version catalog/BOM + lockfiles, enforcer (ban floats/dupes),
  cached CI (< 5 min), dep-scan + SBOM + sign gates, `COPY pom first` layers.
- Long-term: release train (tag → image + provenance), SLSA/Sigstore,
  Renovate/Dependabot policy, build-perf budget, offline-build drill.

## Runbook
```
1. Freeze manual releases; capture tree diffs + scan report.
2. Pin + purge bad dep; CI-tagged rebuild; verify sha + smoke.
3. Roll fleet to CI image; keep prior tag staged for rollback.
4. Enable scan/SBOM/sign gates; cache-fix Dockerfile.
5. Postmortem: dep-add checklist + release runbook.
```

## Metrics
- Rebuilds bit-identical (sha match) 3/3; offline build passes.
- CI < 5 min; critical CVEs = 0 untriaged; SBOM+signature on every release.
- Mixed-version `NoSuchMethodError` = 0; rollback drill < 10 min.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring Boot build plugins: (link removed)
- jlink reference: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html
