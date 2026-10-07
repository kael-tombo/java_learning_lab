# Inheritance — References

## Official Documentation
- [Java Language Specification — Chapter 8.4: Inheritance](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html)
- [Oracle Tutorial — Inheritance](https://docs.oracle.com/javase/tutorial/java/IandI/index.html)
- [Java SE Docs — java.lang.Object](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)

## Books
- *Effective Java* — Joshua Bloch (Items 10-14: Overriding equals/hashCode/toString; Items 19-20: Inheritance design)
- *Core Java Volume I* — Cay S. Horstmann (Chapter 5: Inheritance)
- *Design Patterns* — Gang of Four (Template Method, Factory Method)
- *Head First Design Patterns* — Freeman & Robson

## Articles
- [Baeldung — Inheritance in Java](https://www.baeldung.com/java-inheritance)
- [Baeldung — Guide to equals() and hashCode()](https://www.baeldung.com/java-equals-hashcode-contracts)
- Baeldung — Composition vs Inheritance

## JEPs
- JEP 397: Sealed Classes (Second Preview) — Java 16

## Deep Dive References
- [JVMS §3.8 — Compiling Inheritance](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-3.html) — Bytecode for inheritance
- [JLS §15.12.2.5 — Default Method Resolution](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html) — Most-specific default algorithm
- [Initialization Order in Java](https://www.artima.com/insidejvm/ed2/jvmP.html) — Bill Venners on JVM initialization
- Diamond Problem in Java 8 — Oracle Java Magazine
- [Bridge Methods and Synthetic Constructors](https://docs.oracle.com/javase/tutorial/java/generics/bridgeMethods.html) — Oracle tutorial on bridge methods

## Principles
- Liskov Substitution Principle (LSP)
- Fragile Base Class Problem
- Favor Composition Over Inheritance (GoF)
