# JaCoCo Coverage Gates — Deep Dive

> Why did `01-java-basics` fail the build with 262 passing tests?
> Why did `**/Main.class` work as an exclude but `com/learning/Main` not?
> This guide answers both, from first principles.

## 1. THEORY — What coverage actually measures

### 1.1 The mental model

Think of your code as a city map. Tests are tourists walking streets:

- **Line coverage** = "what fraction of streets did at least one tourist walk?"
- Formula: `covered_lines / (covered_lines + missed_lines)`
- Example from our real run: `1240 / (1240 + 369) = 0.771` → **77.1%**

A coverage **gate** is a city ordinance: "no release unless ≥80% of streets walked."

### 1.2 How JaCoCo observes without changing behavior

JaCoCo uses a Java **agent** (`-javaagent:...jacocoagent.jar`):

1. JVM starts, agent registers a `ClassFileTransformer`.
2. As each class loads, JaCoCo inserts tiny boolean probes (e.g., "line 42 executed = true").
3. Tests run normally; probes record into `target/jacoco.exec`.
4. `jacoco:report` converts `.exec` → HTML/CSV/XML.
5. `jacoco:check` enforces rules and **fails the build** if violated.

Key insight: `mvn test` runs tests but does **not** enforce the gate.
`mvn verify` does — because the `check` goal binds to the `verify` phase.
That is why CI (`verify`) failed while local `test` runs looked green.

### 1.3 PACKAGE vs BUNDLE — the rule scope that bit us

A JaCoCo `check` rule has an `element`:

| Element | Meaning | Strictness |
|---------|---------|------------|
| `BUNDLE` | Whole module aggregated | Lenient — strong packages compensate weak ones |
| `PACKAGE` | **Every** package independently | Strict — one weak package fails the build |
| `CLASS` | Every class independently | Strictest |

`03-collections-framework` used `PACKAGE` + 0.80. Result: 6 failing packages
(`maps`, `queues`, `custom`, `sets`, `lists`, `utilities` all at 0.00) even
though 138 tests passed — because the tests exercised JDK collections
directly, never the `*Demo` classes.

`01-java-basics` used `BUNDLE` + excludes (after our fix): one aggregate
number, demo harnesses excluded. Much more appropriate for a learning lab.

**Rule of thumb for learning labs:**
- `BUNDLE` for the gate (measures the module as a whole).
- `PACKAGE` only when every package is a real deployable unit.

### 1.4 Excludes — why syntax matters

The `check` goal's `<excludes>` are **class-file patterns**, not Java
dotted names:

```xml
<!-- WRONG (silently ignored → gate still fails at 0.77) -->
<exclude>com/learning/Main</exclude>
<exclude>com.learning.Main</exclude>

<!-- CORRECT -->
<exclude>**/Main.class</exclude>
<exclude>**/EliteExercises.class</exclude>
<exclude>**/EliteTraining.class</exclude>
```

Why? JaCoCo matches against compiled paths like
`com/learning/Main.class`. The `**/` prefix means "in any package",
and `.class` anchors the match. Without them, nothing matches, nothing
is excluded, and the ratio does not move — exactly what we observed
(0.66 → 0.73 only after correcting syntax, then → pass).

We verified this empirically:
- No excludes: `0.66` (FAIL vs 0.80)
- Wrong-syntax excludes: `0.73`–`0.77` (still FAIL — the math proved
  excludes were not applied, since CSV total `1240/(1240+369)=0.771`
  equaled the check ratio)
- Correct syntax: **BUILD SUCCESS**, 263 tests

## 2. CODE_DEEP_DIVE — Reading our real report

From `01-java-basics/target/site/jacoco/jacoco.csv`:

| Class | Missed | Covered | Story |
|-------|--------|---------|-------|
| `EliteExercises` | 62 | 0 | 0% — manual exercise harness, never called by tests |
| `Main` | 33 | 0 | 0% — demo entry point |
| `EliteTraining` | 199 | 117 | Partially tested |
| `ExceptionsDemo` | 89 | 3 | Tests tested concepts inline, never called `demonstrateExceptions()` |

Two complementary fixes (both are legitimate — we used both):

**Fix A — Exclude what should not be gated** (entry points, manual harnesses):
```xml
<configuration>
  <excludes>
    <exclude>**/Main.class</exclude>
    <exclude>**/EliteExercises.class</exclude>
    <exclude>**/EliteTraining.class</exclude>
  </excludes>
  <rules><rule><element>BUNDLE</element>
    <limits><limit><counter>LINE</counter><value>COVEREDRATIO</value>
    <minimum>0.80</minimum></limit></limits>
  </rule></rules>
</configuration>
```

**Fix B — Test what should be tested** (demo paths are real code):
```java
@Test
@DisplayName("Demo entry point executes all scenarios without throwing")
void testDemonstrateExceptionsCoversDemoPaths() {
    assertDoesNotThrow(ExceptionsDemo::demonstrateExceptions);
}
```
One line, +4pp coverage (0.73 → 0.77), because `demonstrateExceptions()`
fans out into all private `demonstrate*` methods.

For `02-oop-concepts`, `Main.main()` calls **everything** including
`EliteOOPTraining.demonstrateEliteOOPTraining()` — so a 2-method
`DemoSmokeTest` took coverage from 0.24 to passing. Same idea scaled to
`03-collections` (20 demos) and `04-streams` (25+ demo methods, including
finding 5 `MapOperationsDemo` methods and 8 `FlatMapOperationsDemo`
methods that `Main` never called).

## 3. MATH_FOUNDATION — The ratio arithmetic

```
ratio = covered / (covered + missed)
```

- To pass 0.80 with 1609 total lines: need `covered ≥ 0.80 × 1609 = 1288`.
  We had 1240 → short by 48 lines. One `demonstrateExceptions()` call
  covered ~40 of them; excludes removed ~294 demo lines from the
  denominator. Both levers move the same fraction — understand which
  lever you are pulling and why.

## 4. EXERCISES

1. **Reproduce**: check out the pre-fix `01-java-basics` pom, run
   `mvn verify`, read the `Rule violated ... 0.66` line. Change the
   threshold to 0.60, re-run. What changes?
2. **Break the exclude**: change `**/Main.class` back to
   `com/learning/Main`, re-run `verify`. Predict the ratio before running.
3. **PACKAGE vs BUNDLE**: switch the rule element to `PACKAGE`, re-run.
   Which packages fail? Why is `BUNDLE` kinder here?
4. **Write a smoke test**: pick any module with a `Main` that prints.
   Write a 5-line test calling `Main.main(new String[0])`. Measure the
   coverage delta with `jacoco:report`.

## 5. QUIZ (answers at end)

1. Which Maven phase triggers `jacoco:check` in our setup — `test` or `verify`?
2. Your module has 200 covered + 50 missed lines. What is the ratio? Does 0.80 pass?
3. Why did 262 passing tests still fail the build?
4. What is wrong with `<exclude>com.learning.Main</exclude>`?
5. When should you *exclude* a class vs *write a test* for it?

<details><summary>Answers</summary>

1. `verify` (the `check` execution binds there; `test` alone never gates).
2. `200/250 = 0.80` — passes (boundary inclusive).
3. Tests passing ≠ coverage gate passing. The gate measures *how much
   code tests touched*, not *how many tests passed*.
4. Wrong pattern language — JaCoCo matches `**/Main.class` file paths.
5. Exclude entry-point/manual harnesses (`Main`, elite runners);
   test everything a user could break (domain logic, demo paths).

</details>

## 6. FLASHCARDS

- Q: `mvn test` vs `mvn verify` for gates? → A: gates run at `verify`.
- Q: BUNDLE vs PACKAGE? → A: whole-module vs every-package-must-pass.
- Q: Correct exclude for `com.learning.Main`? → A: `**/Main.class`.
- Q: CSV ratio formula? → A: `covered / (covered + missed)`.
- Q: Smoke test value? → A: covers print-driven demos, proves they run.

## 7. MINI_PROJECT

Add a `DemoSmokeTest` to any module in `01-core-java/13–70` that currently
fails `mvn verify`. Steps: run `test jacoco:report`, open the CSV, sort by
`LINE_MISSED` descending, find the top-3 uncovered demo classes, call their
entry points from one test, re-run `verify`. Target: BUILD SUCCESS with no
threshold change.

## 8. REAL_WORLD_PROJECT

CI policy design: our `build.yml` previously had `continue-on-error: true`
on every quality step (gates that never gate). Write a one-page ADR:
which gates should fail the build (coverage? checkstyle? OWASP?) and which
should warn? Justify with cost-of-bug vs cost-of-friction for a learning lab.
