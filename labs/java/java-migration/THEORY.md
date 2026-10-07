# THEORY — Java Migration

## 1. The three compatibility surfaces

A JDK upgrade breaks code at three distinct levels. Most migration plans only
budget for the first one, which is why "it compiled" is not "it works."

### 1.1 Source compatibility

Old source must still *parse and compile*. This is the surface build tools
automate.

```bash
javac --release 17 -d out src/main/java
```

`--release N` is stricter and more correct than `-source`/`-target` combined:
it checks against the JDK N API signature data, so you cannot accidentally
compile against a newer method that does not exist on the runtime you ship.

Breakers here are mostly *removals* and *access tightening*:

- **Removed modules and tools**: the Java EE and CORBA modules in 11 (JEP 320 —
  `java.xml.bind` (JAXB), `java.xml.ws` (JAX-WS), `java.activation`, `java.corba`),
  `javah` in 10 (JEP 313), Nashorn in 15 (JEP 372), and Pack200 in 14 (JEP 367).
- **Encapsulated, not removed**: internals such as `sun.nio.ch` and most of
  `sun.misc.Unsafe`'s surroundings became inaccessible in 17 (JEP 403) — the classes
  still exist, but reflective access now throws.
- Default-method conflicts on interfaces (Java 8+).
- Removal of `-XX:+UseConcMarkSweepGC` and CMS in JDK 14 (JEP 363).
- **`-source`/`-target` without `--release` is *not* an error on a modern javac** — it
  compiles and prints a warning (measured on javac 23: `location of system modules
  is not set in conjunction with -source 17`). That warning is the migration
  signal: it means you are linking against the *current* JDK's API, not the
  target's, which is exactly how code that uses a newer method ends up with a
  `NoSuchMethodError` on the older runtime you ship.

### 1.2 Binary compatibility

Pre-compiled jars must still *link and run*. JLS 13.5 defines binary
compatibility; the notable breakages:

- Removal of a method from a public class (rare in the JDK itself).
- Changing a field's type or a method signature in a public API.
- JPMS encapsulation: `IllegalAccessError` at runtime for reflective access to
  JDK internals that used to be `setAccessible(true)`-permitted.
- Removal of `java.lang.SecurityManager`-dependent behaviour (deprecated for
  removal in 17 via JEP 411, disabled by default in 18, **permanently disabled in
  24** via JEP 486).
- **`Unsafe.defineAnonymousClass` removed in JDK 17.** Deprecated in JDK 15 by
  JEP 371 (Hidden Classes); Oracle's JDK 17 release notes state the API "has been
  removed" with `Lookup::defineHiddenClass` as the replacement. This is what broke
  old bytecode-generation libraries (cglib, early Mockito) with `NoSuchMethodError`.
- **A separate, later `Unsafe` change: the memory-access methods** (`getInt`,
  `putLong`, `allocateMemory`, ...). Terminally deprecated in JDK 23 (JEP 471) and
  **warning on first use in JDK 24** (JEP 498 — a *warning*, not a removal; later
  releases escalate). Replacements are `VarHandle` (JEP 193, JDK 9) and the Foreign
  Function & Memory API (JEP 454, JDK 22). Do not conflate the two changes: one is
  a hard removal that breaks proxy generation, the other a phased warning that hits
  off-heap and direct-memory code.

The classic symptom: everything compiles, and then `NoSuchMethodError` or
`IllegalAccessError` fires only on the code path nobody tested.

### 1.3 Behavioural compatibility

Same code, different observable behaviour. This is the dangerous surface.

| Behaviour | Changed in | Risk |
|---|---|---|
| Strong encapsulation of JDK internals | 9 (incubating), 17 (enforced) | `InaccessibleObjectException` |
| Default charset from platform locale | 18 | Text corruption on legacy-encoded data |
| `Locale` provider switch to CLDR | 9 | Date/number formatting output differs |
| Removed CMS collector | 14 (JEP 363) | GC pause profile changes |
| Removed `Pack200` | 14 (JEP 367) | Old deploy tooling breaks |
| ZGC experimental → production | 11 (JEP 333) → 15 (JEP 377) | Latency shifts, tuning flags renamed |
| Sealed/`record` tighten `equals`/`hashCode` | 16 | Map/set behaviour can differ |
| Iterative `HashMap` splitting | 8 (JEP 180) | Resize-order, not correctness |
| `Stream`/`Optional` strictness | 9+ | `NullPointerException` surfaces earlier |
| Compact strings (Latin-1 storage) | 9 (JEP 254) | Memory accounting shifts |
| `SecurityManager` disabled by default → permanently off | 18 → 24 (JEP 486) | Permission checks become no-ops |
| Compact object headers (opt-in flag) | 25 (JEP 519; experimental in 24 via JEP 450) | Object size, heap dumps, layout assumptions. Saves 4–8 B/object, not 16 |

**Case worth calling out for a migration plan: compact object headers.** The
mechanism changed (mark word and class word merged into one 8-byte header), so
any code, agent, or tool that hard-codes object layout assumptions must be
revalidated. Two traps for a rollout plan: it is **still opt-in in 25**
(`-XX:+UseCompactObjectHeaders`), and it silently disables itself when
compressed class pointers are off, above an 8 TB heap on non-ZGC collectors, or
under JVMCI. Validate with JOL on your actual objects rather than trusting the
byte arithmetic.

## 2. The compile-first pipeline

Migrations succeed when the pipeline is ordered so that each stage's failures
are cheap to fix.

```
Stage 0  Inventory      jdeps --jdk-internals, dependency tree, encoding audit
Stage 1  Compile        bump maven.compiler.release, fix source errors
Stage 2  Test           run full suite on the new JDK, fix behavioural breaks
Stage 3  Static         error-prone / forbidden-apis / Animal Sniffer gates
Stage 4  Canary         single AZ / 5% traffic, SLO-gated, instant rollback
Stage 5  Fleet          progressive rollout across regions and services
```

**Stage 0 is the one teams skip.** Skipping it means discovering internal-API
usage from a `NoSuchMethodError` in production.

### The two static-analysis gates

```bash
# What internal JDK APIs do we touch?
jdeps --jdk-internals --multi-release base target/app.jar

# What APIs are newer than our declared target?
mvn com.github.spotbugs:spotbugs-maven-plugin:check
```

For Java 9+ cross-compilation correctness, Animal Sniffer enforces a signature
set:

```xml
<plugin>
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>animal-sniffer-maven-plugin</artifactId>
  <version>1.23</version>
  <configuration>
    <signature>
      <groupId>org.codehaus.mojo.signature</groupId>
      <artifactId>java18</artifactId>
      <version>1.0</version>
    </signature>
  </configuration>
</plugin>
```

## 3. Toolchain mechanics

### Maven

```xml
<properties>
  <maven.compiler.release>17</maven.compiler.release>
</properties>
```

Use `--release`, not `source`/`target`. `release` validates against real API
signatures; `source`/`target` sets the language level and class-file version but
still links against the *current* JDK's API, producing the classic
`NoSuchMethodError` in production.

### Gradle

```groovy
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}
```

Gradle toolchains are the cleanest way to guarantee the compile JDK and the
runtime JDK agree. Without a toolchain, Gradle compiles with whatever
`JAVA_HOME` points at.

### JPMS encapsulation

Java 9 added `--illegal-access=permit` as a migration escape hatch; JDK 17
made that default *deny*. Migration options, best first:

1. **Stop using the internal API.** The correct fix, and usually less work
   than it appears (see §4).
2. `--add-opens java.base/java.lang=ALL-UNNAMED` — surgical, explicit, and
   reviewable. Use it, but treat it as a tracked debt item.
3. Upgrade the library that caused the need (often `Mockito`, `cglib`,
   old Hibernate, or a hand-rolled `Proxy`).

```java
// Instead of reflecting into JDK internals, use the supported API.
MethodHandles.privateLookupIn(SomeClass.class, MethodHandles.lookup())
        .unreflectSetter(field)   // module-aware, throws if genuinely inaccessible
```

## 4. The internal-API replacement map

| Internal usage | Replacement | Notes |
|---|---|---|
| `sun.misc.Unsafe` memory ops | `VarHandle` (JDK 9+) | Off-heap work in `java.nio` uses VarHandles |
| `sun.nio.ch.DirectBuffer` | `ByteBuffer` + `MethodHandles` | Prefer not direct at all |
| `javax.xml.bind.*` (JAXB) | Add `jakarta.xml.bind-api` + impl | Package rename `javax` → `jakarta` |
| `java.activation` | `jakarta.activation-api` | |
| `com.sun.net.ssl.*` | JSSE: `SSLContext`, `TrustManager` | Never use the internal class |
| `sun.security.x509` | `java.security.cert.CertificateFactory` | Parse via factory |
| `java.util.jar.Pack200` | jlink / custom image | Tooling replacement, not a library |
| `Nashorn` (`jjs`) | GraalJS, or move to Node | JDK 15 removed Nashorn |
| `Class.newInstance()` | `clazz.getDeclaredConstructor().newInstance()` | Better exception semantics |
| `System.runFinalizersOnExit` | `Runtime.addShutdownHook` | |
| `AccessController.doPrivileged` | Drop it; module system handles it | Removed in JDK 24 |

## 5. Dependency realities

Upgrading the JDK does not upgrade your dependencies, and old dependencies are
the actual blockers.

- **Reflection-heavy libs** break under strong encapsulation. Symptom:
  `InaccessibleObjectException` at bean-instantiation time.
- **Bytecode generators** (cglib, early Mockito, Javassist) break when
  `Unsafe.defineAnonymousClass` is removed in JDK 17.
- **Annotation processors** can break silently on language-level changes.
- **JAXB/JAFB** removal is a dependency problem, not a code problem — the
  classes simply are not in the JDK any more.
- **Transitive test-scoped** surprises: a plugin's own transitive dep can
  conflict with the new runtime.

The discipline: **upgrade libraries before, or at the same time as, the JDK.**
Never both in the same deploy if you can avoid it — you lose attribution.

## 6. Testing for behavioural parity

Unit tests catch contract breaks. They mostly miss *data* breaks.

```java
@Test
void legacyEncodingSurvivesUpgrade() {
    // Before the upgrade, files were written with the platform charset.
    // JDK 18 changed the default to UTF-8, so an explicit read is now required.
    String raw = Files.readString(path, StandardCharsets.ISO_8859_1);
    assertThat(raw).contains("café");   // would fail post-JDK-18 without the charset
}
```

High-value parity tests, in order:

1. **Encoding round-trips** — read/write legacy-encoded fixtures explicitly.
2. **Ordering guarantees** — assert on iteration order where code depends on it.
3. **Numeric/date formatting** — CLDR changed `Locale` output for several
   locales; golden-file the formatted strings.
4. **Hash/equality semantics** — `record` and `sealed` change synthesized methods.
5. **GC and timeout thresholds** — GC change alters pause profiles; re-tune.
6. **Reflection reachability** — an integration test per reflective component.

## 7. Rollout mechanics

The migration is not done when it deploys. It is done when the old fleet is
decommissioned and the rollback path is closed.

- **Canary**: one availability zone, 1–5% traffic, SLO-gated for a full
  business cycle (weekend traffic is a different shape than weekday).
- **Rollback without rebuild**: keep the previous image tagged and pullable.
  A rollback that requires re-running your build is a rollback that takes 20
  minutes, which is 20 minutes of the SLO you were trying to protect.
- **Dual-run shadowing** for the riskiest service: send production traffic to
  both versions, compare responses, alert on divergence.
- **Decommission**: remove the old JDK image, remove compatibility flags, close
  the `--add-opens` debt items. This step is routinely skipped, so the flags
  become permanent and nobody notices.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)

- **JEP 403: Strongly Encapsulate JDK Internals** (JDK 17, Sept 2021) —
  `--illegal-access` ignored by default; JDK internals strongly encapsulated.
  <https://openjdk.org/jeps/403>
- **JEP 411: Deprecate the Security Manager for Removal** (JDK 17) and
  **JEP 486: Permanently Disable the Security Manager** (JDK 24) — the manager
  goes from deprecated, to disabled-by-default (18), to permanently off (24).
  <https://openjdk.org/jeps/486>
- **JEP 400: UTF-8 by Default** (JDK 18) — the silent-corruption risk from §1.3.
  <https://openjdk.org/jeps/400>
- **JEP 471 / JEP 498** — `sun.misc.Unsafe` memory-access methods terminally
  deprecated (23), then a run-time warning on first use (24).
- **JEP 371: Hidden Classes** (JDK 15) — deprecates `Unsafe.defineAnonymousClass`
  (removed in 17, per Oracle's JDK 17 release notes).
  <https://openjdk.org/jeps/371>
  <https://openjdk.org/jeps/498>
- **`jdeps` tool documentation** — the `--jdk-internals` flag is the canonical
  first migration step.
  <https://docs.oracle.com/en/java/javase/21/docs/specs/man/jdeps.html>
- **Animal Sniffer documentation** — signature-based API conformance checking
  for cross-compilation.
  <https://www.mojohaus.org/animal-sniffer/>
- **`--release` documentation** — why `--release` beats `-source`/`-target`.
  <https://docs.oracle.com/en/java/javase/21/docs/specs/man/javac.html>