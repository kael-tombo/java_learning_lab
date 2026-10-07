# References: Sealed Classes

## Official Documentation

- **JEP 409: Sealed Classes** - https://openjdk.org/jeps/409
- **JEP 397: Sealed Classes (Second Preview)** - https://openjdk.org/jeps/397
- **JEP 360: Sealed Classes (First Preview)** - https://openjdk.org/jeps/360
- **Java Language Specification, SE 17 Edition** - Chapter 8.1.1.2: Sealed Classes
- **Class.isSealed()** - Java SE 17 API Documentation
- **Class.getPermittedSubclasses()** - Java SE 17 API Documentation

## Books

- *Modern Java in Action* by Raoul-Gabriel Urma — Sealed classes and pattern matching
- *Effective Java* (3rd Edition) by Joshua Bloch — Updated with sealed class best practices
- *Java 17 in Action* by Nicolai Parlog — Sealed classes in the context of Java 17 LTS
- *The Java Language Specification, Java SE 17 Edition* — Official language reference

## Articles

- **"Sealed Classes in Java 17"** by Brian Goetz — Oracle blog
- **"The State of the Java Type System: Sealed Classes"** by Nicolai Parlog — Java Magazine
- **"Understanding Sealed Classes in Java"** by Baeldung
- **"Algebraic Data Types in Java with Sealed Classes"** by InfoQ
- **"Sealed Classes: A New Tool for API Design"** by Gavin Bierman
- **"Pattern Matching and Sealed Classes"** by José Paumard

## Conference Talks

- **"Java 17: Sealed Classes and Pattern Matching"** by Gavin Bierman — Oracle Dev Live
- **"Sealed Types in Java"** by Brian Goetz — JVM Language Summit
- **"Algebraic Data Types in Java"** by Stuart Marks — Devoxx
- **"The Future of Java Type System"** by Nicolai Parlog — JPoint

## Online Resources

- **Oracle Java Tutorials: Sealed Classes** - https://docs.oracle.com/javase/tutorial/java/records/
- **Baeldung: Java Sealed Classes Guide** - (link removed)
- **Dev.java: Sealed Classes** - Oracle's interactive tutorial
- **OpenJDJ Amber Project** - https://openjdk.org/projects/amber/
- **Java Specification Requests** - JSR 397 (Sealed Classes)

## Related JEPs

- JEP 360: Sealed Classes (Preview, Java 15)
- JEP 397: Sealed Classes (Second Preview, Java 16)
- JEP 409: Sealed Classes (Java 17 — Finalized)
- JEP 395: Records (Java 16)
- JEP 406: Pattern Matching for instanceof (Preview, Java 17)
- JEP 441: Pattern Matching for switch (Java 21)

## Library and Framework Support

- **Jackson** — Supports sealed hierarchies for polymorphic deserialization
- **Gson** — RuntimeTypeAdapterFactory for sealed types
- **Lombok** — @Builder works with sealed hierarchy subtypes
- **Spring** — Sealed types in configuration properties and event handling
- **Micronaut** — Sealed types for HTTP client error handling

## Tools

- **IntelliJ IDEA** — Sealed hierarchy visualization, "Add missing cases" quick fix
- **Eclipse** — Type hierarchy view for sealed types
- **OpenJDJ javac** — Compiler with sealed class support
- **ASM/ByteBuddy** — Bytecode manipulation respecting sealed constraints

## Community Resources

- **Stack Overflow** — [sealed-class] tag
- **r/java** on Reddit — Sealed class discussions
- **Java Discord** — #sealed-classes channel
- **OpenJDK amber-dev mailing list** — Design discussions

## Academic References

- *"Algebraic Data Types for Object-Oriented Languages"* — Research paper
- *"Featherweight Java with Sealed Types"* — Formal type system specification
- *"Type-Based Exhaustiveness Checking for Sealed Types"* — Compiler verification techniques
