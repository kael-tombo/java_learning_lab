# FLASHCARDS — Java Migration

Every row is a version attribution or a migration gotcha. Miss a row, reread the
matching THEORY.md section.

## The three compatibility surfaces

| Q | A |
|---|---|
| Three surfaces an upgrade breaks | Source (compile), binary (link/boot), behavioural (silent wrong result) |
| Which surface does `--release` protect | Source only |
| Which surface has no compiler and no stack trace | Behavioural |
| Binary surface detection | Boot the old jar: `NoSuchMethodError`, `IllegalAccessError` |
| Behavioural surface detection | Golden-file / parity tests, shadow-traffic diffing |
| `String.hashCode()` across JDK 8→21 | Unchanged; the churn is `HashMap` resize *order* (JDK 8, order only) |
| `Stream`/`Optional` null strictness | JDK 9+ — `NullPointerException` surfaces earlier, not later |

## `--release` vs `-source`/`-target`

| Q | A |
|---|---|
| `--release` validates against | JDK N's API signature data (`ct.sym`), not the running JDK |
| `-source`/`-target` link against | The *current* JDK's API → `NoSuchMethodError` in production |
| `--release` also sets | Language level, class-file version, **and** bootclasspath |
| Class-file major versions | 52 = 8, 55 = 11, 61 = 17, 65 = 21 |
| `-Werror` with `-Xlint:all` | Turns every warning into a blocker — useful for `--release` bumps |

## Build tooling

| Q | A |
|---|---|
| Maven property that replaces source/target | `<maven.compiler.release>17</maven.compiler.release>` |
| Maven enforcement of minimum build JDK | `maven-enforcer-plugin` + `<requireJavaVersion>` |
| Gradle mechanism to pin compile+test JDK | `java { toolchain { languageVersion = JavaLanguageVersion.of(17) } }` |
| Build tooling drift without a toolchain | Gradle compiles with whatever `JAVA_HOME` points at |
| Container base image pinning | Pin the JDK image by digest; floating `openjdk:21` tags move under you |
| Build-JDK vs run-JDK skew | Allowed, dangerous — you compile against a superset of what ships |

## Removed APIs and modules

| Q | A |
|---|---|
| `javax.xml.bind` (JAXB) removed | JDK 11 (deprecated 9) → `jakarta.xml.bind-api` + impl |
| `java.activation` (JAFB) removed | JDK 11 → `jakarta.activation-api` |
| `java.corba` removed | JDK 11 → no drop-in replacement |
| Nashorn / `jjs` removed | JDK 15 (JEP 372); deprecated 11 (JEP 335) → GraalJS or Node |
| `java.util.jar.Pack200` | Deprecated 13 (JEP 336), removed 14 (JEP 367) → `jlink` / module image |
| `javah` removed | JDK 10 → `javac -h` |
| CMS collector removed | JDK 14 (JEP 363); deprecated 8 (JEP 291) → G1 or ZGC |
| ParallelFullGC for G1 removed | JDK 23 (JEP 475, late barrier expansion, removes it) — added in 10 (JEP 307); different thing |
| Applet API removed | JDK 26 (JEP 504, Remove the Applet API); deprecated 9 (JEP 289 is VarHandle — a common mix-up) |
| `-XX:+PrintGCDetails` / `PrintGCTimeStamps` | Gone; use `-Xlog:gc*` |
| `Class.newInstance()` | Deprecated 9 → `getDeclaredConstructor().newInstance()` |
| `System.runFinalizersOnExit` | Deprecated 10 → `Runtime.addShutdownHook` |
| Finalizers deprecated for removal | JDK 18 (JEP 421) |
| `AccessController.doPrivileged` | Deprecated 17; SecurityManager permanently disabled 24 (JEP 486) |
| `sun.misc.Unsafe` memory-access methods | Deprecated for removal 23, warnings in 24 → `VarHandle` |
| `Unsafe.defineAnonymousClass` | Removed 17 → upgrade cglib/Mockito; no flag fix |
| Removed-module symptom | `package javax.xml.bind does not exist`, or `NoClassDefFoundError` at runtime |

## Encapsulation and modules

| Q | A |
|---|---|
| Module system (JPMS) introduced | JDK 9 (JEP 261) |
| `--illegal-access=permit` default | JDK 9–16, effectively ignored from 17 |
| Strong encapsulation enforced | JDK 17 (JEP 403) |
| Symptom of encapsulation failure | `java.lang.reflect.InaccessibleObjectException` |
| Surgical escape hatch | `--add-opens java.base/java.lang=ALL-UNNAMED` |
| `--add-opens` vs `--add-exports` | `opens` = deep reflection; `exports` = compile/link access only |
| Module-aware reflection API | `MethodHandles.privateLookupIn(target, MethodHandles.lookup())` |
| Best fix for an `--add-opens` need | Drop the internal API, then upgrade the library that needed it |
| `--add-opens` debt discipline | Tracked list, named owner, `LEGACY-####` ticket, deletion date |

## Behavioural changes (silent, highest severity)

| Q | A |
|---|---|
| Default charset → UTF-8 | JDK 18 (JEP 400) |
| JEP 400 escape hatch | `-Dfile.encoding=COMPAT`, or set `LANG` |
| JEP 400 real risk | Containers with no `LANG`: ASCII default before, UTF-8 now |
| Locale data provider → CLDR default | JDK 9 (JEP 252, Use CLDR Locale Data by Default) |
| CLDR-affected APIs | `DateFormat`, `NumberFormat`, `String` casing, `Collator` |
| Classic CLDR surprise | Turkish dotless-i: `"i".toUpperCase(new Locale("tr"))` → `İ` |
| ZGC promoted to production | JDK 15 (JEP 377); experimental in 11 (JEP 333) |
| Shenandoah promoted to production | JDK 15 (JEP 379) — a different JEP from ZGC's, a frequent mix-up |
| ZGC generational mode | JDK 21 (JEP 439, Generational ZGC); default 23 (JEP 474) — re-baseline p99 SLOs |
| G1 becomes the default collector | JDK 9 (JEP 248) |
| Generational Shenandoah | Experimental 24 (JEP 404), default 25 (JEP 521) |
| Sealed classes | Preview 15 (JEP 360) / 16 (JEP 397), final 17 (JEP 409) |
| Records | Preview 14 (JEP 359) / 15 (JEP 384), final 16 (JEP 395) |
| Risk from synthesized methods | Hand-written vs generated equality can differ → Map/set behaviour shifts |
| Pattern matching for `switch` | Preview 17–20, final 21 (JEP 441) |
| Virtual threads | Preview 19/20, final 21 (JEP 444) |
| Structured concurrency | Still **preview** in 21 (JEP 453) — not production-ready |
| String templates | Preview 21 (JEP 430), **withdrawn** — don't plan on it |
| Preview feature production rule | Same-JDK compile *and* run; preview bytecode won't load on the next JDK |

## JEP index

| Q | A |
|---|---|
| JEP 261 | Module System (JDK 9) |
| JEP 252 | CLDR as default locale provider (JDK 9) |
| JEP 248 | G1 as default GC (JDK 9) |
| JEP 289 | `VarHandle` (JDK 9) — the `Unsafe` replacement |
| JEP 213 | Milling Project Coin (JDK 9) — includes the try-with-resources enhancement allowing effectively-final variables outside the resource list |
| JEP 307 | Parallel full GC for G1 (JDK 10) |
| JEP 336 | Deprecate `Pack200` (JDK 13) |
| JEP 363 | Remove CMS (JDK 14) |
| JEP 367 | Remove `Pack200` (JDK 14) |
| JEP 372 | Remove Nashorn (JDK 15) |
| JEP 377 | ZGC production-ready (JDK 15) |
| JEP 403 | Strongly Encapsulate JDK Internals (JDK 17) |
| JEP 409 | Sealed classes final (JDK 17) |
| JEP 411 | Deprecate SecurityManager for removal (JDK 17) |
| JEP 400 | UTF-8 by default (JDK 18) |
| JEP 416 | Core reflection on method handles (JDK 18) |
| JEP 421 | Deprecate finalization for removal (JDK 18) |
| JEP 439 | Generational ZGC (JDK 21) |
| JEP 441 | Pattern matching for switch (JDK 21) |
| JEP 444 | Virtual threads (JDK 21) |
| JEP 453 | Structured concurrency preview (JDK 21) |
| JEP 471 / JEP 498 | `sun.misc.Unsafe` memory-access methods deprecated (23) / disabled (24) |
| JEP 486 | Permanently disable the SecurityManager (JDK 24) |
| Canonical index | <https://openjdk.org/jeps/0> |

## Inventory and static gates

| Q | A |
|---|---|
| Highest-value first migration command | `jdeps --jdk-internals -R target/app.jar` |
| `jdeps` clean output | `-> No dependencies inside the JDK internal API.` |
| Animal Sniffer checks | Bytecode/API against a signature set (`java18`, `java11`, …) |
| Animal Sniffer covers | Pre-compiled dependencies — what `--release` cannot see |
| forbidden-apis checks | Calls to JDK internals / non-public APIs |
| Binary-compat checkers | `revapi`, `japicmp`, Clirr |
| Reflection reachability test | `setAccessible(true)` on every reflected member; fail on throw |
| Detector: surviving CMS flags | `grep -rn 'UseConcMarkSweepGC\|PrintGCDetails\|PrintGCDateStamps' .` |
| Detector: unguarded charsets | `grep -rn 'new String(\|FileReader(' src/ \| grep -v Charset` |
| Detector: platform-locale assumptions | `grep -rn 'String\.format(' src/ \| grep -v Locale` |
| Detector: `--illegal-access` reliance | `grep -rn 'illegal-access' --include='*Dockerfile*' .` |
| Detector: internal imports | `grep -rn '^import sun\.\|^import jdk\.internal\.' src/` |

## Tooling replacements

| Q | A |
|---|---|
| `sun.misc.Unsafe` memory ops → | `VarHandle` (JDK 9, JEP 289) |
| `sun.nio.ch.DirectBuffer` → | `ByteBuffer`; usually drop direct memory entirely |
| `sun.security.x509` parsing → | `java.security.cert.CertificateFactory` |
| `com.sun.net.ssl.*` → | JSSE: `SSLContext`, `TrustManager` |
| `Pack200` → | `jlink` runtime image, or plain classpath |
| `jjs` → | GraalJS in a separate process, or move logic to Node |
| `Class.newInstance()` → | `clazz.getDeclaredConstructor().newInstance()` |
| `AccessController.doPrivileged` → | Delete it; the module system already scopes access |
| Hand-annotated JAXB classes | XSD + `maven-jaxb2-plugin` |
| Old ORM / bytecode generators | Upgrade the library — `defineAnonymousClass` has no flag fix |

## Rollout and rollback

| Q | A |
|---|---|
| Canary scope | One AZ, 1–5% traffic, SLO-gated for a full business cycle |
| Why a full business cycle | Weekend traffic is a different shape than weekday |
| Rollback without rebuild | Previous image pre-tagged and pullable; rollback = image swap |
| Cost of a rebuild-required rollback | ~20 minutes, spent entirely out of the error budget |
| Promotion gates | SLOs green **at required sample size**, plus shadow-diff within tolerance |
| Sequential rollout shape | 1% → 5% → 25% → 50% → 100%, per region |
| Shadow / dual-run | Mirror traffic to both versions, diff responses, alert on divergence |
| Blast-radius ordering | Lowest-blast-radius service first that still exercises the risky libs |
| Decommission step | Delete old image, remove `--add-opens`, close tickets, drop `-source` fallbacks |
| Single-hop vs staged | Single-hop 8 → 21; 17 as a *separate release* if a dependency blocks it |
| Sequencing discipline | Libraries first, JDK second — never both in one deploy |
| Why that matters | Both together destroys regression attribution |
| Migration done when | Old fleet decommissioned and rollback path closed — not when it compiles |

## Target JDK selection

| Q | A |
|---|---|
| Commercial constraint, no forcing function | Stay on the current LTS |
| Vendor support deadline | Next LTS, plan 8–12 weeks |
| Library dropped old-JDK support | Newest LTS you can qualify — let the dependency set the target |
| Container base image / host OS EOL | Next LTS; infrastructure forces the hand |
| Want virtual threads | JDK 21+ |
| Want structured concurrency final | **Not yet** — it was incubator from 19 and reached only its fifth preview by 25 (JEP 505). Do not plan on it |
| Long-horizon modernization, active team | JDK 25 — largest gain, largest jump |
| Modernization value today (21 vs 17) | Virtual threads, pattern matching for switch, generational ZGC |
| Modernization value today (25 vs 21) | Module import declarations, compact object headers (opt-in), Scoped Values, flexible constructor bodies. Note: structured concurrency is **still preview** in 25, so do not plan on it |
| Risk-scoring formula | `blast_radius × detectability × effort`, weighted (MATH_FOUNDATION.md §1) |