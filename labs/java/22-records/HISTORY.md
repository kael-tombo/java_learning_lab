# History of Records in Java

## Origins: Project Amber

Records were developed as part of **Project Amber**, an OpenJDK project focused on productivity-oriented features. The project also produced local-variable type inference (`var`), enhanced enums, pattern matching, and switch expressions.

### Early Discussions (2016-2018)
The concept of "data classes" or "value types" had been discussed in Java for over a decade. Early proposals included:
- **JEP 169: Valhalla / Larval State for Value Objects** — an exploration of value types in the JVM (today tracked as JEP 401, Value Objects)
- **Project Valhalla** — Value types for the JVM (still in development)
- **Project Amber** — Focused on more approachable features with shorter timelines

### Design Phase (2018-2019)
Brian Goetz led the design of records as a simpler alternative to full value types. Key design decisions included:
- **Name "record"** — Chosen over "data class" or "tuple" to emphasize their role as records of state
- **Compact syntax** — `record Name(components)` rather than more verbose alternatives
- **No extends clause** — Records cannot extend other classes (they implicitly extend `java.lang.Record`)
- **No extends restriction on interfaces** — Records can implement interfaces
- **Immutability** — Components are `private final` fields

## Preview Phases

### Java 14 (March 2020) — First Preview (JEP 359)
Records were introduced as a preview feature. Developers could experiment with them using `--enable-preview`. The reception was overwhelmingly positive, with the main feedback being:
- Request for local records (records inside methods)
- Clarification on serialization behavior
- Refinements to the annotation model

### Java 15 (September 2020) — Second Preview (JEP 384)
The second preview incorporated feedback:
- Added support for local records
- Refined the API for `Record` components
- Clarified serialization rules
- Added `isRecord()` to `Class`

### Java 16 (March 2021) — Finalized (JEP 395)
Records became a permanent, production-ready feature with no changes from the second preview. This was a remarkably short incubation for a major language feature (2 preview phases, ~12 months), reflecting the community's strong support and the design's maturity.

## Post-Finalization Evolution

### Java 17 — Sealed Classes
Records and sealed classes together enable algebraic data type programming. A sealed hierarchy with record implementations provides sum types (sealed interface) with product types (records).

### Java 19-21 — Record Patterns
Java 19 previewed record patterns (JEP 405), which were finalized in Java 21 (JEP 440). This completed the records vision: not only can you declare data carriers concisely, but you can also destructure them in pattern matching.

### Ongoing Work
- **Unnamed patterns** (Java 22+): Allow `case Point(var x, var _)` to ignore components
- **Value types**: Project Valhalla's value types may eventually allow records to be flattened in memory
- **Primitive records**: Future JEPs may allow records with primitive components for better memory layout

## Timeline Summary

| Version | Date | Feature | Status |
|---------|------|---------|--------|
| Java 14 | Mar 2020 | Records (JEP 359) | Preview |
| Java 15 | Sep 2020 | Records (JEP 384) | Second Preview |
| Java 16 | Mar 2021 | Records (JEP 395) | Finalized |
| Java 17 | Sep 2021 | Sealed Classes | Finalized |
| Java 19 | Sep 2022 | Record Patterns (JEP 405) | Preview |
| Java 21 | Sep 2023 | Record Patterns (JEP 440) | Finalized |

## Influences

Records were influenced by:
- **Case classes** in Scala
- **Data classes** in Kotlin
- **Tuples** in Python, C#, and TypeScript
- **Algebraic data types** in Haskell, ML, and other functional languages
- **Lombok's @Data** and @Value annotations
- **JavaBeans convention** (the pattern records aim to improve)

Java's records deliberately avoided some features of these predecessors, such as multiple constructors (Scala case classes have an `apply` method in a companion object) and mutable components (Kotlin data classes can have `var` components). This reflects Java's design philosophy of doing fewer things with more discipline.
