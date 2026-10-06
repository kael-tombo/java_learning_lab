# FLASHCARDS — Java Version History

One row per feature attribution or per design decision. Sections follow THEORY.md.
Miss a row, reread that section. 112 rows, grouped so you can drill one version at
a time rather than all of them at once.

## 1.2 — The Professional Release (1999)

| Q | A |
|---|---|
| `StringBuffer` introduced | 1.2 — the first API admission that string building matters |
| Collections framework (`List`/`Map`/`Set`) | 1.2 — the platform's first mature reusable data-structures package |
| Pressure that produced 1.2 | Java 1.0's credibility: "applets are slow" needed a client-server story |

## 1.4 — Assertions, Logging, XML (2002)

| Q | A |
|---|---|
| `java.util.logging` | 1.4 — Java admitting it lacked observability tooling |
| Why JUL is still in the JDK despite Log4j/SLF4J winning | It is the *only* JDK logging API, so it still causes classpath conflicts |
| `ChainedRuntimeException` | 1.4 — cause chains, the root of modern stack-trace diagnosis |

## 1.5 — Concurrency (2004)

| Q | A |
|---|---|
| `java.util.concurrent` | 1.5 — the pivotal version of the timeline |
| Five locking mechanisms at once | `synchronized`, `ReentrantLock`, `ReadWriteLock`, atomics, `CountDownLatch`/`Semaphore` |
| What 1.5 did *not* fix | The memory model — undefined until the JSR 133 rewrite (5, 2004); 16 years of subtle bugs |

## 5 — Generics (2004)

| Q | A |
|---|---|
| Generics, `enum`, autoboxing, varargs, `StringBuilder`, `StringJoiner` | All JDK 5 |
| `enum` shipped because | `static final int` constants could not be switched on without subclassing |
| Why no `new T[]`, no `instanceof List<String>`, no generic overloads | Erasure — the type argument is not reifiable; use `instanceof List<?>` |

## 6 — Concurrency, finished (2006)

| Q | A |
|---|---|
| Blocking queues, `ConcurrentNavigableMap`, `ExecutorService` ergonomics | 6 — 1.5 shipped the idea; 6 shipped a usable API |
| De/serialization API cleanup | 6 |

## 7 — Project Coin (2011)

| Q | A |
|---|---|
| `try`-with-resources | 7 (JSR 334) — killed the `finally { close() }` bug |
| Diamond `<>` | 7 — but too weak until 8/9/10 to infer from a target type |
| `switch` on strings, multi-catch, `1_000_000` literals | All 7 |
| Why "Coin" mattered | 25 community-voted changes proved ergonomics could ship without big-bang risk |

## 8 — Lambda era (2014)

| Q | A |
|---|---|
| Lambdas, method references, `@FunctionalInterface` | 8 — via `invokedynamic`, not anonymous classes |
| `Stream` API | 8 |
| `Optional` | 8 — intended for **return types only**, a contract never honoured |
| `java.time`, `CompletableFuture`, default/static interface methods | 8 — the last unblocked interface evolution and created the diamond problem |
| Pressure (three, at once) | Functional programming won; collections were sequential-only; interfaces could not grow |

## 9 — Modularity + collection APIs (2017)

| Q | A |
|---|---|
| Module system (Jigsaw, JSR 376, JEP 261) | 9 |
| G1 default GC (JEP 248) / CLDR locales (JEP 252) | Both 9 — the latter a silent formatting change |
| Compact strings (Latin-1 storage) | 9 — halved Latin-1 `String` memory, zero semantic change |
| `List.of` / `Map.of`, `takeWhile`/`dropWhile`, `jlink`, restricted `var` | All 9 |
| Why JPMS adoption was the slowest of any major feature | Split-package restrictions broke the ecosystem; poor migration story |

## 10 — Local type inference (2018)

| Q | A |
|---|---|
| `var` for local variables (JEP 286) | 10 — unrestricted in for-loop headers and try-with-resources |
| Arrow-form `switch` | 10 — the statement form; the *expression* form is 12 preview / 14 final |
| Why 9 → 10 was a split | Explicit rejection feedback: `var` on anonymous classes and initializers failed |

## 11 — HTTP client, var in lambda params (2018, LTS)

| Q | A |
|---|---|
| `java.net.http.HttpClient` | 11 (LTS) — replaces `HttpURLConnection`, adds HTTP/2 |
| `var` in lambda parameters (JEP 323) | 11 |
| `String.strip`/`repeat`/`lines`/`isBlank`, `Files.readString`/`writeString` | 11 |
| Single-file source execution (`java Hello.java`); ZGC experimental (JEP 333) | 11 |
| JAXB / JAFB / CORBA removed (deprecated 9) | 11 |

## 12–13 — Switch expressions, text blocks (2019)

| Q | A |
|---|---|
| Switch expressions preview (JEP 325) | 12 |
| Text blocks preview (JEP 355) | 13, then second preview 14 (JEP 368) |
| Switch expressions second preview (JEP 354) | 13 — final 14 (JEP 361), `yield` included |
| `Files.mismatch`, `CharBuffer` | 13 |
| Friction point | Exhaustive switch over `enum` with no `default` — a real problem for libraries |

## 14 — The garbage collector purges (2020)

| Q | A |
|---|---|
| Text blocks standard | 15 (preview 13/14) |
| CMS collector **removed** (JEP 363) | 14 — deprecated 8 (JEP 291) |
| Pack200 **removed** (JEP 367) | 14 — deprecated 13 (JEP 336); replaced by `jlink` |
| Nashorn deprecated (JEP 335) | 11 — **removed** in 15 (JEP 372) |
| Principle | Removal for *simplification*, not capability |

## 15 — The preview year (2020, LTS)

| Q | A |
|---|---|
| Records preview 2nd (JEP 384); sealed preview (JEP 360) | 15 — records preview 1st was 14 (JEP 359) |
| ZGC production-ready (JEP 377); Shenandoah production (JEP 379) | 15 — ZGC experimental in 11 (JEP 333) |
| Finalization deprecated for removal (JEP 421) | 18 — *not* 23; this is where `finalize()` warnings began |
| Why preview features exist | The 6-month cadence made "too much new surface per release" a real risk |
| Preview benefit vs cost | Designs refined *substantially* while gated; code is not portable across releases |

## 16 — Records and sealed types (2021, LTS)

| Q | A |
|---|---|
| Records standard (JEP 395); `instanceof` pattern matching standard (JEP 394) | 16 — `instanceof` pattern preview was 14 (JEP 305) |
| `Stream.toList()` | 16 |
| Records are | **Shallowly** immutable — a `List` component is still mutable |
| Sealed still preview in 16 | Yes — preview 15 *and* 16, standard 17 |

## 17 — Sealed + encapsulation lands (2021, LTS)

| Q | A |
|---|---|
| Sealed classes standard (JEP 409) | 17 — sealed previewed in 15 *and* 16 |
| Strongly Encapsulate JDK Internals (JEP 403) | 17 — `--illegal-access` becomes a no-op |
| Note on JEP 406 | That is *Pattern Matching for switch (Preview)*, delivered in **17** — it is not the switch-pattern final |
| Symptom of JEP 403 | `java.lang.reflect.InaccessibleObjectException` from `setAccessible` |
| `permits` commitment / cost | Adding a subtype is source-breaking everywhere; the largest migration pain since 9 |

## 18 — UTF-8 by default (2022, LTS)

| Q | A |
|---|---|
| UTF-8 as the default charset (JEP 400) | 18 — escape hatch `-Dfile.encoding=COMPAT` |
| `SimpleWebServer` | 18 |
| Why it mattered | The default charset was OS-locale-dependent — platform-dependent behaviour |
| The most under-appreciated migration risk | Yes — silent data corruption, no exception |
| Core reflection reimplemented on method handles (JEP 416) | 18 — also a source of reflective-access changes |
| Finalization deprecated for removal (JEP 421) | 18 |

## 19 — Records in switch, virtual threads preview (2022)

| Q | A |
|---|---|
| Virtual threads **preview** (JEP 425) | 19 — first preview; *not* 18 |
| Record patterns preview (JEP 405); `java.lang.foreign` preview (JEP 424) | 19 |
| Structured concurrency **incubator** (JEP 428) | 19 — incubator, a weaker gate than preview |
| Switch patterns preview 3rd (JEP 427) | 19 — the switch-pattern final is JEP 441 in **21** |
| Pressure on platform threads | ~1 MB stack each, OS-thread-bound → high-concurrency IO was uneconomic |

## 20 — Pattern matching everywhere (2023)

| Q | A |
|---|---|
| Virtual threads preview 2nd (JEP 436); structured concurrency 2nd preview (JEP 437); record patterns 2nd preview (JEP 432) | 20 |
| Switch patterns preview 4th (JEP 433) | 20 |
| Why 20 mattered | Pattern matching reached feature-complete *as a whole* — but the switch parts were still preview here |
| Correction worth knowing | Record patterns (JEP 440) and virtual threads (JEP 444) shipped in **21**, not 20 |
| The trade-off | Exhaustive switch is compiler-checked, so adding a subtype is a compile break everywhere |

## 21 — The LTS consolidation release (2023, LTS)

| Q | A |
|---|---|
| Virtual threads standard (JEP 444); record patterns (JEP 440); switch patterns (JEP 441) | 21 — the modern-concurrency baseline |
| Generational ZGC (JEP 439); sequenced collections (JEP 431); string templates preview (JEP 430) | 21 |
| Scoped values preview (JEP 446); structured concurrency preview (JEP 453) | 21 |
| Dynamic agent loading to be restricted (JEP 451) | 21 — *not* a virtual-thread builder API |
| Sizing guidance inverted | One virtual thread per task; a fixed pool is now an anti-pattern |
| Why existing pool code is dangerous | It kept compiling and silently stopped being the right shape |

## 22 — Unnamed patterns and variables (2023)

| Q | A |
|---|---|
| Unnamed variables and patterns `_` (JEP 456) | 22 |
| Implicitly declared classes / instance main preview 2nd (JEP 463) | 22 — the second program form with no `public class` |
| Class-File API preview (JEP 457); FFM API final (JEP 454, Foreign Function & Memory) | 22 — Class-File API went final in 24 (JEP 484) |

## 23 — ZGC generational, string templates (2023)

| Q | A |
|---|---|
| Generational ZGC default (JEP 474) | 23 — brought G1-class pause behaviour to large heaps by default |
| String templates 2nd preview (JEP 459) | 23 — withdrawn (JEP 465) after API criticism |
| Markdown documentation comments (JEP 467) | 23 |
| Generational Shenandoah (experimental, JEP 404) | 24 — promoted to default in 25 (JEP 521) |

## 24 — Generational Shenandoah (2024, LTS)

| Q | A |
|---|---|
| SecurityManager permanently disabled (JEP 486) | 24 — deprecated 17 (JEP 411), terminally deprecated then |
| `Stream` gatherers (JEP 485) | 24 — the sanctioned extension point |
| Class-File API final (JEP 484) | 24 — preview 22 (JEP 457) |
| AOT class loading & linking (JEP 483) | 24 |
| Flexible constructor bodies preview 3rd (JEP 492) | 24 |
| Synchronize virtual threads without pinning (JEP 491) | 24 — resolves the JDK 21/22 pinning problem |
| Note on JEP 521 | Generational Shenandoah went **default in 25**, not 24; 24 shipped it as experimental |

## 25 — The current frontier (2025, LTS)

| Q | A |
|---|---|
| Compact object headers (JEP 519) | 25 — header goes 12–16 B → 8 B, so **4–8 B** saved per object, NOT 16 |
| Compact headers experimental (JEP 450) | 24 — the experimental gate; 519 only removed the gate |
| Compact headers default? | **Still off in 25.** JEP 519 kept it opt-in; JEP 534 tracks making it default |
| Module import declarations (JEP 511) — `import module java.base` | 25 — the ergonomic counterweight to JPMS |
| Flexible constructor bodies standard (JEP 513); Scoped Values standard (JEP 506) | 25 |
| Compact source files and instance main (JEP 512) | 25 — preview graduated in 24 (JEP 495) |
| Generational Shenandoah (JEP 521) default | 25 — experimental in 24 |
| AOT method profiling (JEP 515); AOT command-line ergonomics (JEP 514) | 25 |
| Pressure 1 | Memory density — object headers had been a fixed cost since 1.0 |
| Pressure 2 | Migration friction — `import module` attacks what stalled JPMS |
| Pressure 3 | Concurrency completion — ScopedValue + StructuredTaskScope close the 19→25 Loom roadmap |
| Cost of compact headers | Heap dumps, memory accounting, and layout assumptions must be revalidated |

## Cross-cutting: the four patterns

| Q | A |
|---|---|
| Pattern 1 — boilerplate elimination follows widespread pain | Generics (5), try-with-resources (7), lambdas (8), records (16) |
| Pattern 2 — preview became the release valve | Since 12–14; 1–4 releases; also a way to *kill* a design |
| Pattern 3 — API evolution mechanisms are features | Default methods (8), modules (9), preview (12+), compact headers (25) |
| Pattern 4 — the runtime keeps being rebuilt | CMS→G1(9)→ZGC(15)→gen ZGC(23)/gen Shenandoah(24); threads→pools(1.5)→virtual(21) |
| Pivot of the whole timeline | 1.5 — concurrency, and the memory model it did *not* define |
| Pivot of the modern timeline | 21 — virtual threads plus the Loom consolidation |

## JEP quick index

| Q | A |
|---|---|
| JEP 248 / 252 / 261 / 254 | G1 default GC (9) / CLDR locales (9) / Module System (9) / Compact Strings (9) |
| JEP 286 / 323 / 321 | `var` locals (10) / `var` lambda params (11) / HTTP Client (11) |
| JEP 325 / 361 / 378 | Switch expressions preview (12) / final (14) / Text Blocks (15) |
| JEP 336 / 363 / 367 / 372 | Pack200 deprecated (13) / remove CMS (14) / remove Pack200 (14) / remove Nashorn (15) |
| JEP 359 / 384 / 395 | Records preview (14) / 2nd preview (15) / final (16) |
| JEP 360 / 397 / 409 | Sealed preview (15) / 2nd preview (16) / final (17) |
| JEP 400 / 403 / 411 / 486 | UTF-8 by Default (18) / Strongly Encapsulate JDK Internals (17) / SecurityManager deprecated (17) / permanently disabled (24) |
| JEP 425 / 436 / 444 | Virtual threads preview (19) / 2nd preview (20) / final (21) |
| JEP 405 / 432 / 440 | Record patterns preview (19) / 2nd preview (20) / final (21) |
| JEP 406 / 427 / 433 / 441 | Switch patterns preview (17) / 3rd (19) / 4th (20) / final (21) |
| JEP 430 / 459 / 465 | String templates preview (21) / 2nd (23) / withdrawn (24) |
| JEP 439 / 474 / 404 / 521 | Generational ZGC (21) / gen ZGC default (23) / gen Shenandoah experimental (24) / default (25) |
| JEP 456 / 485 / 484 / 491 | Unnamed patterns (22) / gatherers (24) / Class-File API (24) / VT pinning fixed (24) |
| JEP 506 / 511 / 512 / 513 / 519 | Scoped Values (25) / module import (25) / compact source (25) / flex constructors (25) / compact headers (25) |
| Canonical index / compat rules | <https://openjdk.org/jeps/0> · JLS 13.5 |