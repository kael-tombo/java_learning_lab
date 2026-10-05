# QUIZ — Java Migration

Aim 16/20. Miss any of 1–7 and reread THEORY.md §1–§2.

**1. Name the three compatibility surfaces.** Source (does it compile), binary (do old jars link), behavioural (same code, different result). Only the third has no compiler and no stack trace helping you.
**Answer:** Source → `javac --release N`; binary → `NoSuchMethodError`/`IllegalAccessError` at boot; behavioural → wrong data, no exception. `--release` protects only source.

**2. `--release 17` vs `-source 17 -target 17`.** Which is correct, and why does it matter?
**Answer:** `--release`. It compiles against JDK 17's API signature data (`ct.sym`); `source`/`target` set the language level and class-file version but still link against the *running* JDK's API, so you can compile a call that doesn't exist on the runtime you ship and get `NoSuchMethodError` in production.

**3. Which JDK removed `javax.xml.bind`, and what is the fix?**
**Answer:** JDK 11 (deprecated 9). Add `jakarta.xml.bind-api` + an implementation (`org.glassfish.jaxb:jaxb-runtime`) and rename imports. A dependency problem, not a code problem — the classes are simply absent from the JDK.

**4. When did strong encapsulation become enforced, and which flag became a no-op?**
**Answer:** JDK 17 (JEP 403). `--illegal-access` (a `permit` default from JDK 9) is ignored. Symptom: `InaccessibleObjectException` from `setAccessible` into `java.base`.

**5. List three legitimate fixes for an `--add-opens` need, best first.**
**Answer:** (1) Stop using the internal API — `MethodHandles.privateLookupIn` or `VarHandle`. (2) Surgical `--add-opens java.base/java.lang=ALL-UNNAMED`, tracked as debt with an owner and a deletion date. (3) Upgrade the library that created the need (Mockito, cglib, old Hibernate, hand-rolled `Proxy`).

**6. What changed in JDK 18 about charsets, and how do you defend?**
**Answer:** JEP 400 made UTF-8 the default charset everywhere, independent of platform locale. A container with no `LANG` previously defaulted to ASCII. Defend by making every read/write charset-explicit (`Files.readString(p, ISO_8859_1)`, `new String(bytes, cs)`) and grepping for the bare constructors.

**7. What does Animal Sniffer catch that `javac --release` does not?**
**Answer:** Pre-compiled dependencies. `--release` only checks code you compile; a jar built on JDK 17 can still call `Files.readString` and reach a JDK 11 runtime. You need both — or `revapi`/`japicmp` for binary checks.

**8. What replaces each removal?** JAXB/JAFB (11) → `jakarta.*` artifacts. Nashorn/`jjs` (15) → GraalJS or Node. Pack200 (14) → `jlink`. CMS (14, JEP 367) → G1 or ZGC. `javah` (10) → `javac -h`. `SecurityManager` disabled by default (18), terminally deprecated 24 (JEP 486).

**9. Your p99 regressed 8% on the canary. Why is 5% traffic not enough, and what gates promotion?**
**Answer:** 5% of traffic yields far too few *tail* events for a p99 verdict. Gate on request count (`min_samples`), not elapsed time, plus a full business cycle including weekend — a different traffic shape. Promote only when SLOs are green at required sample size, not when "no alerts yet."

**10. What makes a rollback "without rebuild," and why insist?**
**Answer:** The previous image stays tagged and pullable, so rollback is an image swap, not a re-run of the build. A rebuild-required rollback takes ~20 minutes, spent entirely out of the error budget you were protecting. Drill it and record the wall-clock.

**11. `-source 8 -target 8` compiles clean; production throws `NoSuchMethodError` on JDK 17. Diagnose.**
**Answer:** Code linked against a newer API than JDK 8 has, or a transitive dependency did. Re-compile your own source with `--release 8`, then inspect the *jars* with `jdeps --jdk-internals` and Animal Sniffer. Binary surface: `--release` never sees inside a dependency.

**12. A library calls `Unsafe.defineAnonymousClass`. What breaks, and is there a flag fix?**
**Answer:** JDK 17 — old cglib and early Mockito fail with `NoSuchMethodError` during proxy generation. No flag fixes it; upgrade the library. Clearest example of a binary break: your source compiles fine because the call is inside someone else's bytecode.

**13. True/false: `-XX:+UseConcMarkSweepGC` still works with `-XX:+IgnoreUnrecognizedVMOptions`.**
**Answer:** False. CMS was removed in JDK 14 (JEP 367); the flag no longer exists and that JVM option only silences *experimental/unknown* flags, not removed ones — startup fails. Migrate to G1/ZGC, including logging renames (`-XX:+PrintGCDetails` → `-Xlog:gc*`).

**14. Locale-sensitive invoice text changed after the upgrade but no test failed. Why?**
**Answer:** CLDR became the default locale provider in JDK 9 (JEP 252), so `DateFormat`/`NumberFormat` output differs from old JRE data. A test asserting *parsed values* sees nothing; only the formatted string changed. Add per-locale golden files and pin formatting with explicit `DateTimeFormatter`.

**15. Preview features in 21 — what's the production rule?**
**Answer:** `--enable-preview` at compile *and* run, same JDK only: preview bytecode from 21 will not load on 22. Never ship previews in the production JDK. And port twice — the final switch-pattern API differs from the 17/18 previews (guard syntax, `when` clauses).

**16. Which service goes first on a fleet migration, and why not the biggest?**
**Answer:** The lowest blast-radius service that still exercises the risky shared libraries. The first migration buys you the `--add-opens` catalogue, the encoding audit, and the canary/rollback runbook cheaply. Migrating the biggest revenue service first maximises the cost of being wrong.

**17. A dependency chain blocks 17. Do you stage 17 or skip to 21?**
**Answer:** Single-hop when possible. If something only works on 17, treat 17 as a **staging release with its own deploy and SLOs**, not a phase of one release — then upgrade the blocker and go 17 → 21. See VISION.md.

**18. Compact strings (Latin-1 storage, JDK 9) — correctness risk?**
**Answer:** None; `String` semantics are identical. It changes memory accounting for Latin-1 workloads (~halved), so heap sizing and OOM thresholds tuned on the old footprint become wrong. Re-tune; don't carry the numbers forward.

**19. Why doesn't a JDK upgrade upgrade dependencies, and why sequence libraries first?**
**Answer:** Classpath and JDK are independent; old dependencies are the actual blockers. Doing libraries and JDK in one deploy destroys attribution — every regression becomes "maybe the JDK, maybe the lib." Upgrade libs first, or never both together.

**20. After 100% rollout on 21, what is still outstanding?**
**Answer:** Decommission: delete the JDK 8 image, remove `--add-opens` and compatibility flags, close the debt tickets, delete the `-source 8` fallback profiles. This step is routinely skipped, so flags become permanent and unowned. The migration isn't done when it compiles — it's done when the flags are gone.