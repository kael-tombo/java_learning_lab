# EXERCISES — Java Version History

Ten labs on the *lineage* of the platform. Each has a mechanically checkable
observation. If you cannot produce the observation, you have read a fact, not
learned a version boundary.

Scaffold once: `mkdir -p lineage/src/main/java/com/acme && cd lineage && git init`.

---

## 1. The `--release` error-class matrix

**Goal.** Prove that "it compiles" is version-relative, and catalogue the *classes*
of failure, not just the messages.

```bash
for r in 8 11 17 21 25; do
  javac --release $r -d out/$r $(find src/main/java -name '*.java') 2> err-$r.txt
  echo "release $r -> $(grep -c 'error:' err-$r.txt) errors"
done
grep -oh "error: [a-z' ]*" err-*.txt | sed 's/[A-Za-z_]*$//' | sort | uniq -c | sort -rn
```

**Expected observation.** Five distinct error classes, in this order:

| Class | Example message | Boundary |
|---|---|---|
| Language-feature rejection | `error: records are not supported in -source 11` | per feature |
| API-absence | `package java.net.http does not exist` | `HttpClient` = 11 |
| Preview-feature refusal | `error: records is a preview API and is disabled by default` | add `--enable-preview`, same `r` |
| Removal | `cannot find symbol ... Charset.defaultCharset` semantics | behavioural, silent |
| Encoding/locale | nothing — **no error at all** | 9 and 18 |

**Pass.** You can name, for every error line, whether it is a *language* boundary,
an *API* boundary, or a *removal* — and you can list the errors the compiler
**cannot** produce (the last two rows), which is the expensive class.

---

## 2. Trace a module with `--describe-module`

**Goal.** See Jigsaw (9) as a real graph rather than a concept.

```bash
java --describe-module java.base | head -20
java --describe-module java.base | grep -c '^exports'
java --describe-module java.base | grep 'java.lang'
java --list-modules | wc -l
java --show-module-resolution --module-path . -m com.acme.app 2>&1 | head
```

**Expected observation.** A module descriptor: `java.base@25.0` / `exports
java.lang ... requires java.base ... contains ...`. Then: `--list-modules` prints
~70–80 modules, and `java.se` (the aggregator) shows which ~20 are on the *default*
root set — which is why JAXB removal (11) worked while `java.sql` survived.

**Pass.** You can explain why `java.xml.bind` was *separable* while `java.sql`
was not, using the requires/exports graph above.

---

## 3. Same logic, five ways

**Goal.** Price the evolution 1.4 → 8 → 16 → 21 for one domain problem: summing
the totals of orders grouped by customer, tolerating nulls.

```java
// (a) pre-8: anonymous class + manual null checks
// (b) 8:    lambda + Stream + Optional
// (c) 11:   var + List.copyOf
// (d) 16:   record for Order (no getters/equals/hashCode/toString)
// (e) 21:   sealed Result + exhaustive switch over the sealed hierarchy
```

```bash
for v in 8 11 17 21; do javac --release $v -d out/$v Solution$v.java; done
wc -l Solution*.java
```

**Expected observation.** (b) removes ~60% of (a). (d) removes the boilerplate
that (b) still carried — the *data* classes shrink to two lines while the
algorithm code does not shrink at all, because records did not touch algorithms.
(e) removes the `default:` branch, which is the only line (d)+(b) cannot remove.

**Pass.** For each version you can state which *specific* pain it removed, and
which pain it left in place. Answering "it was nicer" scores zero.

---

## 4. Reproduce the JDK 18 UTF-8 default change

**Goal.** Reproduce THEORY.md §18's silent corruption on a real file.

```bash
printf 'caf\xe9 order %s\n' 42 > legacy.txt          # Latin-1 bytes, 0xE9
jshell <<'EOF'
var raw = java.nio.file.Files.readAllBytes(java.nio.file.Path.of("legacy.txt"));
System.out.println(new String(raw));                                  // default charset
System.out.println(new String(raw, java.nio.charset.StandardCharsets.ISO_8859_1));
System.out.println(java.nio.charset.Charset.defaultCharset());
EOF
```

```bash
java -Dfile.encoding=COMPAT -cp out CharsetDemo 2>/dev/null   # the 18 escape hatch
```

**Expected observation.** On JDK 17 the default decode of `0xE9` is
platform-dependent (`café` on a UTF-8 Linux desktop, `caf?` on a Windows console
or a container with no `LANG`). On JDK 18+ it is always UTF-8, so `0xE9` is an
invalid byte and you get the replacement character `U+FFFD` — **no exception**.
That is the failure: wrong data, not a crash.

**Pass.** You have reproduced at least one *different* result per JDK and can
name the flag that restores the old behaviour (`-Dfile.encoding=COMPAT`), plus
why using it is debt rather than a fix.

---

## 5. CLDR vs COMPAT locale formatting

**Goal.** Reproduce THEORY.md §9's silent *formatting* change (JEP 252, Use CLDR Locale Data by Default).

```bash
for p in CLDR COMPAT; do
  echo "== $p"
  java -Djava.locale.providers=$p -cp out LocaleDemo de-DE fr-FR tr-TR en-US
done
```

`LocaleDemo` prints `NumberFormat.getInstance(l).format(1234567.891)`,
`DateFormat.getDateInstance(SHORT, l).format(new Date(0))`, and
`"title".toUpperCase(l)` for each locale.

**Expected observation.** `tr-TR` is the reliable offender: `toUpperCase` yields
`TİTLE` under CLDR and `TITLE` under COMPAT (dotless-i). `de-DE`/`fr-FR`
differ in grouping separators, currency placement, and narrow-nbsp vs space.
`en-US` usually matches — which is why the bug survives a US-only test suite.

**Pass.** You can name the locale property that changed the behaviour and explain
why a test asserting *parsed values* rather than *formatted strings* would pass
on both JDKs and still let the bug reach a German invoice.

---

## 6. Compact object headers, on and off

**Goal.** Measure THEORY.md §25's memory-layout change with arithmetic, not
vibes.

```bash
java -XX:+PrintFlagsFinal -version | grep -iE 'compact|objectheader'
# with JOL on the classpath (org.openjdk.jol:jol-core):
java -XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders    -cp "out:jol-core.jar" -jar jol-cli.jar internals ObjectLayoutDemo
java -XX:+UnlockExperimentalVMOptions -XX:-UseCompactObjectHeaders   -cp "out:jol-core.jar" -jar jol-cli.jar internals ObjectLayoutDemo
```

`ObjectLayoutDemo` allocates 1,000,000 plain objects with two `int` fields and
prints `ClassLayout.parseInstance(new Node(1,2)).toPrintable()` plus
`Runtime.totalMemory() - usedBefore`.

**Expected observation.** The header shrinks from 12–16 bytes to a flat **8** —
a class-level header is stored once per class, not per object. For an object with
8 bytes of `int` fields the saving is large in *relative* terms (24 → 16 bytes,
33%); for a 200-byte object it is ~4% (216 → 208). JOL prints the two layouts
side by side and the `object size` line differs by **exactly 4 or 8 bytes** — not
16. If you measure 16, you have misread which header size you started from.

Two preconditions to check before you are surprised by no change: compressed
class pointers must be on, and the feature silently disables itself above an 8 TB
heap with any collector other than ZGC.

**Pass.** You can compute the whole-heap saving from your own live-object count
using MATH_FOUNDATION.md §2 and reconcile it with the measured `totalMemory`
delta. A number you cannot reconcile is not a result.

---

## 7. Virtual threads vs platform threads, observed

**Goal.** See the 21 concurrency change (THEORY.md §21) rather than read it.

```bash
java -cp out ThreadDemo platform 50000 &
PID=$!; sleep 3; jcmd $PID Thread.print | grep -c '^"'; jcmd $PID Thread.print | grep 'java.lang.Thread.State' | sort | uniq -c
java -cp out ThreadDemo virtual 50000 &
PID=$!; sleep 3; jcmd $PID Thread.print | head -30; jcmd $PID Thread.count   # JDK 21+
```

**Expected observation.** `Thread.print` on the platform version dumps 50,000
OS-nominal `java.lang.Thread` entries (this takes minutes and can exhaust the
terminal — cap it at 5,000 and say so). On the virtual version, `Thread.print`
shows a *small* number of platform threads — the scheduler/continuation carrier
threads plus the few real threads — while `Thread.count` reports ~50,000 virtual
threads and `VirtualThreadMountTable` is empty because nothing is mounted (all
parked on `Socket`).

**Pass.** You can explain why `Thread.print` shows so little for virtual threads
(that is the *design goal*: cheap, unmounted, pooled stacks) and state which
operations force a mount (`synchronized`, `Object.wait`, and a native/foreign
frame). That list is why `synchronized` is the migration's real work.

---

## 8. Trace a preview feature's whole lifecycle

**Goal.** Run a feature across two JDKs and see the preview mechanism from both
sides.

```bash
# JDK 21 — switch pattern matching, standard
cat > Pattern.java <<'EOF'
sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double s) implements Shape {}
public class Pattern {
    public static double area(Shape s) {
        return switch (s) { case Circle c -> Math.PI*c.r()*c.r();
                            case Square q -> q.s()*q.s(); };
    }
}
EOF
javac -d out21 Pattern.java && java -cp out21 Pattern

# JDK 17 — the same source is preview
javac --release 17 --enable-preview -d out17 Pattern.java
javap -v -cp out17 Pattern | grep -iE 'minor version|Preview'
java --enable-preview -cp out17 Pattern
```

**Expected observation.** On 17 you *must* pass `--enable-preview` to **both**
`javac` and `java`, and `javap -v` shows the class-file `minor version: 65535`
plus a `Preview` attribute — that is the mechanism that makes preview bytecode
refuse to load on the next JDK. On 21 the same source compiles with no flag.
Add a fourth line `case Object o -> -1;` to show that the sealed exhaustiveness
check (17+) replaced the `default:` branch that (a) pre-21 code required.

**Pass.** You can state the two rules — *same JDK for compile and run* and *never
ship preview* — and explain why the class-file minor-version trick is stronger
than a compiler warning. Then name a feature that failed those rules and was
killed: string templates.

---

## 9. Build the version-attribution table from `jshell`

**Goal.** Derive the timeline from the runtime instead of from memory, so you can
never get it wrong again.

```bash
for r in 8 11 17 21 25; do
  echo "== $r"; echo '
var rt = Runtime.version();
System.out.println(rt.feature() + " " + rt.version());
System.out.println("compactHeaders=" + System.getProperty("jdk.objmap.maxObjectHeaderSize"));
System.out.println("locales=" + java.util.Locale.getAvailableLocales().length);
System.out.println("charsets=" + java.nio.charset.Charset.defaultCharset());
' | jshell --execution local -q -
done
```

**Expected observation.** `feature()` returns 8/11/17/21/25; `defaultCharset()`
returns the platform charset pre-18 and `UTF-8` on 18+; the locale count jumps at
9 when CLDR becomes the default locale provider (JEP 252); the object-header-size
property is absent before 24/25 and present after.

**Pass.** You have a version/feature table with at least four columns (feature,
`runtime.version()`, `Runtime.Version`, and a probe result) that you generated,
cross-checked against <https://openjdk.org/jeps/0>. Then fill in FLASHCARDS.md
from *your table*, not from the internet.

---

## 10. GC differences from the logs

**Goal.** Reproduce THEORY.md's runtime-rebuild theme (CMS→G1→ZGC→Shenandoah) as
numbers.

```bash
java -Xmx2g -Xms2g -XX:+UseG1GC          -Xlog:gc*,gc+pause=info:file=gc-g1.log  -cp out AllocDemo
java -Xmx2g -Xms2g -XX:+UseZGC -Xlog:gc  -Xlog:gc+phases=info:file=gc-zgc.log        -cp out AllocDemo
java -Xmx2g -Xms2g -XX:+UseShenandoahGC   -Xlog:gc*,gc+pause=info:file=gc-shen.log  -cp out AllocDemo
grep -c 'Pause Young' gc-g1.log; grep -o 'gc,phases.*ms' gc-zgc.log | tail -5
awk '{print $NF}' gc-*.log | sort -n | tail -1
```

`AllocDemo` allocates 200 GB of short-lived objects over 30 s with a 2 GB live
set, forcing hundreds of collections.

**Expected observation.** G1 prints hundreds of `Pause Young (Normal) (G1 Evacuation
Pause) 12.345ms` lines — you *count* pauses. ZGC and Shenandoah print
sub-millisecond cycle lines and the total-pause arithmetic is entirely different:
their whole pitch is that pause count matters less than pause *distribution*.
Shenandoah, which is a concurrent compacting collector, shows the smallest pauses
on this allocation profile; ZGC's advantage grows with heap size, so **the ranking
changes when you move the `-Xmx`** — measure at 2 GB *and* at 32 GB.

**Pass.** You have three logs, a pause-count and worst-pause table, and a written
answer to "which collector would you pick for this workload and this heap size?"
with the number that drove it. Then apply MATH_FOUNDATION.md §3.