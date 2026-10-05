# MINI_PROJECT — Java Version Compatibility Analyzer

Two weeks. Build **`vca`** — a tool that scans a Java source tree and reports
which language and library features it actually uses, the minimum `--release` it
needs, and — the part that is genuinely hard — what it will *behaviourally*
sensitive to when that release changes.

The deliverable is a working jar plus an honesty about its limits. A tool that
reports "needs 16" for code that only works on 21 because of a preview-era API is
worse than no tool.

## Requirements

1. `java -jar vca.jar <path>` prints a per-file table of detected features with
   the version that introduced each.
2. A single-line minimum `--release` verdict, computed as the **max** of all
   detected feature floors — not a guess, not the highest file number.
3. Distinguishes three feature classes: **language** (`record`, text block,
   `switch` expression, pattern matching), **library** (`HttpClient`, `List.of`,
   `Files.readString`), and **preview**.
4. Detects behavioural exposure and reports it separately: unguarded default
   charset, `Locale`-sensitive formatting, `HashMap`/`Set` iteration order
   dependence, platform-charset round-trips.
5. Exit codes: `0` clean, `1` findings, `2` the tree could not be parsed
   (report which file — do not crash).
6. Detects *removals* too: `javax.xml.bind`, `sun.misc.*`, `SecurityManager`,
   `finalize()`.
7. Handles both `.java` files and a directory walk; ignores `target/`, `build/`,
   `node_modules/`, and generated sources under `META-INF`.
8. Tolerates source it cannot fully parse: reports the file as `UNPARSED` and
   continues. **Total failure on one bad file is the standard failure mode of
   this kind of tool and it is what you are being graded against.**
9. Unit tests for each rule, with at least one negative case per rule.
10. A `README.md` stating the tool's known limits, in particular: it does not
    inspect **compiled dependencies**, so it cannot see the Java 17-era API a jar
    on the classpath calls. Cross-reference `jdeps` for that half.
11. Runtime: a 20,000-file tree in under 30 s single-threaded.

## Design constraints

**Do not use the JavaParser library.** Parse with the JDK's own
`com.sun.source.tree` API (`ToolProvider.getSystemJavaCompiler()`, a
`TaskListener`, and `Trees`) so the tool runs on any JDK without a shading
dependency. This is the version-history point of the project: *the JDK ships a
parser*, and reaching for a third-party one hides a real capability.

**The hard part is the floor, not the detection.** Detection is a lookup table.
The floor is a max-reduction over a tree where **the maximum is a compatibility
promise to consumers you do not control** — so the tool must be conservative:

- One occurrence of `record` means the tree needs 16. It does **not** mean the
  tree is 16-*ready* (see requirement 4).
- A detected feature in a file excluded from the build (a `@Deprecated` profile,
  a commented-out test) still counts, unless you can prove exclusion. Default to
  counting.
- Library detection must key on the **resolved** type, not the string
  `java.net.http`. `"java.net.http.HttpClient"` in a comment is not a dependency.

## Phased plan

### Days 1–2 — Parser skeleton and file walk

```java
JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
StandardJavaFileManager fm = compiler.getStandardFileManager(null, null, StandardCharsets.UTF_8);
JavacTask task = (JavacTask) compiler.getTask(null, fm, diagnostics,
        List.of("-proc:none"), null, fm.getJavaFileObjects(files));
task.setTaskListener(new TaskListener() { ... collect CompilationUnitTree ... });
```

Wrap the walk in try/catch and count failures explicitly.

**Deliverable:** `vca parse <dir>` prints files parsed, files unparsed, and total
time. If unparsed is non-zero you have already found the tool's hardest case.

### Days 3–4 — The rule engine

One rule per feature, each a pure function from a `CompilationUnitTree` to a list
of `(feature, introducedIn, file, line)`:

```java
record Finding(String feature, int since, Kind kind, String file, int line) {}
enum Kind { LANGUAGE, LIBRARY, PREVIEW, REMOVED, BEHAVIOURAL }
```

Rules to write first (they are also the quiz answers): records, text blocks,
`switch` expressions, pattern matching, sealed types, `var`, lambdas,
`List.of`/`Map.of`, `Optional`, `Stream`, `HttpClient`, `Files.readString`,
modules. Table-driven where possible:

```java
Map<String, Integer> LIBRARY_FLOORS = Map.ofEntries(
    Map.entry("java.net.http.HttpClient", 11),
    Map.entry("java.util.stream.Stream",  8),
    Map.entry("java.util.Optional",      8),
    Map.entry("java.time",               8),
    Map.entry("java.nio.file.Files#readString", 11));
```

**Deliverable:** `vca features <dir>` — the per-file table, sorted by version.

### Days 5–6 — Floor reduction and exit codes

```java
int floor = findings.stream().filter(f -> f.since() > 0).mapToInt(Finding::since).max().orElse(1);
int withPreview = findings.stream().anyMatch(f -> f.kind() == Kind.PREVIEW)
        ? floor + 1 : floor;      // and require --enable-preview regardless
```

Be explicit that a preview floor is **not** a release number: report
`--release <n> --enable-preview` and warn that the code will not load on any
other JDK.

**Deliverable:** the one-line verdict plus exit codes 0/1/2, tested against a tree
you deliberately broke.

### Days 7–8 — Behavioural exposure

The four detectors from THEORY.md, each a **separate section** in the report:

```bash
grep -rn 'new String(' --include='*.java' . | grep -v Charset   # JDK 18 class
grep -rn 'String.format(' --include='*.java' . | grep -v Locale   # JDK 9 class
grep -rn 'for (.* : .*HashMap\|entrySet()' --include='*.java' .   # JDK 8 order class
grep -rn 'getBytes()\|new FileReader\|new FileWriter' --include='*.java' .
```

These are **not** version floors. Report them as `BEHAVIOURAL` with the version
that changed the behaviour, and never fold them into the `--release` number — a
tool that confuses the two is the failure this whole lab exists to prevent.

**Deliverable:** a report where a reader can tell in one glance what will *break
loudly* versus what will *corrupt quietly*.

### Days 9–10 — Removals and preview detection

Removals (`javax.xml.bind`, `javax.activation`, `sun.misc.Unsafe`,
`SecurityManager`, `finalize()`, `Class.newInstance`) get `Kind.REMOVED` and a
"removed in" version, which is the *inverse* of the normal mapping — 11 removed
JAXB while 11 added `HttpClient`, so a single `since` integer cannot express both.
Model it explicitly.

Preview detection: recognise the syntactic shapes that were preview (string
templates `STR."..."`, unnamed patterns `_`, primitive patterns) and report them
with a warning that the feature may be withdrawn.

**Deliverable:** the `REMOVED` and `PREVIEW` sections, each with a
known-real-world example.

### Days 11–12 — Performance, packaging, tests

Stream the directory walk with `Files.walk` and a bounded queue; parse file
batches rather than one-at-a-time so the compiler's initialisation is amortised.
Package with `maven-shade-plugin` (or a plain `jar` with a `Main-Class` manifest
if you want to avoid the plugin).

```bash
java -jar target/vca.jar ../java_learning_lab/labs/java   # 20k-file smoke test
time java -jar target/vca.json --format=json .           # machine-readable output
```

**Deliverable:** under 30 s on 20,000 files, JSON output for CI use.

### Days 13–14 — Limits document and demo

Write the section that makes the tool trustworthy: **what it cannot see**.
Compiled dependencies. Reflection. Generated code. Commented-out code. Files not
on the compile path. Cross-reference `jdeps --jdk-internals` and Animal Sniffer
for the dependency half, and say plainly which half of the compatibility problem
this tool addresses.

Then run it on three trees: your own lab sources, a JDK-8-era sample, and your
project. Report whether its verdict matched reality on all three.

**Deliverable:** `README.md` with a limits section, a worked example on three
trees, and the one case where it was wrong.

## Rubric (100 points)

| # | Criterion | Pts | Full marks |
|---|---|---|---|
| 1 | Parser uses `com.sun.source` and survives bad input | 12 | Runs on any JDK, no third-party parse dep; `UNPARSED` reported, never a crash |
| 2 | Feature detection accuracy | 15 | Each rule has a positive **and** a negative test; string-matching false positives (comments, string literals) rejected |
| 3 | Floor reduction is conservative and justified | 12 | Max-reduction over the whole tree; excluded files handled explicitly; the choice documented |
| 4 | Language vs library vs preview classification | 8 | Three categories distinguishable; preview never silently folded into a release |
| 5 | Removals handled as the inverse mapping | 8 | `javax.xml.bind` = removed in 11 *and* `HttpClient` = added in 11 both reported |
| 6 | Behavioural detectors, reported separately | 12 | All four classes; never folded into the `--release` number |
| 7 | Exit codes and machine-readable output | 6 | 0/1/2 correct; `--format=json` validates |
| 8 | Performance on 20k files | 8 | Under 30 s; measured and reported, not estimated |
| 9 | Tests | 8 | One positive + one negative per rule; `mvn test` green |
| 10 | Limits documented honestly | 11 | Names what it cannot see (dependencies, reflection, generated code) and points at `jdeps`/Animal Sniffer for the rest |

**Deductions.** −10 for folding `BEHAVIOURAL` findings into the `--release`
verdict. −8 for crashing on an unparseable file. −5 for a rule that matches raw
source text without checking it is real code. −5 for an undocumented third-party
parser dependency. −5 for a limits section that claims more than the tool does.

**Done when.** Criterion 1 and criterion 10 are all-or-nothing. A tool that
crashes on one bad file, or that overstates its coverage, has moved the risk from
the code to the reader of the report — which is worse than having no tool.