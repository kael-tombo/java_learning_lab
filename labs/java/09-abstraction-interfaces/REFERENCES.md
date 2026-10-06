# Abstraction & Interfaces — References

## Official Documentation
- [Java Language Specification — Chapter 9: Interfaces](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html)
- [Java Language Specification — Chapter 8.1.1: Abstract Classes](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html)
- [Oracle Tutorial — Abstract Methods and Classes](https://docs.oracle.com/javase/tutorial/java/IandI/abstract.html)
- [Oracle Tutorial — Interfaces](https://docs.oracle.com/javase/tutorial/java/IandI/createinterface.html)

## Books
- *Effective Java* — Joshua Bloch (Items 19-22: Interfaces vs Abstract Classes)
- *Core Java Volume I* — Cay S. Horstmann (Chapter 6: Interfaces, Lambda, Inner Classes)
- *Design Patterns* — Gang of Four (Adapter, Facade, Proxy patterns)
- *Clean Architecture* — Robert C. Martin (Dependency Inversion Principle)

## JEPs
- JEP 255: Evolve the Language with Default Methods — Java 8
- JEP 218: Generic Overlays — Java 8 (the static-method half of interface evolution)
- JEP 360: Sealed Classes (Preview) — Java 15
- JEP 397: Sealed Classes (Second Preview) — Java 16
- JEP 409: Sealed Classes — Java 17

## Functional Interfaces
- `java.util.function` package docs
- [Baeldung — Functional Interfaces in Java](https://www.baeldung.com/java-8-functional-interfaces)
- [Baeldung — Lambda Expressions Guide](https://www.baeldung.com/java-8-lambda-expressions-tips)

## Deep Dive References
- [JLS §15.12.2.5 — Most-Specific Method Resolution](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html) — Default method ambiguity resolution
- [JEP 255: Evolve the Language with Default Methods](https://openjdk.org/jeps/255) — the specification for default methods (Java 8)
- [JEP 218: Generic Overlays](https://openjdk.org/jeps/218) — static interface methods (Java 8)
- [JEP 395: Records](https://openjdk.org/jeps/395) — Records and interfaces
- [Bridge Methods in the JVM](https://docs.oracle.com/javase/tutorial/java/generics/bridgeMethods.html) — Oracle tutorial on bridge methods
- [Lambda Metafactory JavaDoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/invoke/LambdaMetafactory.html) — Official API documentation

## Principles
- Dependency Inversion Principle
- Interface Segregation Principle
- Program to an Interface, Not an Implementation
