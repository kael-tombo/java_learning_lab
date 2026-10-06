# History of Sealed Classes

## Origins

Sealed classes were developed as part of Project Amber, the same project that produced records, pattern matching, and switch expressions.

### Early Proposals (2017-2019)
The concept of "sealed types" had existed in other languages (Scala's `sealed`, Kotlin's `sealed`, C#'s discriminated unions). In Java, the idea was discussed as early as 2011 in the context of switch expressions, but the concrete proposal emerged around 2017.

### Design Goals
Gavin Bierman and Brian Goetz led the design with these goals:
1. Support exhaustive pattern matching (primary motivation)
2. Allow API designers to control inheritance
3. Integrate with the module system
4. Be backward compatible with existing code

### Key Design Decisions
- **Name "sealed"**: Chosen over alternatives like "finalized" or "closed"
- **`permits` clause**: Explicit listing of permitted subtypes (rather than inferring from compilation unit)
- **Three subclass modifiers**: `final`, `sealed`, `non-sealed` for flexible hierarchy control
- **Module awareness**: Permitted subtypes can span packages within a module

## Preview Phases

### Java 15 (September 2020) — First Preview (JEP 360)
Sealed classes were introduced as a preview feature. The initial design required permitted subtypes to be declared in the same compilation unit or explicitly listed.

### Java 16 (March 2021) — Second Preview (JEP 397)
The second preview incorporated feedback including:
- More flexible syntax for permitted subtype declarations in the same file
- Refined rules for sealed classes and records interaction

### Java 17 (September 2021) — Finalized (JEP 409)
Sealed classes became permanent with no changes from the second preview. Java 17 was the first LTS release to include sealed classes (along with pattern matching for instanceof and the Java 17 LTS).

## Post-Finalization Evolution

### Java 17-21: Integration with Pattern Matching
Pattern matching for switch (finalized in Java 21) relies on sealed classes for exhaustiveness checking. The combination of `sealed` + `records` + `pattern matching` enables algebraic data type programming.

### Java 21: Record Patterns
Record patterns allow deconstructing sealed subtypes directly in pattern matching, completing the ADT picture.

## Timeline

| Version | Date | Feature | Status |
|---------|------|---------|--------|
| Java 15 | Sep 2020 | Sealed Classes (JEP 360) | Preview |
| Java 16 | Mar 2021 | Sealed Classes (JEP 397) | Second Preview |
| Java 17 | Sep 2021 | Sealed Classes (JEP 409) | Finalized |
| Java 17 | Sep 2021 | Switch pattern matching (JEP 406) | Preview |
| Java 21 | Sep 2023 | Pattern Matching for switch (JEP 441) | Finalized |

## Influences

- **Scala's sealed classes** (2004): The primary inspiration
- **Kotlin's sealed classes** (2016): Similar concept with record-style data classes
- **C# discriminated unions** (OneOf pattern)
- **Functional programming languages**: Haskell's algebraic data types, ML's datatype declarations
- **Java enums**: Sealed classes are "enums for types" — restricting variant values becomes restricting variant types

## Differences from Precursors

Compared to Scala's sealed classes:
- Java requires explicit `permits` clause; Scala infers sealed subtypes from the compilation unit
- Java allows `non-sealed` subtypes; Scala does not (all subtypes must be final)
- Java integrates with the module system; Scala's sealed works at package/file level
- Java's sealed can be applied to interfaces and classes; Scala's sealed applies only to classes and traits

## Ongoing Work

Future JEPs may extend sealed classes with:
- **Sealed enums**: Enum-like constructs with generic type parameters and per-constant state
- **Sealed patterns**: Pattern matching optimizations for sealed hierarchies
- **Broader sealed support**: Possibly extending to methods and fields
