# Java Migration — java-migration

> Hands-on lab: migrating real codebases from legacy Java to modern JDKs (8 → 17 → 21/25) without breaking production.

## Why this lab exists

Most production Java estates are not on the latest JDK. They sit on 8 or 11 for
good commercial reasons, accumulate technical debt, and eventually *must* move —
because of a support-policy deadline, a container base-image change, a security
advisory, or a new library that dropped compatibility.

Migrating is not "change the compiler flag." It is a compatibility project with
three distinct surfaces:

1. **Source compatibility** — does it still compile?
2. **Binary compatibility** — do old jars still link?
3. **Behavioural compatibility** — does it still do the same thing?

The third is where migrations actually fail. `String.hashCode()` semantics,
`Collection` iteration order, reflection access under JPMS, and `sun.misc.Unsafe`
usage all shift between releases in ways that pass every test and still corrupt
production data.

## Objectives

- Classify a codebase's Java-version blockers into a typed inventory.
- Build a compile-first migration pipeline with an explicit risk ledger.
- Execute behavioural de-risking for the four highest-risk change classes.
- Plan a staged canary rollout with rollback that does not require a redeploy.
- Measure migration outcome with concrete before/after signals.

## Layout

| File | Purpose |
|---|---|
| `VISION.md` | Career framing, mental models, decision framework |
| `THEORY.md` | Compatibility surfaces, JEP lineage, migration mechanics |
| `EXERCISES.md` | 10 hands-on migration exercises |
| `QUIZ.md` | 20 self-check questions with answers |
| `FLASHCARDS.md` | 80 rapid-review cards |
| `MATH_FOUNDATION.md` | Risk scoring, effort estimation, rollout math |
| `CODE_DEEP_DIVE.md` | Annotated before/after migration diffs |
| `MINI_PROJECT.md` | 2-week legacy-app migration |
| `REAL_WORLD_PROJECT.md` | Full production JDK 8 → 21 migration |

## Prerequisites

- JDK 21 and JDK 25 installed side by side (`java -version`).
- Maven 3.9+ and Gradle 8+.
- A scratch Git repo for the migration exercises.
- Reading `labs/java/java-version-history/THEORY.md` first is strongly recommended.

## Quickstart

```bash
cd labs/java/java-migration

# Compile an 8-era source tree against a modern JDK
javac --release 8 -d out src/main/java

# See what modern compilation would reject
javac --release 17 -Xlint:all -d out src/main/java

# Produce a migration-relevant API surface scan
jdeps --jdk-internals -R target/your-app.jar
```

`jdeps --jdk-internals` is the single highest-value first command in any JDK
migration. It lists every internal-API dependency that will be removed.

## How to use

1. Read `labs/java/java-version-history/THEORY.md` for the version timeline.
2. Read `THEORY.md` here for the three compatibility surfaces.
3. Run Exercises 1–5 (the inventory + compile pipeline).
4. Run Exercises 6–10 (behavioural de-risking).
5. Attempt `MINI_PROJECT.md`.
6. Take `QUIZ.md` (aim 16/20).
7. Work `REAL_WORLD_PROJECT.md` as the capstone.

## Done when

- You can run `jdeps --jdk-internals` and classify every finding.
- You can name the four behavioural risks and write a test that catches each.
- You have a canary/rollback plan that does not require a rebuild.
- You can defend the JDK choice to a skeptical platform team.