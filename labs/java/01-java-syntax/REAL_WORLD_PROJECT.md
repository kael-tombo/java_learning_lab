# REAL-WORLD PROJECT — Java Syntax: Build Breaks on Release Night

## Incident Scenario
Friday 18:20 — release pipeline red. `javac` fails on `OrderService.java` only in CI; works on dev laptop. On-call pages build owner. Artifact blocked, hotfix train waiting.

## Symptoms
- CI log: `cannot find symbol: class Money`, `package com.acme.money does not exist`.
- Local `mvn compile` green; CI uses raw `javac` script.
- Recent PR added `com.acme.money.Money` + wildcard imports; file named `money.java` (lowercase) on a case-insensitive Mac.

## Investigation Tasks
1. Reproduce: `javac -d out $(find src -name "*.java")` vs IDE build; capture exact errors.
2. Inspect: `ls src/com/acme/money/`, check filename case vs class name; `git status` for untracked files (IDE hid the issue).
3. Classpath: `echo $CLASSPATH`, `javac -verbose` to see sourcepath resolution; confirm CI script omits new package dir.
4. Hygiene: `grep -rn "import com.acme.money.\*" src/`; compile with `-Werror -Xlint:all`.
5. Tooling: `jcmd <pid> VM.class_hierarchy` on running old jar to prove stale class still loaded (red herring check); collect CI compiler log artifact.

## Root Cause
Case-mismatched filename + missing sourcepath entry in CI `javac` script + wildcard import masking the gap locally (IDE auto-added dependency). Not a language bug — a build-contract breach.

## Resolution
- Immediate: rename to `Money.java`, add explicit `import com.acme.money.Money;`, fix CI script source glob; green build in 20 min.
- Short-term: replace script with Maven/Gradle wrapper; add `package-info.java`; forbid wildcards via Checkstyle `AvoidStarImport`.
- Long-term: CI `javac -Werror` gate + filename-vs-class check in pre-commit; reproducible container builder image.

## Runbook (next time)
```
1. Save full javac log (artifact).
2. Repro with same JDK: java -version + javac -verbose.
3. Check filename case + package-dir match.
4. Verify sourcepath/classpath in CI script.
5. Fix, rebuild clean (rm -rf out), tag.
```

## Metrics
- MTTR < 30 min; build repro rate 100%; zero wildcard imports (lint); CI/local JDK skew = 0 (toolchains file).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Java compilation & packages: https://docs.oracle.com/javase/tutorial/java/package/packages.html
- javac tool reference: https://docs.oracle.com/en/java/javase/21/docs/specs/man/javac.html
