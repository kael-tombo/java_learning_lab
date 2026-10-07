# FLASHCARDS — Java Version History

One row per feature attribution or design decision. Sections follow THEORY.md.
Every release and stage below was checked against the JEP's own page on
openjdk.org (Release and Title fields) or Oracle's Java SE Support Roadmap, fetched
October 2026. Pre-9 rows cite the JSR that defined the feature, since there is no
JEP index before JDK 8. Miss a row, reread that section.

LTS releases are **8, 11, 17, 21, 25** only (Oracle roadmap). Every other number is
a six-month non-LTS release.

## 1.2 — "Java 2" (December 1998)

| Q | A |
|---|---|
| Collections Framework (`List`/`Set`/`Map`), `Iterator` replacing `Enumeration` | 1.2 |
| Swing, `strictfp`, JDBC 2.0 | 1.2 |
| "Java 2" branding | 1.2 — the J2SE / J2EE / J2ME split |
| Why generics were needed | Collections arrived *before* generics, so every element needed a cast |

## 1.4 — Assertions, regex, NIO, logging (February 2002)

| Q | A |
|---|---|
| `assert` keyword | **1.4** — not 1.2 |
| `java.util.logging`, `java.util.regex`, `java.nio` | 1.4 |
| Chained exceptions (`Throwable.getCause`) | 1.4 |
| Is `java.util.logging` the *only* JDK logging API? | No — `System.Logger` (JEP 264, JDK 9) is a facade over the configured backend |
| Is `StringBuffer` deprecated? | **No.** `StringBuilder` (5) is the unsynchronised alternative; `StringBuffer` remains |

## 5 (also "1.5") — The generics release (September 2004)

| Q | A |
|---|---|
| Java 5 vs Java 1.5 | The **same release**; renumbered at launch |
| Generics (JSR 14), enums, autoboxing, varargs, enhanced `for`, static imports | 5 (JSR 201 for the language features) |
| Annotations | 5 (JSR 175) |
| `StringBuilder` | 5 |
| `StringJoiner` | **8** — not 5 |
| `java.util.concurrent` (thread pools, `ConcurrentHashMap`, `Semaphore`, `BlockingQueue`, `ScheduledExecutorService`, atomics, locks) | 5 (JSR 166) — not 6 |
| The rewritten Java Memory Model | 5 (JSR 133) |
| Why no `new T[]`, no `instanceof List<String>`, no overload on generic type | Erasure — the type argument is not reifiable; use `instanceof List<?>` |

## 6 — Scripting and performance (December 2006)

| Q | A |
|---|---|
| Scripting API (JSR 223), compiler API, JDBC 4.0, `SwingWorker` | 6 |
| `Deque`/`ArrayDeque`, `NavigableMap`, `ConcurrentSkipListMap` | 6 |
| `@Override` on a method implementing an *interface* | 6 — Java 5 allowed it only for superclass overrides |

## 7 — Project Coin and `invokedynamic` (July 2011)

| Q | A |
|---|---|
| `try`-with-resources, diamond `<>`, strings in `switch`, multi-catch, `1_000_000` and binary literals | 7 (Project Coin, JSR 334) |
| NIO.2 (`java.nio.file`), Fork/Join, `java.util.Objects` | 7 |
| `invokedynamic` bytecode | 7 (JSR 292) — the mechanism lambdas are later compiled against |
| Diamond's weakness | Could not infer from a method-argument target type until 8 (JEP 101) |

## 8 — The lambda release (March 2014, LTS)

| Q | A |
|---|---|
| Lambdas and method references | 8 (JEP 126), via `invokedynamic`, not anonymous classes |
| Default and static interface methods | 8 — let interfaces grow without breaking implementors |
| `Stream` API, `Optional`, `CompletableFuture` | 8 |
| `java.time` | 8 (JEP 150) |
| Repeatable annotations / type annotations | 8 (JEP 120 / JEP 104) |
| HashMap collision handling with balanced trees | 8 (JEP 180) |
| `Optional`'s intended use | Method **return types only** — a contract the ecosystem never honoured |
| Diamond problem with defaults | A class inheriting the same default from two interfaces must override it |

## 9 — The module release (September 2017)

| Q | A |
|---|---|
| Module system | 9 (JSR 376, JEP 261) |
| `jlink` / `jshell` | 9 (JEP 282 / JEP 222) |
| G1 becomes the default collector | 9 (JEP 248) — a silent behaviour change |
| CLDR becomes the default locale data | 9 (JEP 252) — a silent formatting change |
| Compact strings | 9 (JEP 254) |
| `List.of` / `Set.of` / `Map.of` | 9 (JEP 269) |
| Stack-Walking API / `Flow` API | 9 (JEP 259 / JEP 266) |
| Milling Project Coin (private interface methods, diamond with anonymous classes, effectively-final try-with-resources) | 9 (JEP 213) |
| CMS collector deprecated | 9 (JEP 291) |
| Applet API deprecated | 9 (**JEP 289** — this is *not* VarHandle) |
| `var` | **10**, not 9 |
| Why JPMS adoption was slow | `split package` restrictions broke much of the ecosystem; weak migration story |

## 10 — Local-variable type inference (March 2018)

| Q | A |
|---|---|
| `var` for local variables | 10 (JEP 286) — locals only, not fields/parameters/returns |
| Parallel full GC for G1 | 10 (JEP 307) — still present, never removed |
| `javah` removed | 10 (JEP 313) → `javac -h` |
| Time-based release versioning | 10 (JEP 322) — the six-month cadence |
| `List.copyOf`, `Collectors.toUnmodifiableList` | 10 |
| `var` in lambda parameters | 11, not 10 (JEP 323) |

## 11 — HTTP client and the Java EE removal (September 2018, LTS)

| Q | A |
|---|---|
| `java.net.http.HttpClient` | 11 (JEP 321) |
| `var` in lambda parameters | 11 (JEP 323) |
| `java Hello.java` single-file launch | 11 (JEP 330) |
| Flight Recorder in the JDK | 11 (JEP 328) |
| TLS 1.3 | 11 (JEP 332) |
| ZGC (experimental) | 11 (JEP 333) |
| Java EE and CORBA modules **removed** | 11 (JEP 320) — the JAXB/JAX-WS break |
| Nashorn / Pack200 **deprecated** | 11 (JEP 335 / JEP 336) |
| `String.strip`/`repeat`/`lines`/`isBlank`, `Files.readString`, `Optional.isEmpty` | 11 |

## 12–13 — First previews (2019)

| Q | A |
|---|---|
| Switch expressions (preview) | 12 (JEP 325); second preview 13 (JEP 354); **final 14** (JEP 361) |
| Text blocks (preview) | 13 (JEP 355); second preview 14 (JEP 368); **final 15** (JEP 378) |
| Shenandoah (experimental) | 12 (JEP 189); production 15 (JEP 379) |
| Abortable mixed collections for G1 / default CDS archives | 12 (JEP 344 / JEP 341) |
| ZGC uncommits unused memory | 13 (JEP 351, experimental) |

## 14 — The GC purge (March 2020)

| Q | A |
|---|---|
| Switch expressions final | 14 (JEP 361) |
| Records first preview | 14 (JEP 359) |
| `instanceof` pattern matching first preview | 14 (JEP 305) |
| Helpful NullPointerExceptions | 14 (JEP 358) |
| JFR event streaming | 14 (JEP 349) |
| CMS **removed** | 14 (JEP 363); deprecated 9 (JEP 291) |
| Pack200 **removed** | 14 (JEP 367); deprecated 11 (JEP 336) |
| ParallelScavenge + SerialOld combination | Deprecated 14 (JEP 366) |
| ZGC on macOS / Windows | 14 (JEP 364 / JEP 365), experimental |
| Principle | Removal for *simplification*, not capability |

## 15 — Production GCs, text blocks (September 2020)

| Q | A |
|---|---|
| Text blocks final | 15 (JEP 378) |
| ZGC production / Shenandoah production | 15 (JEP 377 / JEP 379) — two different JEPs |
| Records second preview | 15 (JEP 384) |
| Sealed classes first preview | 15 (JEP 360) |
| `instanceof` pattern matching second preview | 15 (JEP 375) |
| Nashorn **removed** | 15 (JEP 372); deprecated 11 (JEP 335) |
| Biased locking deprecated and disabled by default | 15 (JEP 374) |
| Hidden classes | 15 (JEP 371) — also deprecates `Unsafe.defineAnonymousClass` |

## 16 — Records final (March 2021)

| Q | A |
|---|---|
| Records final | 16 (JEP 395) |
| `instanceof` pattern matching final | 16 (JEP 394) |
| Sealed classes second preview | 16 (JEP 397) — **not final until 17** |
| Strong encapsulation by default (`--illegal-access=deny`) | 16 (JEP 396) |
| `Stream.toList()` | 16 |
| Records are | **Shallowly** immutable — a `List` component is still mutable |

## 17 — Sealed and encapsulated (September 2021, LTS)

| Q | A |
|---|---|
| Sealed classes final | 17 (JEP 409) |
| Strongly encapsulate JDK internals | 17 (JEP 403) — `--illegal-access` ignored; the largest migration break since 9 |
| SecurityManager deprecated for removal | 17 (JEP 411) |
| `RandomGenerator` | 17 (JEP 356) |
| Pattern matching for `switch` | **First preview** 17 (JEP 406) — final is **21** |
| Experimental AOT and JIT compiler removed | 17 (JEP 410) |
| `Unsafe.defineAnonymousClass` | **Removed 17** (Oracle JDK 17 release notes); deprecated 15; use `Lookup::defineHiddenClass` |

## 18 — UTF-8 by default (March 2022)

| Q | A |
|---|---|
| UTF-8 as the default charset | 18 (JEP 400) — escape hatch `-Dfile.encoding=COMPAT` |
| Why it mattered | The default was OS-locale-dependent; silent data corruption on upgrade |
| Simple Web Server | 18 (JEP 408) |
| Internet-Address Resolution SPI | 18 (JEP 418) |
| Core reflection on method handles | 18 (JEP 416) |
| Finalization deprecated for removal | **18** (JEP 421) — not 23 |
| Code snippets in Javadoc | 18 (JEP 413) |
| `switch` patterns second preview | 18 (JEP 420) |
| Is 18 an LTS? | **No** |

## 19 — Previews (September 2022)

| Q | A |
|---|---|
| Virtual threads first preview | 19 (JEP 425) |
| Record patterns first preview | 19 (JEP 405) |
| `switch` patterns third preview | 19 (JEP 427) |
| FFM API first preview | 19 (JEP 424) |
| Structured concurrency | **Incubator** 19 (JEP 428) — a weaker gate than preview |

## 20 — The last preview round (March 2023)

| Q | A |
|---|---|
| Virtual threads second preview | 20 (JEP 436) |
| Record patterns second preview | 20 (JEP 432) |
| `switch` patterns fourth preview | 20 (JEP 433) |
| FFM API second preview | 20 (JEP 434) |
| Scoped Values incubator | 20 (JEP 429) |
| Structured concurrency | **Second incubator** 20 (JEP 437) — not a preview |
| Why 20 mattered | It was the last preview round; nothing headline was *final* until 21 |

## 21 — The LTS consolidation (September 2023, LTS)

| Q | A |
|---|---|
| Virtual threads final | 21 (JEP 444) |
| `switch` patterns final / record patterns final | 21 (JEP 441 / JEP 440) |
| Sequenced collections | 21 (JEP 431) |
| Generational ZGC (flag-enabled) | 21 (JEP 439); default in 23 (JEP 474) |
| String templates first preview | 21 (JEP 430) |
| Structured concurrency first **preview** | 21 (JEP 453) |
| Scoped Values first preview | 21 (JEP 446) |
| Unnamed patterns/variables preview; unnamed classes + instance `main` preview | 21 (JEP 443; JEP 445) |
| Dynamic agent loading — prepare to disallow | 21 (JEP 451) |
| Sizing guidance inverted | One virtual thread per task; a fixed pool is now an anti-pattern |

## 22 — Unnamed variables, FFM final (March 2024)

| Q | A |
|---|---|
| Unnamed variables and patterns final | 22 (JEP 456) |
| FFM API final | 22 (JEP 454) |
| Multi-file source launch | 22 (JEP 458) |
| Flexible constructor bodies first preview ("Statements before `super`") | 22 (JEP 447) |
| Structured concurrency second preview | 22 (JEP 462) |
| Scoped Values second preview | 22 (JEP 464) |
| Stream Gatherers first preview | 22 (JEP 461) |
| Class-File API first preview | 22 (JEP 457) |
| String templates second preview | 22 (JEP 459) |

## 23 — Generational ZGC by default (September 2024)

| Q | A |
|---|---|
| Generational ZGC becomes the default | 23 (JEP 474) |
| Markdown documentation comments | 23 (JEP 467) |
| `Unsafe` memory-access methods terminally deprecated | 23 (JEP 471) |
| Structured concurrency third preview | 23 (JEP 480) |
| Scoped Values third preview / flexible constructors second preview | 23 (JEP 481 / JEP 482) |
| Module import declarations first preview | 23 (JEP 476) |
| Primitive types in patterns first preview | 23 (JEP 455) |
| String templates | **Absent from 23** — JEP 465 was withdrawn; the feature never became final |

## 24 — Security and cleanup (March 2025, non-LTS)

| Q | A |
|---|---|
| SecurityManager permanently disabled | 24 (JEP 486) — deprecated 17 (JEP 411), disabled by default 18 |
| Stream Gatherers final | 24 (JEP 485) |
| Class-File API final | 24 (JEP 484) |
| AOT class loading and linking | 24 (JEP 483) |
| `synchronized` no longer pins virtual threads | 24 (JEP 491) |
| Generational Shenandoah (experimental) | 24 (JEP 404); product in 25 (JEP 521) |
| Compact object headers (experimental) | 24 (JEP 450); product in 25 (JEP 519) |
| ZGC non-generational mode removed | 24 (JEP 490) |
| `Unsafe` memory-access run-time warning | 24 (JEP 498) — a *warning*, not a removal |
| 32-bit x86 | Windows port removed 24 (JEP 479); Linux port deprecated 24 (JEP 501), removed 25 (JEP 503) |
| Structured concurrency fourth preview | 24 (JEP 499) |
| Is 24 an LTS? | **No** |

## 25 — The current LTS (September 2025, LTS)

| Q | A |
|---|---|
| Compact object headers (product feature) | 25 (JEP 519) — header 12–16 B → 8 B, so **4–8 B saved per object**; **opt-in** in 25 |
| Module import declarations final | 25 (JEP 511) — `import module java.base` |
| Scoped Values final | 25 (JEP 506) |
| Flexible constructor bodies final | 25 (JEP 513) |
| Compact source files and instance `main` final | 25 (JEP 512) — four preview rounds: 445 (21), 463 (22), 477 (23), 495 (24) |
| Generational Shenandoah (product) | 25 (JEP 521) |
| AOT method profiling / command-line ergonomics | 25 (JEP 515 / JEP 514) |
| Structured concurrency | **Still preview** — fifth preview in 25 (JEP 505) |
| Primitive types in patterns | Third preview 25 (JEP 507) |
| PEM encodings | First preview 25 (JEP 470) |
| Pressure 1 | Memory density — object headers were a fixed cost since 1.0 |
| Pressure 2 | Migration friction — `import module` attacks what stalled JPMS (8 years after 9) |
| Pressure 3 | Concurrency completion — Scoped Values final; structured concurrency not yet |
| Cost of compact headers | Heap dumps, memory accounting and layout assumptions must be revalidated |

## After 25 (26 and 27 are non-LTS; next LTS is 29)

| Q | A |
|---|---|
| HTTP/3 for the HTTP Client | **26** (JEP 517) — not 25 |
| Applet API removed | 26 (JEP 504); deprecated 9 (JEP 289) |
| Structured concurrency | Sixth preview 26 (JEP 525), seventh preview 27 (JEP 533) |
| Compact object headers become the default | 27 (JEP 534) |
| G1 the default collector in all environments | 27 (JEP 523) |
| Why 25 → 27 is a *defaults* migration | Heap layout and collector choice change with no flag; re-baseline memory and pauses |

## Common misattributions (each of these has actually been made)

| Wrong | Right |
|---|---|
| `assert` is a 1.2 feature | 1.4 |
| `StringBuffer` is deprecated | It is not |
| `StringJoiner` is Java 5 | Java 8 |
| `@Override` on interface methods is Java 5 | Java 6 |
| `java.util.concurrent` is Java 6 | Java 5 |
| `var` shipped in 9 | 10 (JEP 286) |
| `var` in lambda parameters is 10 | 11 (JEP 323) |
| Switch expressions are final in 13 | Final in 14 (JEP 361) |
| Text blocks are a 13 feature | Final in 15 (JEP 378) |
| `instanceof` patterns are final in 13 or 15 | Final in 16 (JEP 394) |
| Sealed classes are final in 16 | Final in 17 (JEP 409) |
| `switch` patterns are final in 17, 19 or 20 | Final in 21 (JEP 441) |
| Virtual threads are final in 19 or 20 | Final in 21 (JEP 444) |
| Structured concurrency is "preview 20" or final | Incubator 19–20, preview 21 onward, **still preview** |
| String templates shipped, previewed 21–24, or were finalised | Previewed 21 and 22, then **withdrawn** (JEP 465) |
| Finalization was deprecated in 23 | 18 (JEP 421) |
| CMS was deprecated in 8 | 9 (JEP 291) |
| Pack200 was deprecated in 13 | 11 (JEP 336) |
| Nashorn was deprecated in 14 or removed in 14 | Deprecated 11 (JEP 335), removed 15 (JEP 372) |
| JEP 289 is VarHandle | JEP 193 is VarHandle; 289 is "Deprecate the Applet API" |
| JEP 379 is ZGC production | 377 is ZGC; 379 is Shenandoah |
| `defineAnonymousClass` was removed in 24 | Removed in **17** |
| `Unsafe` memory-access methods were disabled in 24 | A run-time *warning* in 24 (JEP 498) |
| Compact headers save 16 B/object | 4–8 B/object |
| Compact headers are default in 25 | Opt-in in 25; default in 27 (JEP 534) |
| HTTP/3 shipped in 25 | 26 |
| 16, 18 or 24 is an LTS | LTS is 8, 11, 17, 21, 25 only |

## Cross-cutting: the four patterns

| Q | A |
|---|---|
| Pattern 1 — boilerplate elimination follows widespread pain | Generics (5), try-with-resources (7), lambdas (8), records (16) |
| Pattern 2 — preview became the release valve | Since 12; 1–4 rounds; also a way to *stop* a design (string templates) |
| Pattern 3 — API evolution mechanisms are features | Default methods (8), modules (9), preview (12+), compact headers (25) |
| Pattern 4 — the runtime keeps being rebuilt | CMS→G1 (9)→ZGC (15)→gen ZGC (21/23)→gen Shenandoah (24/25); threads→pools (5)→virtual (21) |
| Pivot of the whole timeline | 5 — generics, concurrency and the memory model together |
| Pivot of the modern timeline | 21 — virtual threads plus the pattern-matching consolidation |

## JEP quick index

| Q | A |
|---|---|
| JEP 193 / 213 / 222 / 248 / 252 / 254 / 261 | VarHandle / Milling Coin / jshell / G1 default / CLDR / compact strings / modules — all 9 |
| JEP 286 / 307 / 313 / 322 | `var` / parallel G1 full GC / `javah` removed / time-based versioning — all 10 |
| JEP 320 / 321 / 323 / 330 / 332 / 333 | Java EE removed / HTTP client / `var` lambda / single-file / TLS 1.3 / ZGC experimental — all 11 |
| JEP 335 / 336 | Nashorn / Pack200 deprecated (11) |
| JEP 325 / 354 / 361 | Switch expressions: preview 12 / second preview 13 / final 14 |
| JEP 355 / 368 / 378 | Text blocks: preview 13 / second preview 14 / final 15 |
| JEP 359 / 384 / 395 | Records: preview 14 / second 15 / final 16 |
| JEP 305 / 375 / 394 | `instanceof` patterns: preview 14 / second 15 / final 16 |
| JEP 360 / 397 / 409 | Sealed: preview 15 / second 16 / final 17 |
| JEP 406 / 420 / 427 / 433 / 441 | `switch` patterns: previews 17, 18, 19, 20 / final 21 |
| JEP 405 / 432 / 440 | Record patterns: previews 19, 20 / final 21 |
| JEP 425 / 436 / 444 | Virtual threads: previews 19, 20 / final 21 |
| JEP 428 / 437 / 453 | Structured concurrency: incubators 19, 20 / first preview 21 |
| JEP 462 / 480 / 499 / 505 / 525 / 533 | Structured concurrency previews 22, 23, 24, 25, 26, 27 |
| JEP 363 / 367 / 372 | CMS removed / Pack200 removed (14) / Nashorn removed (15) |
| JEP 377 / 379 | ZGC / Shenandoah production (15) |
| JEP 396 / 403 / 411 / 486 | Strong encapsulation default 16 / enforced 17 / SecurityManager deprecated 17 / disabled 24 |
| JEP 400 / 416 / 421 | UTF-8 / reflection on method handles / finalization deprecated — all 18 |
| JEP 430 / 459 / 465 | String templates: preview 21 / second preview 22 / **withdrawn** |
| JEP 439 / 474 / 404 / 521 | Gen ZGC (21) / default (23) / gen Shenandoah experimental (24) / product (25) |
| JEP 450 / 519 / 534 | Compact headers: experimental 24 / product 25 / default 27 |
| JEP 471 / 498 / 454 | `Unsafe` memory methods: deprecated 23 / warn 24 / FFM replacement final 22 |
| JEP 456 / 485 / 484 / 491 | Unnamed vars (22) / gatherers (24) / Class-File API (24) / no pinning (24) |
| JEP 506 / 511 / 512 / 513 | Scoped Values / module import / instance `main` / flexible constructors — all final in 25 |
| JEP 504 / 517 / 523 | Applet removed 26 / HTTP/3 26 / G1 default everywhere 27 |
| Canonical index | <https://openjdk.org/jeps/0> · Oracle roadmap: <https://www.oracle.com/java/technologies/java-se-support-roadmap.html> |