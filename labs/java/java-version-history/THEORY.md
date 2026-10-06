# THEORY — Java Features from 1.2 to 25

Each section: **what shipped**, **the pressure that produced it**, and
**what it cost**.

---

## 1.2 — The Professional Release (1999)

**Shipped**: `StringBuffer` (the `String` sibling — the first time the API
admitted that string building matters), JDBC 2.0 core, `assert` keyword,
collections framework (`List`, `Map`, `Set`), iterators replacing `Enumeration`.

**Pressure**: Java 1.0's credibility. The "applets are slow" narrative needed
a credible client-server story. The collections framework was the first mature
reusable data-structures package shipped with the platform.

**Cost**: `StringBuffer` was `String`'s mutable twin — a naming and API-design
wart the platform could not remove for a decade. It is deprecated in favour of
`StringBuilder` since Java 9.

---

## 1.4 — Assertions, Logging, XML (2002)

**Shipped**: `assert` keyword, `java.util.logging`, the XML parser core,
`ChainedRuntimeException`.

**Pressure**: production debugging without `System.out.println`. Logging was
Java's admission that it lacked observability tooling.

**Cost**: `java.util.logging` is functionally weak and long-superseded by
Log4j/SLF4J — but it is still the *only* logging API in the JDK, which still
causes classpath conflicts.

---

## 1.5 — Concurrency (2004)

**Shipped**: `java.util.concurrent` — thread pools, `ConcurrentHashMap`,
`CountDownLatch`, `Semaphore`, `CyclicBarrier`, atomics (`j.u.c.atomic`), and
`java.util.concurrent.locks`.

**Pressure**: This is the pivotal version. Java's single-threaded-per-request
model could not scale to servers, and the "Java is slow" critique was really
"Java's threading is unsafe and verbose."

**Cost**: The API was famously hard to learn — five different locking mechanisms
at once. The **memory model** that makes it correct was not *defined* until
Java 5's fix, and was not *documented coherently* until the JSR 133 rewrite in
2004 (JDK 5). Sixteen years of subtle concurrency bugs came from this gap.

---

## 5 — Generics (2004)

**Shipped**: type parameters, erasure, `@Override` on interface implementations,
`enum`, autoboxing, varargs, `StringBuilder`/`StringJoiner`, `Iterable`/
`for-each`, `java.util.concurrent` improvements, static imports.

**Pressure**: collections had no compile-time type safety, forcing casts
everywhere. `enum` came because `static final int` constants could not be
switched on without subclassing.

**Cost of erasure**: no reified generics (`List<String>` is not reifiable), so
you cannot overload on generic type, cannot `new T[]`, and cannot do
`instanceof List<String>`. This remains the single most-argued design decision
in the language, and the reason `List<?>` exists.

---

## 6 — Concurrency, finished (2006)

**Shipped**: `java.util.concurrent` blocking queues, `ConcurrentNavigableMap`,
`ExecutorService` ergonomics, de/serialization APIs (`java.io.Serializable`
cleanup), Swing `Worker` thread.

**Pressure**: the 1.5 concurrency API was incomplete — no good blocking queue,
no concurrent set, no `ScheduledExecutorService` semantics you could trust.

---

## 7 — The "Project Coin" (2011)

**Shipped**: `try`-with-resources, diamond operator `<>`, strings in `switch`,
multi-catch, binary literals and underscores (`1_000_000`), JDBC 4, `Objects`
utility, `Files`/`Path` NIO 2 addition.

**Pressure**: exactly 25 small changes, voted on by the community — the JSR that
proved the process could ship ergonomics without a big-bang risk.

**Cost**: minor. Diamond inference was too weak (it cannot infer from the
target type in a method argument until 8).

---

## 8 — Lambda era (2014)

**Shipped**: **lambdas**, method references, functional interfaces
(`@FunctionalInterface`), default and static interface methods, `Stream` API,
`Optional`, `java.time`, repeatable annotations, type annotations, `CompletableFuture`.

**Pressure**: two forces at once. First, functional programming had won the
industry argument (map/reduce, immutability). Second, the collection framework
was fundamentally sequential — every parallel computation was hand-rolled and
wrong. Plus the *pragmatic* pressure: interfaces could not grow without
breaking every implementor, which blocked API evolution throughout the JDK.

**Costs, both still felt today**:
- `Optional` was **contested**. Oracle engineers stated it was intended for
  *method return types only*, a position that has never fully been honoured and
  which produced a decade of debate and a `Optional` field anti-pattern.
- **Default methods created a diamond problem**: if two interfaces provide the
  same default, the class *must* override it. `Collection.toArray(IntFunction)`
  is an example of API evolution paying a lasting tax.

---

## 9 — Modularity + collection APIs (2017)

**Shipped**: **module system** (Jigsaw, JSR 376), `var` (as a *restricted type
inference*, not a general type), interface private methods, diamond with
anonymous classes, collection factory methods (`List.of`), `try`-with-resources
effectively final, StackFlow API, jlink.

**Pressure**: the classpath made encapsulation impossible ("the compile-time
dependency graph is the module graph, and everything is public"), and building
a minimal custom runtime image was impossible.

**Cost**: the module system's adoption has been the slowest of any major Java
feature by a wide margin, because `split package` restrictions broke much of the
older ecosystem and the migration story was poor. This is why `--illegal-access`
then `--add-opens` remained necessary for years afterwards.

`var` is the notable *narrowing*: it only infers local variables, never fields,
parameters, or returns. This is deliberate — the restriction is what keeps `var`
from harming readability.

---

## 10 — Local type inference (2018)

**Shipped**: `var` for local variables (JEP 286) — *un*restricted in for-loop
headers and try-with-resources, plus switch improvements (arrow syntax), and
`Collectors.toUnmodifiableList`.

**Pressure**: diamond did not work on anonymous classes, and the ceremony of
naming generic types in lambdas was severe. The 9 → 10 split was explicitly a
"rejection feedback" iteration.

**Cost**: mild but real. `var` on a lambda parameter is a syntax error, and
`var` erases the documentation value of an explicit type. The Java team's own
guidance is to use it when the type is already evident from the right-hand side.

---

## 11 — HTTP client, var in lambda params (2018, LTS)

**Shipped**: `java.net.http.HttpClient`, `var` in lambda parameters, string
methods (`strip`, `repeat`, `lines`, `isBlank`), `Files.readString`/`writeString`,
`Optional.isEmpty()`, `List.copyOf`/`Map.copyOf`, ZGC experimental, single-file
source execution (`java Hello.java`).

**Pressure**: the JDK's `HttpURLConnection` was long-obsolete, and the "run a
Java file without compiling" story was a perennial developer-experience
complaint.

---

## 12–13 — Switch expressions, text blocks (2019)

**Shipped** (12 LTS): Switch Expressions (preview, JEP 325 — the expression
form was not final here), `G1` improvements (JEP 344, abortable mixed
collections), `Switch` arrow syntax, default CDS archives (JEP 341).
**Shipped** (13): text blocks **preview** (JEP 355), switch expressions second
preview (JEP 354), `Files.mismatch`, `CharBuffer`.

**Correction worth recording**: switch expressions went final in **14**
(JEP 361), not 13 — and `instanceof` pattern matching went final in **16**
(JEP 394), not 13. Text blocks went final in **15** (JEP 378). Conflating this
12–15 cluster is one of the most common version-attribution errors, because
text blocks are remembered as "a 13 feature" from their preview.

**Pressure**: switch statements had been a known readability disaster since
Java 1.0. Multi-line strings were impossible before 15 — every JSON payload or
SQL query was string-concatenated.

**Cost**: switch expressions over `enum` require exhaustive coverage, which is
why the compiler demanding either a `default` or all cases covered generated
friction in library authors' code.

---

## 14 — The garbage collector purges (2020)

**Shipped**: **CMS collector removed** (JEP 363), **Pack200 tools and API removed**
(JEP 367), `switch` expressions with `yield` (JEP 354 second preview), records
**first preview** (JEP 359), pattern matching `instanceof` **second preview**
(JEP 375), pattern matching for `switch` **first preview** (JEP 406), and the
deprecation of the ParallelScavenge + SerialOld combination (JEP 366).

**Correction worth recording**: text blocks and Nashorn's removal are **15**
(JEP 378 and JEP 372), not 14 — and Nashorn's *deprecation* was 11 (JEP 335).
Common conflations here put text blocks in 13 or 14 and Nashorn's removal in 14;
both are off by one release.

**Pressure**: GC history. CMS was deprecated in 8 (JEP 291) and removed in 14;
the platform consolidated onto G1 (default since 9, JEP 248) and ZGC (production
15, JEP 377). This is the clearest case in Java history of *removal for
simplification* rather than capability.

**Cost**: teams still pinned to CMS in 2020 had to move to G1 or Shenandoah and
re-tune pause-time thresholds — a real, unplanned capacity exercise. Pack200's
removal broke deploy tooling outright, since it had been the packaging mechanism
for a decade with no replacement carrying the same feature set.

---

## 15 — The preview/preview/preview year (2020, LTS)

**Shipped**: **text blocks standard** (JEP 378), **ZGC production** (JEP 377),
records **second preview** (JEP 384), **sealed classes first preview** (JEP 360),
pattern matching `instanceof` **final** (JEP 394 — so it is 16, not 15), and
`CharSequence.chars()`.

**Pressure**: Java's release cadence had changed to 6-monthly. That created a
problem: too much new surface per release would be unmanageable, so Java
introduced **preview features** — fully working but gated behind
`--enable-preview`. Records, sealed classes, and switch patterns all spent
multiple releases in preview before going final.

**Cost**: preview features made code non-portable across releases, and tooling
support lagged. But the mechanism let the language ship much larger changes
safely — the sealed-type and record designs were refined substantially while in
preview.

---

## 16 — Records and sealed types (2021, LTS)

**Shipped**: **records**, **sealed classes** (`permits`), pattern matching for
`instanceof` standard, `Stream.toList()`, `Collectors.toUnmodifiableList`.

**Pressure**: the "data class" pattern required hundreds of lines of boilerplate
per type — equals/hashCode/toString/constructors/copy semantics. And exhaustive
type dispatch was impossible, so `switch` over sealed hierarchies required a
`default` that silently absorbed unknown cases, defeating the point.

**Cost**: records are *shallowly* immutable. Their fields can hold mutable
objects, so a record containing a `List` is not deeply immutable — a source of
real bugs.

Sealed types also create a **compatibility commitment**: `permits` is a closed
set, so adding a subtype is a breaking change. This is intentional (it buys
exhaustiveness) but it inverts the usual open/closed trade-off.

---

## 17 — Sealed + encapsulation lands (2021, LTS)

**Shipped**: pattern matching for `switch` standard, **strong encapsulation of
JDK internals** (JEP 403, Strongly Encapsulate JDK Internals — `--illegal-access`
ignored), `RandomGenerator` API,
contextual records, sealed classes standard.

**Pressure**: the module system was useless while `--illegal-access=permit`
silently opened the JDK. Strong encapsulation was the payoff, three years after
JPMS shipped — and it broke the reflection-heavy ecosystem.

**Cost**: the largest single source of migration pain since Java 9. See
`labs/java/java-migration`.

---

## 18 — UTF-8 by default (2022, LTS)

**Shipped**: **UTF-8 as the default charset** (JEP 400), `SimpleWebServer`,
`CompletableFuture` improvements, `InternetAddress` parsing.

**Pressure**: the platform default charset depended on the OS locale, which made
behaviour platform-dependent and had produced countless mojibake bugs and
security issues (e.g. `ISO-8859-1` misuse).

**Cost**: silent data corruption on upgrade for any code that relied on the
platform default. Files written on JDK 11 with a Latin-1 locale read as garbage
on JDK 18. **This is the single most under-appreciated migration risk.**

---

## 19 — Records in switch, virtual threads preview (2022)

**Shipped**: record patterns preview, **virtual threads** preview, pattern
matching for `switch` *third preview* (final arrives in 21), `java.lang.foreign`
(Panama) preview, structured concurrency *incubator* (JEP 428 — an incubator is a
weaker gate than preview, and this distinction matters when reading 19's notes).

**Pressure**: platform threads cost ~1 MB of stack each and were OS-thread-bound,
which made high-concurrency IO services uneconomic. Project Loom targeted the
concurrency model itself, not the API.

---

## 20 — Pattern matching everywhere (2023)

**Shipped**: virtual threads **second preview**, structured concurrency second
preview, record patterns second preview, `switch` pattern matching fourth
preview, `java.lang.foreign` second preview, vector API fifth incubator.

**Correction worth recording**: it is easy to assume pattern matching
"completed" here, because all three pieces existed in preview by this point. But
none of them were final until **21** — record patterns (JEP 440), switch patterns
(JEP 441), and virtual threads (JEP 444) all shipped together in 21. Version-20
is the last preview iteration, not a feature release.

**Pressure**: pattern matching was the last major gap versus Kotlin/Scala, but the
construct took **five releases to stabilise** — switch preview (17), record-patterns
preview (19), then four preview iterations of the switch side (17→19→20→21). The
slow convergence is the lesson: a large language feature costs multiple release
cycles to get the exhaustiveness and null-handling rules right.

**Cost**: once final in 21, `switch` over sealed types is compiler-checked for
exhaustiveness, which is a benefit — but adding a permitted subtype becomes a
compile-time break for every consumer, reinforcing the sealed commitment from 16.

---

## 21 — The LTS consolidation release (2023, LTS)

**Shipped**: **virtual threads** (now mainstream), pattern matching for `switch`,
record patterns, **sequenced collections**, string templates preview,
`StructuredTaskScope` preview, `ExecutorService` rewritten on virtual threads,
`Thread.ofVirtual`.

**Pressure**: 21 was a deliberate consolidation — many preview features from 19
and 20 went final together, making it the "modern concurrency" baseline.

**Cost**: virtual threads changed the sizing story completely. Thread pools sized
for platform threads are now *anti-patterns*; the guidance inverted to
"one virtual thread per task, use a semaphore for CPU work." Existing pool-based
code did not break, but it stopped being the right shape — a subtler failure
than a compile error.

---

## 22 — Unnamed patterns and variables (2023)

**Shipped**: unnamed variables and patterns (`_`, JEP 456), **Foreign Function &
Memory API final** (JEP 454), **implicitly declared
classes and instance main** (second preview — the second Java program without a
`public class`), multi-file source-code programs, Class-File API *preview*
(JEP 457 — final only in 24), and the FFM API reaching fourth preview.

**Pressure**: unused variables in patterns (`case Point(var x, var y)` where `y`
is unused) were noise. Also the "beginner wall" — the first Java program still
required understanding of `public static void main` and a class.

**Cost**: both headline features stayed in preview for **two more releases**
(instance main went final as JEP 512 in 25), so the ergonomic win that developers
most wanted landed three years after first previewing.

---

## 23 — ZGC generational, string templates (2023)

**Shipped**: **ZGC generational mode by default** (JEP 474 — experimental
generational ZGC shipped in 21 as JEP 439), **string templates** second preview,
flexible constructor bodies second preview, structured concurrency third preview,
Scoped Values third preview, primitive-types-in-patterns preview, and Markdown
documentation comments.

**Pressure**: generational ZGC brought G1-class pause behaviour to large heaps
*by default*, two years after Shenandoah got the same treatment. String templates
aimed at SQL injection avoidance via type-safe interpolation.

**Correction worth recording**: finalization was deprecated for removal in
**18** (JEP 421), not in 23. If you see a claim that 23 deprecated `finalize()`,
it conflated JEP 421 with a different 23 change — and the 18 attribution matters,
because that is where `--illegal-access`-era migration work met deprecation
warnings.

**Cost**: string templates' withdrawal is a notable lesson — the feature solved
a real problem with an API that the community rejected, and shipping it to
preview let the design be killed before it was final. Good argument for
previews.

---

## 24 — The removal release (2024, LTS)

**Shipped**: **SecurityManager permanently disabled** (JEP 486 — deprecated in 17
as JEP 411, then terminally deprecated and disabled), **`Stream` Gatherers**
(JEP 485), **Class-File API final** (JEP 484), AOT class loading & linking
(JEP 483), **flexible constructor bodies** third preview (JEP 492),
**generational Shenandoah (experimental**, JEP 404), **virtual-thread pinning
resolved** (JEP 491 — `synchronized` no longer pins), primitive patterns second
preview, the 32-bit x86 port removed, JNDI restrictions prepared, ZGC's
non-generational mode removed, and string templates' third preview (JEP 465,
**withdrawn**).

**Pressure**: cleanup. Once JEP 403, Strongly Encapsulate JDK Internals, had
been in force for seven years, the
`SecurityManager` was pure liability; Gatherers fixed the long-standing absence
of a sanctioned `Stream` extension point; and JEP 491, Synchronize Virtual Threads
without Pinning, removed what was probably
the single most-cited virtual-thread complaint — `synchronized` pinning.

**Cost**: disabling the `SecurityManager` removed a long-standing source of
classpath and runtime surprises, but also removed the mechanism some enterprise
deployments had used for sandboxing. The withdrawal of string templates (JEP 465)
is the other cost — a feature that solved a real problem in 21 through 24 was
killed rather than shipped, which is the strongest possible argument that
preview exists.

---

## 25 — The current frontier (2025, LTS)

**Shipped**: **compact object headers** (JEP 519), **module import declarations**
(JEP 511 — `import module java.base`), **Scoped Values standard** (JEP 506),
**flexible constructor bodies standard** (JEP 513), **compact source files and
instance main** (JEP 512 — previewed from 22), **generational Shenandoah by
default** (JEP 521), AOT method profiling (JEP 515), AOT command-line ergonomics
(JEP 514), the PEM crypto API, and **HTTP/3 for the HTTP Client API** (JEP 517).

**Pressure**: three separate pressures converged here.

1. **Memory density** — compact object headers cut the object header from 12–16
   bytes to a flat 8, by folding the compressed class pointer into the mark word.
   With object headers having been a fixed cost since 1.0, and JEP 450 observing
   that *more than 20% of live data can be headers alone*, this was the largest
   memory-layout change in the platform's history. It is also the most
   structurally invasive: it changes `java.lang.Object` itself. Note it stays
   **opt-in in 25** — JEP 519 promoted it to a product feature but explicitly
   did not make it the default layout.
2. **Migration friction** — `import module` directly attacks the ergonomics
   complaint that made JPMS adoption stall. Sixteen years after the module system
   shipped, the platform finally reduced its cost of use.
3. **Concurrency completion** — Scoped Values go final six years after Loom
   started in 19, closing the structured-data-flow story.

**Cost**: compact object headers change object size and therefore heap
behaviour — heap-dump tooling, memory accounting, and any code assuming fixed
object layout must be revalidated. Another case of a "harmless-sounding"
upgrade with real consequences.

---

## Cross-cutting patterns in the timeline

Reading 1.2 → 25, four themes recur:

1. **Boilerplate elimination follows widespread pain.** Generics (5) for casts,
   try-with-resources (7) for close(), lambdas (8) for anonymous classes,
   records (16) for data classes.
2. **Preview features became the release valve.** Since 12–14, complex features
   ship in preview for 1–3 releases. This is how sealed classes, records,
   pattern matching, virtual threads, and string templates all landed.
3. **API evolution mechanisms came from necessity.** Default methods (8),
   modules (9), and compact headers (25) all exist to let the platform change
   without breaking the ecosystem.
4. **The runtime keeps being rebuilt.** GC from CMS→G1→ZGC→Shenandoah
   (9→24), memory layout in 25, concurrency from threads→pools→virtual threads
   (5→21).

## Sourced field notes (fetched Oct 2026 — verify before citing)

- **OpenJDK JEP index** — the authoritative record of every feature/JEP by JDK
  version. The primary source for any "which version shipped X" question.
  <https://openjdk.org/jeps/0>
- **Java SE support roadmap** — LTS cadence, release dates, vendor support
  windows. Essential for target-JDK decisions.
  <https://www.oracle.com/java/technologies/java-se-support-roadmap.html>
- **JEP 395: Records** (JDK 16) — the record design rationale, including the
  shallow-immutability discussion. (Its preview lineage is JEP 359 → JEP 384.)
  <https://openjdk.org/jeps/395>
- **JEP 409: Sealed Classes** (JDK 17) — why `permits` is a closed set and the
  exhaustiveness/exchange trade-off. (Preview lineage: JEP 360 → JEP 397.)
  <https://openjdk.org/jeps/409>
- **JEP 441: Pattern Matching for switch** (JDK 21) — the final switch-pattern
  feature and its exhaustiveness rules. (Preview lineage: JEP 406 → 427 → 433.)
  <https://openjdk.org/jeps/441>
- **JEP 440: Record Patterns** (JDK 21) — completes destructuring, and shows how
  far pattern matching iterated over five releases.
  <https://openjdk.org/jeps/440>
- **JEP 400: UTF-8 by Default** (JDK 18) — the data-corruption risk for code
  relying on the platform default charset.
  <https://openjdk.org/jeps/400>
- **JEP 519: Compact Object Headers** (JDK 25) — the memory-layout change and
  its consequences.
  <https://openjdk.org/jeps/519>
- **JEP 444: Virtual Threads** (JDK 21) — why thread-pool sizing guidance
  inverted.
  <https://openjdk.org/jeps/444>
- **Java Language Specification, JLS 13.5** — the binary-compatibility rules
  that define what a version change may not break.
  <https://docs.oracle.com/javase/specs/jls/se21/html/jls-13.html>