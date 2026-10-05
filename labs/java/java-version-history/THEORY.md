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

**Shipped** (12 LTS): switch *expressions*, `G1` improvements, `String.numbered`
(no), records preview, pattern matching `instanceof` preview.
**Shipped** (13): text blocks, switch expressions standard, `instanceof`
pattern matching standard, `Files.mismatch`, `CharBuffer`.

**Pressure**: switch statements had been a known readability disaster since
Java 1.0. Multi-line strings were impossible before 13 — every JSON payload or
SQL query was string-concatenated.

**Cost**: switch expressions over `enum` still need exhaustive coverage, which
is why the compiler requiring either a `default` or all cases covered generated
friction in libraries.

---

## 14 — The garbage collector purges (2020)

**Shipped**: text blocks standard, `switch` expressions with `yield`,
**CMS collector removed**, **Pack200 removed**, pattern matching `instanceof`
preview, records preview, Nashorn deprecated.

**Pressure**: GC history. CMS was deprecated in 8 and removed in 14; the
platform consolidated onto G1 (default since 9) and ZGC (production 15). This
is the clearest case in Java history of *removal for simplification* rather
than capability.

**Cost**: teams still pinned to CMS in 2020 had to move to G1 or Shenandoah and
re-tune pause-time thresholds — a real, unplanned capacity exercise.

---

## 15 — The preview/preview/preview year (2020, LTS)

**Shipped**: records preview, sealed classes preview, pattern matching for
`switch` preview, text blocks standard, ZGC production, `CharSequence`
`chars()`.

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
JDK internals** (JEP 403 — `--illegal-access` ignored), `RandomGenerator` API,
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
matching for `switch` standard, `java.lang.foreign` (Panama) preview, structured
concurrency preview.

**Pressure**: platform threads cost ~1 MB of stack each and were OS-thread-bound,
which made high-concurrency IO services uneconomic. Project Loom targeted the
concurrency model itself, not the API.

---

## 20 — Pattern matching everywhere (2023)

**Shipped**: record patterns standard, **virtual threads** standard, `switch`
pattern matching, **structured concurrency preview**, `ScopedValue` preview,
`java.lang.foreign` preview, sequenced collections (preview).

**Pressure**: pattern matching was the last major gap versus Kotlin/Scala. The
20 release delivered the third and final piece (record patterns), completing the
construct.

**Cost**: `switch` over sealed types is now exhaustive-checked by the compiler,
which is a benefit, but it also means adding a permitted subtype becomes a
compile-time break for every consumer — reinforcing the sealed commitment from 16.

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

**Shipped**: unnamed variables and patterns (`_`), **implicitly declared classes
and instance main** (preview — the second Java program without a `public class`),
`ClassFile` API, FFM API (incubating).

**Pressure**: unused variables in patterns (`case Point(var x, var y)` where `y`
is unused) were noise. Also the "beginner wall" — the first Java program still
required understanding of `public static void main` and a class.

---

## 23 — ZGC generational, string templates (2023)

**Shipped**: **ZGC generational mode**, **string templates** preview, structured
concurrency and ScopedValue second preview, `java.io.IO` read/write atomics.

**Pressure**: generational ZGC brought G1-class pause behaviour to large heaps.
String templates aimed at SQL injection avoidance via type-safe interpolation —
though they shipped in preview and were *ultimately withdrawn* in a later
release after significant API criticism.

**Cost**: string templates' withdrawal is a notable lesson — the feature solved
a real problem with an API that the community rejected, and shipping it to
preview let the design be killed before it was final. Good argument for
previews.

---

## 24 — Generational Shenandoah, final string templates (2024, LTS)

**Shipped**: **generational Shenandoah**, final string templates (later
withdrawn), **SecurityManager terminally deprecated** (JEP 486),
`Stream Gatherers`, `ClassFile` API final, **flexible constructor bodies**
preview, `ScopedValue` third preview, primitive patterns preview.

**Pressure**: bringing every modern collector into generational mode,
standardizing on the newer `Stream` extension point (`gather`) rather than the
ill-fated `Collector`.

**Cost**: the `SecurityManager` finally reached its documented end state, which
removed a long-standing source of classpath and runtime surprises.

---

## 25 — The current frontier (2025, LTS)

**Shipped**: **flexible constructor bodies** (standard), **compact object
headers** (JEP 519), **module import declarations** (`import module java.base`),
ScopedValue standard, StructuredTaskScope second preview, **Generational Shenandoah
and ZGC defaults**, `java.lang.foreign` preview, vector API incubation,
`--source 26` groundwork.

**Pressure**: three separate pressures converged here.

1. **Memory density** — compact object headers shrink every Java object by up to
   16 bytes by sharing a class-level header. With object headers having been a
   fixed cost since 1.0, this was the single largest memory-layout change in
   the platform's history.
2. **Migration friction** — `import module` directly attacks the ergonomics
   complaint that made JPMS adoption stall.
3. **Concurrency completion** — ScopedValue and StructuredTaskScope finish the
   Loom roadmap that began in 19.

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
- **JEP 440: Records** (JDK 16) — the record design rationale, including the
  shallow-immutability discussion.
  <https://openjdk.org/jeps/395>
- **JEP 440 / JEP 409: Sealed Classes** (JDK 17) — why `permits` is a closed set
  and the exhaustiveness/exchange trade-off.
  <https://openjdk.org/jeps/409>
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