# THEORY — Java Features from 1.2 to 25

Each section: **what shipped**, **the pressure that produced it**, and
**what it cost**.

---

## 1.2 — "Java 2": the Collections Framework (December 1998)

**Shipped**: the **Collections Framework** (`List`, `Set`, `Map`, and `Iterator`
replacing `Enumeration`), **Swing**, `strictfp`, JDBC 2.0, and the "Java 2"
branding that split the platform into J2SE, J2EE and J2ME.

**Pressure**: 1.0 and 1.1 shipped only arrays, `Vector` and `Hashtable`. A
language used for server work needed reusable, consistently-designed data
structures, and the Collections Framework was the first mature package of them.

**Cost**: the collections arrived *before* generics, so every element came out as
`Object` and needed a cast. That is the pressure that produces generics six years
later (see 5). Legacy `Vector`/`Hashtable` were retrofitted onto the framework
rather than removed, and they are still in the JDK.

---

## 1.4 — Assertions, regex, NIO, logging (February 2002)

**Shipped**: the `assert` keyword, `java.util.logging`, `java.util.regex`,
`java.nio` (buffers, channels, selectors), chained exceptions
(`Throwable.getCause`) and the JAXP XML APIs bundled into the platform.

**Pressure**: production services needed non-blocking I/O to scale past one thread
per connection, and developers needed a built-in way to log and assert without
third-party libraries.

**Cost**: `java.util.logging` never displaced Log4j and later SLF4J, so most
applications carry more than one logging API. The JDK added a facade,
`System.Logger` (JEP 264, JDK 9), over whichever backend is configured — it
exists *because* the logging landscape stayed fragmented.

---

## 5 (version "1.5") — The generics release (September 2004)

Java 5 and "1.5" are the same release; the version was renumbered at launch.

**Shipped**: **generics** (JSR 14), **enums**, **annotations** (JSR 175),
**autoboxing**, **varargs**, the **enhanced `for` loop** and **static imports**
(these language features are JSR 201), `StringBuilder`, the **`java.util.concurrent`
package** (JSR 166: thread pools, `ConcurrentHashMap`, `CountDownLatch`,
`Semaphore`, `CyclicBarrier`, `BlockingQueue`, `ScheduledExecutorService`,
`java.util.concurrent.atomic`, `java.util.concurrent.locks`) and a **rewritten Java
Memory Model** (JSR 133).

**Pressure**: collections had no compile-time type safety, forcing casts at every
read. `int` constants for enumerated values were not type-safe. And Java's thread
primitives (`synchronized`, `wait`, `notify`) were too low-level to build servers
on safely, while the original memory model had well-known holes.

**Cost of erasure**: generics are implemented by erasure to preserve binary
compatibility, so `List<String>` is not reifiable at run time. You cannot overload
on a generic type, cannot write `new T[]`, and cannot write
`instanceof List<String>`. That is the price of introducing generics without
breaking every existing class file — and the reason wildcards (`List<?>`) exist.

**Cost of the concurrency package**: it is a large API with several locking
mechanisms, and it took years for most teams to use it correctly. The *memory
model* (JSR 133) is what finally made those APIs' guarantees well-defined; the
older double-checked-locking idioms remained broken for code that ignored it.

---

## 6 — The scripting and performance release (December 2006)

**Shipped**: the **scripting API** (JSR 223), the **compiler API**, JDBC 4.0,
`SwingWorker`, and concurrency-library additions that complete the Java 5 package:
`Deque`/`ArrayDeque`, `NavigableMap`/`NavigableSet`, `ConcurrentSkipListMap` and
`ConcurrentSkipListSet`. `@Override` became legal on methods that implement an
*interface* (Java 5 only allowed it on superclass overrides).

**Pressure**: 6 was mostly a performance-and-polish release after the large
language changes of 5, and it is where the JVM's tuning story (and later
biased locking, which JEP 374 disabled in 15) starts to matter operationally.

---

## 7 — Project Coin and `invokedynamic` (July 2011)

**Shipped**: the **Project Coin** language changes (JSR 334) — `try`-with-resources,
the diamond operator `<>`, strings in `switch`, multi-catch, binary literals and
underscores in numeric literals — plus **NIO.2** (`java.nio.file`, JSR 203),
the **Fork/Join framework**, `java.util.Objects`, and the **`invokedynamic`**
bytecode (JSR 292), which is the mechanism lambdas are later compiled against.

**Pressure**: a set of small, self-contained language annoyances (resource-closing
boilerplate, repeated generic type arguments, verbose multi-catch) that Project
Coin addressed without a large language redesign.

**Cost**: minor. Diamond inference was weak — it could not infer from the target
type in a method-argument position until Java 8 improved target typing
(JEP 101).

---

## 8 — The lambda release (March 2014, LTS)

**Shipped**: **lambda expressions** and method references (JEP 126),
`@FunctionalInterface`, **default and static interface methods**, the **`Stream`
API** (JEPs 107 and 109), **`Optional`**, the **`java.time` date and time
API** (JEP 150), **repeatable annotations** (JEP 120), **type annotations**
(JEP 104), improved target typing (JEP 101), `CompletableFuture`, and **HashMap
collision handling with balanced trees** (JEP 180).

**Pressure**: two forces at once. Functional programming had won the industry
argument (map/filter/reduce, immutability), and the collections API had no way to
add methods such as `forEach`, `removeIf` or `Map.getOrDefault` without breaking
every existing implementor. **Default methods** were the mechanism that let
interfaces grow, and lambdas were the reason to want those methods.

**Costs, both still felt today**:

- `Optional` was **contested**. Its designers intended it for *method return
  types only*, a position the ecosystem never fully honoured; `Optional` fields
  and parameters remain a common anti-pattern.
- **Default methods created a diamond problem**: if a class inherits the same
  default from two interfaces, it *must* override it to resolve the conflict.
  That is the price of letting interfaces evolve after the fact.

---

## 9 — The module release (September 2017)

**Shipped**: the **module system** (JSR 376, JEP 261), `jlink` (JEP 282) for
building minimal runtime images, `jshell` (JEP 222), **G1 as the default
collector** (JEP 248), **compact strings** (JEP 254), **CLDR as the default locale
data** (JEP 252), collection factory methods such as `List.of` (JEP 269), the
Stack-Walking API (JEP 259), the `Flow` reactive-streams API (JEP 266), and
**Milling Project Coin** (JEP 213: private interface methods, diamond with
anonymous classes, effectively-final variables in try-with-resources).

**Pressure**: the classpath made strong encapsulation impossible — every public
class in a jar was reachable by everyone — and building a minimal custom runtime
image was impractical.

**Cost**: the module system was adopted slowly, because `split package`
restrictions broke much of the older ecosystem and the migration story was poor;
that is why `--illegal-access` and later `--add-opens` stayed necessary for years.
The *quiet* costs were elsewhere: **G1-as-default and CLDR-as-default both changed
behaviour with no code change**, which is why they appear in the migration lab as
silent-break risks rather than as features.

---

## 10 — Local-variable type inference (March 2018)

**Shipped**: `var` for local variables (JEP 286), **parallel full GC for G1**
(JEP 307), removal of the `javah` tool (JEP 313) and **time-based release
versioning** (JEP 322 — the six-month cadence is a 10-era decision). API
additions without a JEP: `List.copyOf`/`Set.copyOf`/`Map.copyOf` and
`Collectors.toUnmodifiableList`.

**Pressure**: the verbosity of writing a long generic type on both sides of an
assignment, e.g. `Map<String, List<String>> m = new HashMap<String, List<String>>()`.

**Cost**: mild but real. `var` is deliberately narrow: it infers only local
variables, never fields, parameters or return types, and in 10 it could not be
used for lambda parameters (that arrives in 11 via JEP 323). It also erases the
documentation value of an explicit type, so OpenJDK's own style guidance is to use
it when the type is already evident from the right-hand side.

---

## 11 — HTTP client, Flight Recorder, and the Java EE removal (September 2018, LTS)

**Shipped**: the **HTTP Client API** (JEP 321), **`var` in lambda parameters**
(JEP 323), **launching single-file source programs** (`java Hello.java`, JEP 330),
**Flight Recorder** in the JDK (JEP 328), **TLS 1.3** (JEP 332), **ZGC as an
experimental collector** (JEP 333), plus string methods (`strip`, `repeat`,
`lines`, `isBlank`), `Files.readString`/`writeString` and `Optional.isEmpty()`.

**Removed and deprecated**: the **Java EE and CORBA modules were removed**
(JEP 320 — the JAXB/JAX-WS break that every 8 → 11 migration hits), and **Nashorn**
(JEP 335) and **Pack200** (JEP 336) were **deprecated**.

**Pressure**: `HttpURLConnection` was long-obsolete, the "run a Java file without
compiling" story was a perennial developer-experience complaint, and the Java EE
modules had no business living inside the JDK.

**Cost**: JEP 320 is the first large *dependency* break of the modern era: code
that used `javax.xml.bind` compiled on 8 and simply had no classes on 11. It is
the origin of "libraries first, JDK second".

---

## 12–13 — Switch expressions and text blocks, first previews (2019)

**Shipped in 12 (March 2019)**: **switch expressions** as a preview (JEP 325),
**Shenandoah** as an experimental collector (JEP 189), abortable mixed collections
for G1 (JEP 344) and default CDS archives (JEP 341).

**Shipped in 13 (September 2019)**: **text blocks** as a preview (JEP 355), switch
expressions' second preview (JEP 354) and ZGC's ability to uncommit unused memory
(JEP 351, experimental).

**Worth knowing**: neither feature was final in 12 or 13. Switch expressions went
final in **14** (JEP 361) and text blocks in **15** (JEP 378), which is why the
cluster is easy to misattribute: people remember "a 13 feature" from the preview.

**Pressure**: switch statements had been a known readability problem since Java
1.0, and multi-line strings were impossible until 15 — every JSON payload or SQL
query was string-concatenated.

**Cost**: switch expressions over an `enum` require exhaustive coverage, so the
compiler demanding either a `default` or every constant generated friction for
library authors.

---

## 14 — The garbage collector purge (March 2020)

**Shipped**: **switch expressions final** (JEP 361), **records first preview**
(JEP 359), **pattern matching for `instanceof` first preview** (JEP 305), **text
blocks second preview** (JEP 368), **Helpful NullPointerExceptions** (JEP 358),
**JFR event streaming** (JEP 349), and ZGC on macOS and Windows as experimental
(JEP 364, 365). **Removed**: the **CMS collector** (JEP 363) and the **Pack200
tools and API** (JEP 367). The ParallelScavenge + SerialOld combination was
deprecated (JEP 366).

**Pressure**: GC history. CMS was deprecated in 9 (JEP 291) and removed in 14; the
platform consolidated onto G1 (default since 9, JEP 248) and ZGC (production in 15,
JEP 377). This is the clearest case in Java history of *removal for simplification*
rather than capability.

**Cost**: teams still pinned to CMS in 2020 had to move to G1 or Shenandoah and
re-tune pause-time thresholds — a real, unplanned capacity exercise. Pack200's
removal broke deploy tooling outright; it had been the packaging mechanism for a
decade, deprecated since 11.

---

## 15 — Production GCs, text blocks final, more previews (September 2020)

**Shipped**: **text blocks final** (JEP 378), **ZGC production** (JEP 377),
**Shenandoah production** (JEP 379), **records second preview** (JEP 384),
**sealed classes first preview** (JEP 360), **pattern matching for `instanceof`
second preview** (JEP 375), **hidden classes** (JEP 371), and **biased locking
deprecated and disabled by default** (JEP 374). **Removed**: **Nashorn**
(JEP 372, deprecated since 11).

**Pressure**: Java's release cadence had become six-monthly. Too much new surface
per release would be unmanageable, so Java leaned on **preview features** — fully
working but gated behind `--enable-preview`. Records, sealed classes and switch
patterns all spent multiple releases in preview before going final.

**Cost**: preview features made code non-portable across releases, and tooling
support lagged. But the mechanism let the language ship much larger changes
safely: the sealed-type and record designs were refined substantially while in
preview.

---

## 16 — Records final (March 2021)

**Shipped**: **records final** (JEP 395), **pattern matching for `instanceof`
final** (JEP 394), **sealed classes second preview** (JEP 397), `Stream.toList()`,
and **strong encapsulation of JDK internals by default** (JEP 396 — the
`--illegal-access` default flipped to deny, one release before 17 removed the
flag).

**Pressure**: the "data class" pattern needed hundreds of lines of boilerplate per
type — `equals`/`hashCode`/`toString`/constructors. And exhaustive type dispatch was
impossible, so a `switch` over a sealed hierarchy needed a `default` that silently
absorbed unknown cases.

**Cost**: records are *shallowly* immutable. Their fields can hold mutable
objects, so a record containing a `List` is not deeply immutable — a source of real
bugs.

Sealed types also create a **compatibility commitment**: `permits` is a closed
set, so adding a subtype is a breaking change. This is intentional (it buys
exhaustiveness) but inverts the usual open/closed trade-off.

---

## 17 — Sealed classes and strong encapsulation (September 2021, LTS)

**Shipped**: **sealed classes final** (JEP 409), **strong encapsulation of JDK
internals** with `--illegal-access` ignored (JEP 403), the **SecurityManager
deprecated for removal** (JEP 411), the `RandomGenerator` API (JEP 356), **first
preview of pattern matching for `switch`** (JEP 406), and removal of the
experimental AOT and JIT compiler (JEP 410). Also removed: the `Unsafe`
`defineAnonymousClass` method (deprecated in 15 by JEP 371; Oracle's JDK 17 release
notes confirm the removal and name `Lookup::defineHiddenClass` as the replacement).

**Pressure**: the module system was useless while `--illegal-access=permit`
silently opened the JDK. Strong encapsulation was the payoff, four years after JPMS
shipped — and it broke the reflection-heavy ecosystem.

**Cost**: the largest single source of migration pain since Java 9. See
`labs/java/java-migration`.

---

## 18 — UTF-8 by default (March 2022)

**Shipped**: **UTF-8 as the default charset** (JEP 400), the **Simple Web Server**
(JEP 408), the **Internet-Address Resolution SPI** (JEP 418), **core reflection
reimplemented on method handles** (JEP 416), **finalization deprecated for
removal** (JEP 421) and **code snippets in Javadoc** (JEP 413).

**Pressure**: the platform default charset depended on the OS locale, which made
behaviour platform-dependent and produced countless mojibake bugs.

**Cost**: silent data corruption on upgrade for any code that relied on the
platform default. Files written on JDK 11 with a Latin-1 locale read as garbage on
JDK 18. **This is the single most under-appreciated migration risk.**

---

## 19 — Previews begin to pay off (September 2022)

**Shipped (all as previews or incubators)**: **virtual threads** (first preview,
JEP 425), **record patterns** (first preview, JEP 405), **pattern matching for
`switch`** (third preview, JEP 427), the **Foreign Function & Memory API** (first
preview, JEP 424) and **structured concurrency** (first *incubator*, JEP 428 — an
incubator is a weaker gate than a preview, which matters when reading 19's notes).

**Pressure**: platform threads cost ~1 MB of stack each and were OS-thread-bound,
which made high-concurrency IO services uneconomic. Project Loom targeted the
concurrency model itself, not the API.

---

## 20 — The last preview round (March 2023)

**Shipped (still not final)**: **virtual threads** second preview (JEP 436),
**record patterns** second preview (JEP 432), **pattern matching for `switch`**
fourth preview (JEP 433), the **FFM API** second preview (JEP 434), **Scoped
Values** as an incubator (JEP 429), **structured concurrency** second *incubator*
(JEP 437) and the **Vector API** fifth incubator (JEP 438).

**Worth knowing**: it is easy to assume pattern matching "completed" here, because
every piece existed in preview. But none of the three headline features were final
until **21** — record patterns (JEP 440), switch patterns (JEP 441) and virtual
threads (JEP 444) all went final together. 20 is the last preview iteration, not a
feature release.

**Pressure**: pattern matching was the last major gap versus Kotlin and Scala, but
the construct took **five releases to stabilise**: `switch` patterns previewed in
17, 18, 19 and 20 (JEPs 406, 420, 427, 433) before going final in 21 (JEP 441),
with record patterns previewed in 19 (JEP 405) and 20 (JEP 432). The slow
convergence is the lesson — a large language feature costs several release cycles
to get exhaustiveness and null-handling right.

**Cost**: once final in 21, a `switch` over sealed types is compiler-checked for
exhaustiveness, which is a benefit — but adding a permitted subtype becomes a
compile-time break for every consumer, reinforcing the sealed commitment from 16.

---

## 21 — The LTS consolidation release (September 2023, LTS)

**Shipped**: **virtual threads** final (JEP 444), pattern matching for `switch`
final (JEP 441), **record patterns** final (JEP 440), **sequenced collections**
(JEP 431) and **generational ZGC** (JEP 439). First previews of **string
templates** (JEP 430), **structured concurrency** (JEP 453), **Scoped Values**
(JEP 446), unnamed patterns and variables (JEP 443) and unnamed classes with
instance `main` (JEP 445). `Executors.newVirtualThreadPerTaskExecutor()` is the
idiomatic way to use virtual threads.

**Pressure**: 21 was a deliberate consolidation — the pattern-matching and
virtual-thread previews that had run through 17–20 went final together, making it
the "modern concurrency" baseline.

**Cost**: virtual threads changed the sizing story completely. Thread pools sized
for platform threads are now *anti-patterns*; the guidance inverted to
"one virtual thread per task, use a semaphore for CPU work." Existing pool-based
code did not break, but it stopped being the right shape — a subtler failure
than a compile error.

---

## 22 — Unnamed variables, FFM final (March 2024)

**Shipped**: **unnamed variables and patterns** final (`_`, JEP 456), the
**Foreign Function & Memory API final** (JEP 454), and **multi-file source-code
programs** (JEP 458). Preview rounds continued for the **Class-File API**
(JEP 457), **Stream Gatherers** (JEP 461), **structured concurrency** (second
preview, JEP 462), **Scoped Values** (second preview, JEP 464), **flexible
constructor bodies** (first preview, as "Statements before `super(...)`",
JEP 447), implicitly declared classes with instance `main` (second preview,
JEP 463) and **string templates** (second preview, JEP 459).

**Pressure**: unused variables in patterns (`case Point(var x, var y)` where `y`
is unused) were noise. Native interop had been `JNI` since 1.1; FFM finally gave
Java a supported, safe alternative, and it is the API JEP 498 names as the
replacement for `Unsafe`'s memory-access methods.

**Cost**: unnamed variables went final immediately, but the "beginner wall" fix —
a first program with no `public class` and no `public static void main` — took
**four preview rounds**: JEP 445 (21), 463 (22), 477 (23), 495 (24), then final in
25 as JEP 512. Two years from first preview to final, for what looks like a small
ergonomic change, is the clearest illustration of how conservatively language
features move.

---

## 23 — Generational ZGC by default (September 2024)

**Shipped**: **generational mode becomes ZGC's default** (JEP 474; generational ZGC
had been added, behind a flag, in 21 as JEP 439), **Markdown documentation
comments** (JEP 467), and the first step of the `sun.misc.Unsafe` phase-out:
**memory-access methods terminally deprecated** (JEP 471). Preview rounds
continued for structured concurrency (third preview, JEP 480), Scoped Values
(third preview, JEP 481), flexible constructor bodies (second preview, JEP 482),
Stream Gatherers (second preview, JEP 473), the Class-File API (second preview,
JEP 466), module import declarations (first preview, JEP 476) and **primitive types
in patterns** (first preview, JEP 455).

**Notably absent from 23: string templates.** They had previewed in 21
(JEP 430) and 22 (JEP 459); the follow-up JEP 465 was **withdrawn**, so the
feature never became final and did not appear in 23.

**Pressure**: making the generational mode the default meant ZGC users got the
better-performing collector without opting in, and it set up the removal of the
non-generational mode in 24.

**Cost**: for string templates, the cost was all on the developers who adopted
the preview in 21 or 22 — the API was withdrawn rather than finalised. That is
the preview mechanism working as designed, and the strongest practical argument
for never putting a preview feature on a production path.

**Finalization, for the record**: `finalize()` was deprecated for removal in
**18** (JEP 421), not in 23 as some secondary sources say.

---

## 24 — The security-and-cleanup release (March 2025, non-LTS)

**Shipped**: the **SecurityManager permanently disabled** (JEP 486 — deprecated
for removal in 17 via JEP 411, disabled by default in 18), **Stream Gatherers**
final (JEP 485), the **Class-File API** final (JEP 484), **ahead-of-time class
loading & linking** (JEP 483), **virtual threads without `synchronized` pinning**
(JEP 491), **generational Shenandoah** as an experimental option (JEP 404),
**compact object headers** as an experimental option (JEP 450), the
**non-generational ZGC mode removed** (JEP 490), and a **run-time warning on first
use of `Unsafe`'s memory-access methods** (JEP 498). The **Windows 32-bit x86 port
was removed** (JEP 479) and the **Linux 32-bit x86 port deprecated for removal**
(JEP 501). Late barrier expansion for G1 landed (JEP 475). Preview rounds
continued for structured concurrency (fourth, JEP 499), Scoped Values (fourth,
JEP 487), flexible constructor bodies (third, JEP 492), instance `main` (fourth,
JEP 495), module import declarations (second, JEP 494) and primitive patterns
(second, JEP 488).

**Pressure**: cleanup. Once JEP 403 (Strongly Encapsulate JDK Internals) had been
in force since 17, the SecurityManager was pure liability. Gatherers filled the
long-standing absence of a sanctioned `Stream` extension point, and JEP 491
removed what was probably the most-cited virtual-thread complaint:
`synchronized` pinning.

**Cost**: disabling the SecurityManager removed a long-standing source of
classpath and runtime surprises, but it also removed the mechanism some
enterprise deployments had used for sandboxing. And the `Unsafe` warning is the
first one most teams will see in logs: it is a *warning*, not a removal, which
makes it easy to ignore until the phase-out escalates.

**24 is not an LTS.** Oracle's roadmap lists 22–24 as non-LTS with six-month
support, which is why the interesting question for a fleet is usually "21 or 25",
not "24".

---

## 25 — The current LTS (September 2025, LTS)

**Shipped**: **compact object headers** as a product feature (JEP 519),
**module import declarations** final (JEP 511 — `import module java.base`),
**Scoped Values** final (JEP 506), **flexible constructor bodies** final
(JEP 513), **compact source files and instance `main`** final (JEP 512),
**generational Shenandoah** as a product option (JEP 521), **ahead-of-time
method profiling** (JEP 515) and **command-line ergonomics** (JEP 514), and the
**Linux 32-bit x86 port removed** (JEP 503). Still in preview: structured
concurrency (fifth, JEP 505), primitive types in patterns (third, JEP 507) and
PEM encodings (first, JEP 470).

**Pressure**: three separate pressures converged here.

1. **Memory density** — compact object headers cut the object header from 12–16
   bytes to a flat 8, by folding the compressed class pointer into the mark word.
   With object headers a fixed cost since 1.0, and JEP 450 observing that *more
   than 20% of live data can be headers alone*, this is among the most
   structurally invasive memory-layout changes the platform has made: it changes
   `java.lang.Object` itself. Note it stays **opt-in in 25** — JEP 519 promoted it
   to a product feature but explicitly did not make it the default layout.
2. **Import noise and learnability** — `import module` imports every package a
   module exports in one line, which JEP 511 frames as simplifying reuse of modular
   libraries and helping beginners. Crucially it does **not require your own code to
   be modular**: it works in plain classpath code, though you cannot import from the
   unnamed module. It is a convenience layered on the module system, eight years
   after that system shipped in 9, not a fix for its adoption problems.
3. **Concurrency completion** — Scoped Values go final three years after virtual
   threads first previewed in 19, closing the structured-data-flow story. The
   other half, structured concurrency, is still preview.

**Cost**: compact object headers change object size and therefore heap
behaviour — heap-dump tooling, memory accounting, and any code assuming fixed
object layout must be revalidated. Another case of a "harmless-sounding"
upgrade with real consequences.

---

## After 25: 26 and 27 (non-LTS), and the next LTS

Oracle's roadmap lists **26 (March 2026)** and **27 (September 2026)** as non-LTS,
with the next LTS being **29 (September 2027)**. Three changes already delivered
are worth knowing because they alter defaults you may be relying on:

- **26**: **HTTP/3 for the HTTP Client API** (JEP 517) and the **Applet API
  removed** (JEP 504). Structured concurrency reaches its sixth preview
  (JEP 525).
- **27**: **compact object headers become the default** (JEP 534) and **G1 becomes
  the default collector in all environments** (JEP 523). Structured concurrency
  reaches its seventh preview (JEP 533).

The 25 → 27 delta is a *defaults* change, not a feature change: a fleet that
pins no flags will get a different heap layout and collector choice on 27 than on
25. That is the reason to treat "which defaults am I implicitly relying on?" as a
migration question, and to re-baseline memory and pause behaviour rather than
assume 25's numbers carry over.

---

## Cross-cutting patterns in the timeline

Reading 1.2 → 25, four themes recur:

1. **Boilerplate elimination follows widespread pain.** Generics (5) for casts,
   try-with-resources (7) for close(), lambdas (8) for anonymous classes,
   records (16) for data classes.
2. **Preview features became the release valve.** Since 12–14, complex features
   ship in preview for 1–4 releases. This is how sealed classes, records,
   pattern matching and virtual threads landed — and how string templates
   (previewed in 21 and 22, then withdrawn) were stopped before becoming permanent.
3. **API evolution mechanisms came from necessity.** Default methods (8),
   modules (9), and compact headers (25) all exist to let the platform change
   without breaking the ecosystem.
4. **The runtime keeps being rebuilt.** GC from CMS→G1→ZGC→Shenandoah
   (9→25), memory layout in 25 and 27, concurrency from threads→pools→virtual threads
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