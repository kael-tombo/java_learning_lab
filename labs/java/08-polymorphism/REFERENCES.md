# Polymorphism — References

## Official Documentation
- [Java Language Specification — Chapter 8.4: Method Overriding](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html)
- [Oracle Tutorial — Polymorphism](https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html)
- [Oracle Tutorial — Overriding and Hiding](https://docs.oracle.com/javase/tutorial/java/IandI/override.html)

## Books
- *Design Patterns* — Gang of Four (Strategy, Command, Observer, State patterns)
- *Head First Design Patterns* — Freeman & Robson (Excellent OO principles explanation)
- *Effective Java* — Joshua Bloch (Item 41: Overloading; Item 42: Varargs)
- *Core Java Volume I* — Cay S. Horstmann (Chapter 5: Inheritance and Polymorphism)
- *Clean Architecture* — Robert C. Martin (Polymorphism as architectural principle)

## Articles
- [Baeldung — Polymorphism in Java](https://www.baeldung.com/java-polymorphism)
- Baeldung — Method Overloading vs Overriding
- Baeldung — Covariant Return Types

## JEPs
- JEP 394: Pattern Matching for instanceof — Java 16
- JEP 441: Pattern Matching for switch — Java 21

## Deep Dive References
- [JVMS §2.9.4 — Virtual Invocation](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html) — Dynamic dispatch in JVM
- [JVM Anatomy Quark #4: Inline Cache](https://shipilev.net/jvm/anatomy-quarks/4-inline-cache/) — C2 inline cache analysis
- [JVM Anatomy Quark #5: Polymorphic Call Sites](https://shipilev.net/jvm/anatomy-quarks/5-polymorphic-call-sites/) — Polymorphic site optimization
- [VTable Implementation in HotSpot](https://wiki.openjdk.org/display/HotSpot/VirtualCalls) — OpenJDK Wiki on vtables
- [Interface Dispatch in HotSpot](https://wiki.openjdk.org/display/HotSpot/InterfaceCalls) — Itable implementation

## Principles
- Open/Closed Principle
- Liskov Substitution Principle
- Programming to an Interface, Not an Implementation
