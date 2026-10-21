# History of Java 21 Features

## Virtual Threads (Project Loom)

### Origins (2017-2019)
Project Loom was formally proposed by Ron Pressler and Alan Bateman in 2017 as OpenJDK project "Loom." The goal was to add lightweight user-mode threads to the JVM. Early prototypes explored three approaches: continuations-as-library, bytecode rewriting, and JVM-level continuations.

### Preview Phases (2020-2023)
- **Java 19 (Sep 2022)**: Virtual Threads preview (JEP 425)
- **Java 20 (Mar 2023)**: Second preview with refinements to API
- **Java 21 (Sep 2023)**: Finalized as production feature (JEP 444)

Key design decisions during incubation included:
- Virtual threads use `Thread` API, not a separate class (seamless migration)
- Platform threads renamed to "carrier threads" for clarity
- Pinning scenarios (synchronized blocks, native frames) were documented rather than eliminated

## Pattern Matching for switch

### Precursors (Java 16-17)
- **Java 16**: Pattern matching for `instanceof` (JEP 394, finalized)
- **Java 17**: Sealed classes (JEP 409), enabling exhaustive switch

### Evolution (Java 17-21)
- **Java 17**: Pattern matching for switch (JEP 406, preview)
- **Java 18**: Second preview (JEP 420) with refinements
- **Java 19**: Third preview (JEP 427) adding record patterns
- **Java 20**: Fourth preview (JEP 433) with pattern dominance checking
- **Java 21**: Finalized (JEP 441) including record patterns

The four-preview evolution shows the complexity of getting pattern matching right. Early feedback led to changes in how nulls are handled (the `null` case), dominance rules, and exhaustiveness checking.

## Record Patterns

Closely tied to pattern matching, record patterns evolved alongside switch patterns. Java 16 introduced records (JEP 395). Java 19 previewed record patterns (JEP 405). Java 21 finalized them (JEP 440, separate from switch patterns JEP 441).

## Sequenced Collections

- **2015**: Initial proposal by Stuart Marks
- **2021**: Draft JEP for Sequenced Collections (JEP 431)
- **Java 21**: Finalized (JEP 431)

The long gestation (8 years from proposal to delivery) reflects the challenge of adding interfaces to the existing collection hierarchy without breaking backward compatibility.

## String Templates

- **Java 21 (Preview)**: JEP 430 — String Templates
- **Java 22 (Second Preview)**: JEP 459 — refined but still under review
- **Java 23**: Withdrawn — the experts group declined to continue the preview

The feature built on Java's experience with `MessageFormat`, `String.format`, and external template engines (JSP, Thymeleaf, etc.), but after two preview rounds the experts group declined to continue the preview and the feature was discontinued wholesale. It is not part of any shipping JDK today; `String.formatted` remains the standard tool for interpolation.

## Structured Concurrency

- **Java 19 (Preview)**: JEP 428 — Structured Concurrency (Incubator)
- **Java 20 (Preview)**: Second preview with refinements
- **Java 21 (Preview)**: Third preview (JEP 453)

Structured Concurrency remains in preview in Java 21, reflecting the ongoing work to integrate it with virtual threads and the rest of the concurrency ecosystem.

## Release Context

Java 21 is an LTS release (every two years since Java 17). Its feature set represents a culmination of several multi-year projects. The table below shows the incubation path:

| Feature | First Preview | Finalized In | Total Preview Phases |
|---------|---------------|-------------|---------------------|
| Virtual Threads | Java 19 | Java 21 | 2 |
| Pattern Matching for switch | Java 17 | Java 21 | 4 |
| Record Patterns | Java 19 | Java 21 | 2 |
| Sequenced Collections | Java 21 (direct) | Java 21 | 0 |
| String Templates | Java 21 | Withdrawn before Java 23 (finalized: none) | 2 |
| Structured Concurrency | Java 19 | Preview | Ongoing |
