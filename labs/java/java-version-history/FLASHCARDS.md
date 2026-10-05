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
| G1 default GC (JEP 158) / CLDR locales (JEP 252) | Both 9 — the latter a silent formatting change |
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
| `switch` expressions preview (JEP 325) | 12 |
| Text blocks preview | 13 and 14 |
| `switch` expressions standard, `yield` | 13/14 (JEP 361, final 14) |
| `Files.mismatch`, `CharBuffer` | 13 |
| Friction point | Exhaustive switch over `enum` with no `default` — a real problem for libraries |

## 14 — The garbage collector purges (2020)

| Q | A |
|---|---|
| Text blocks standard | 15 (preview 13/14) |
| CMS collector **removed** (JEP 367) | 14 — deprecated in 8 |
| Pack200 **removed** | 14 — deprecated 13; replaced by `jlink` |
| Nashorn deprecated (JEP 372) | 14 — removed in 15 |
| Principle | Removal for *simplification*, not capability |

## 15 — The preview year (2020, LTS)

| Q | A |
|---|---|
| Records preview (2nd), sealed preview (JEP 360), switch-pattern preview (JEP 406) | 15 |
| ZGC production-ready (JEP 379) | 15 — experimental in 11 |
| Why preview features exist | The 6-month cadence made "too much new surface per release" a real risk |
| Preview benefit vs cost | Designs refined *substantially* while gated; code is not portable across releases |

## 16 — Records and sealed types (2021, LTS)

| Q | A |
|---|---|
| Records standard (JEP 395); `instanceof` pattern matching standard (JEP 305) | 16 |
| `Stream.toList()` | 16 |
| Records are | **Shallowly** immutable — a `List` component is still mutable |
| Sealed still preview in 16 | Yes — preview 15 *and* 16, standard 17 |

## 17 — Sealed + encapsulation lands (2021, LTS)

| Q | A |
|---|---|
| Sealed classes standard (JEP 409); switch patterns standard (JEP 406) | 17 |
| Strong encapsulation of JDK internals (JEP 403) | 17 — `--illegal-access` becomes a no-op |
| Symptom of JEP 403 | `java.lang.reflect.InaccessibleObjectException` from `setAccessible` |
| `permits` commitment / cost | Adding a subtype is source-breaking everywhere; the largest migration pain since 9 |

## 18 — UTF-8 by default (2022, LTS)

| Q | A |
|---|---|
| UTF-8 as the default charset (JEP 400) | 18 — escape hatch `-Dfile.encoding=COMPAT` |
| `SimpleWebServer` | 18 |
| Why it mattered | The default charset was OS-locale-dependent — platform-dependent behaviour |
| The most under-appreciated migration risk | Yes — silent data corruption, no exception |
| Virtual threads **preview** (JEP 425) | 18 — *first* preview, not 19 |

## 19 — Records in switch, virtual threads preview (2022)

| Q | A |
|---|---|
| Virtual threads preview (2nd, JEP 436) | 19 |
| Record patterns preview (JEP 405); `java.lang.foreign` preview (JEP 424) | 19 |
| Structured concurrency preview (JEP 428) | 19 |
| Switch patterns standard (JEP 441) | 19 |
| Pressure on platform threads | ~1 MB stack each, OS-thread-bound → high-concurrency IO was uneconomic |

## 20 — Pattern matching everywhere (2023)

| Q | A |
|---|---|
| Record patterns standard (JEP 440); virtual threads standard (JEP 444) | 20 |
| Structured concurrency preview (2nd), ScopedValue preview (JEP 446), sequenced collections preview | 20 |
| Why 20 mattered | It delivered the third and final piece of pattern matching |
| The trade-off | Exhaustive switch is compiler-checked, so adding a subtype is a compile break everywhere |

## 21 — The LTS consolidation release (2023, LTS)

| Q | A |
|---|---|
| Virtual threads mainstream; `Thread.ofVirtual()` builders (JEP 451) | 21 — the modern-concurrency baseline |
| Generational ZGC (JEP 448); sequenced collections preview; string templates preview (JEP 430) | 21 |
| `StructuredTaskScope` preview (2nd) — **still preview** | 21 |
| Sizing guidance inverted | One virtual thread per task; a fixed pool is now an anti-pattern |
| Why existing pool code is dangerous | It kept compiling and silently stopped being the right shape |

## 22 — Unnamed patterns and variables (2023)

| Q | A |
|---|---|
| Unnamed variables and patterns `_` (JEP 456) | 22 |
| Implicitly declared classes / instance main (preview) | 22 — the second program form with no `public class` |
| `ClassFile` API (JEP 484) final 24; FFM API incubating (JEP 447) | 22 |

## 23 — ZGC generational, string templates (2023)

| Q | A |
|---|---|
| Generational ZGC (JEP 474) | 23 — brought G1-class pause behaviour to large heaps |
| String templates (2nd preview, JEP 459) | 23 — **withdrawn** after API criticism |
| Finalizers deprecated for removal (JEP 421) | 23 |

## 24 — Generational Shenandoah (2024, LTS)

| Q | A |
|---|---|
| Generational Shenandoah (JEP 521) | 24 |
| SecurityManager terminally deprecated (JEP 486) | 24 — finally at its documented end state |
| `Stream` gatherers (JEP 485) | 24 — the sanctioned extension point, replacing `Collector` |
| Flexible constructor bodies preview (JEP 492); `ClassFile` API final | 24 |

## 25 — The current frontier (2025, LTS)

| Q | A |
|---|---|
| Compact object headers (JEP 519) | 25 — saves up to 16 bytes per object |
| `import module java.base` (module import declarations) | 25 — the ergonomic counterweight to JPMS |
| Flexible constructor bodies standard (JEP 513); ScopedValue standard (JEP 506) | 25 |
| StructuredTaskScope preview (2nd); `java.lang.foreign` preview; Vector API incubation | 25 |
| Generational Shenandoah + generational ZGC defaults | 25 |
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
| JEP 158 / 252 / 261 / 277 | G1 default GC / CLDR locales / Module System / enhanced try-with-resources — all 9 |
| JEP 286 / 323 | `var` for locals (10); `var` in lambda params (11) |
| JEP 354 / 367 / 372 / 379 | Pack200 deprecated (13) / remove CMS (14) / Nashorn removed (15) / ZGC prod (15) |
| JEP 395 / 400 / 403 / 405 / 409 | Records (16) / UTF-8 (18) / strong encapsulation (17) / record patterns preview (19) / sealed final (17) |
| JEP 425 / 436 / 444 | Virtual threads preview 18, preview 19, final 20 |
| JEP 441 / 448 / 451 / 474 | Switch patterns (19) / gen ZGC (21) / virtual-thread executors (21) / gen ZGC (23) |
| JEP 430 | String templates — preview 21–24, **withdrawn** |
| JEP 456 / 485 / 486 / 521 | Unnamed patterns (22) / gatherers (24) / SecurityManager off (24) / gen Shenandoah (24) |
| JEP 519 | Compact object headers (25) |
| Canonical index / compat rules | <https://openjdk.org/jeps/0> · JLS 13.5 |