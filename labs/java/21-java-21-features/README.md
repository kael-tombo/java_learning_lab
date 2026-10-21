# Lab 21: Java 21 Features

## Overview

Java 21 (released September 2023) is a landmark LTS release that introduces several transformative features including Virtual Threads (Project Loom), Pattern Matching for switch, Record Patterns, Sequenced Collections, and Structured Concurrency (Preview). This lab provides a comprehensive exploration of these features, their motivations, usage patterns, and best practices.

### Key Features Covered

- **Virtual Threads**: Lightweight threads that dramatically simplify concurrent programming by allowing a million-thread scale without the overhead of OS platform threads.
- **Pattern Matching for switch**: Enhanced switch expressions and statements that allow pattern matching on type, enabling more expressive and safer code.
- **Record Patterns**: Deconstruction of record types directly in pattern matching, enabling nested pattern matching.
- **Sequenced Collections**: New interfaces (`SequencedCollection`, `SequencedSet`, `SequencedMap`) providing uniform access to first/last elements and reverse-order traversal.
- **String Templates (withdrawn)**: Template expressions that safely compose strings with embedded expressions. Previewed in JDK 21/22 (JEP 430/459) and withdrawn before JDK 23 — covered here historically; use `String.formatted` on current JDKs.
- **Structured Concurrency (Preview)**: Structured approach to concurrent programming that treats groups of related tasks as a single unit of work.

### Prerequisites

- Java 21 JDK installed (`java -version` should show 21 or later)
- Basic understanding of Java concurrency, collections, and switch statements
- Familiarity with records and sealed classes (covered in Labs 22 and 23)

### Lab Structure

Each feature is explored through theory, code examples, exercises, and quizzes. The lab is divided into 24 standard documentation files covering everything from mental models to performance analysis.

Let's begin exploring the future of Java programming.
