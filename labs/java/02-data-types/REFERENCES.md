# Data Types — References

## Official Documentation
- [Java Language Specification — Chapter 4: Types, Values, and Variables](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html)
- [Oracle Tutorial — Primitive Data Types](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html)
- [Java SE Docs — java.lang](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/package-summary.html)

## Books
- *Core Java Volume I* — Cay S. Horstmann (Chapter 3: Fundamental Programming Structures)
- *Effective Java* — Joshua Bloch (Items 1-9 relate to types and objects)
- *Java: The Complete Reference* — Herbert Schildt

## Articles
- [Baeldung — Java Primitives vs Objects](https://www.baeldung.com/java-primitives-vs-objects)
- [Baeldung — Guide to Autoboxing](https://www.baeldung.com/java-autoboxing)
- [Oracle — Autoboxing](https://docs.oracle.com/javase/tutorial/java/data/autoboxing.html)

## JEPs
- JEP 286: Local-Variable Type Inference (var) — Java 10
- JEP 395: Records — Java 16 (preview lineage JEP 359 → JEP 384)
- JEP 401: Value Objects (Project Valhalla, in development)

## Deep Dive References
- [JLS Chapter 4 — Types, Values, and Variables](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html) — Complete type system specification
- [JVMS Chapter 2 — JVM Data Types](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html) — JVM-level type model
- [JEP 401: Value Objects (Valhalla)](https://openjdk.org/jeps/401) — Value types in the JVM
- [JVM Field Access Optimization](https://shipilev.net/jvm/anatomy-quarks/3-field-access-costs/) — Aleksey Shipilëv's detailed analysis
- [Compact Object Headers](https://openjdk.org/jeps/519) — JEP 519: Compact
  Object Headers (JDK 25). JEP 450 was the earlier *experimental* iteration in
  JDK 21; 519 is the feature that actually shipped.
