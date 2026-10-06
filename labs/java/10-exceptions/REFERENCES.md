# Exceptions — References

## Official Documentation
- [Java Language Specification — Chapter 11: Exceptions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html)
- [Oracle Tutorial — Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/index.html)
- [Java SE Docs — java.lang.Throwable](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Throwable.html)

## Books
- *Effective Java* — Joshua Bloch (Items 69-77: Exception guidance)
- *Core Java Volume I* — Cay S. Horstmann (Chapter 7: Exceptions, Assertions, Logging)
- *Clean Code* — Robert C. Martin (Chapter 7: Error Handling)
- *Java Concurrency in Practice* — Brian Goetz (InterruptedException handling)

## Articles
- [Baeldung — Exception Handling in Java](https://www.baeldung.com/java-exceptions)
- [Baeldung — Try-With-Resources](https://www.baeldung.com/java-try-with-resources)
- [Baeldung — Custom Exception in Java](https://www.baeldung.com/java-new-custom-exception)
- [JEP 358 — Helpful NullPointerExceptions](https://openjdk.org/jeps/358)

## JEPs
- JEP 213: Milling Project Coin — Java 9 (shipped try-with-resources's
  enhancement allowing effectively-final variables outside the resource list,
  plus JEP 250-style deprecation of `finalize` warning groundwork)
- JEP 358: Helpful NullPointerExceptions — Java 14
- JEP 421: Deprecate Finalization for Removal — Java 18

## Deep Dive References
- [JVMS §3.12 — Throwing and Handling Exceptions](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-3.html) — Exception table and bytecode
- [JVMS §4.7.3 — Code Attribute Exception Table](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html) — Exception table structure
- [JVM Anatomy Quark #18: Stack Trace](https://shipilev.net/jvm/anatomy-quarks/18-stacktrace/) — Stack trace construction costs
- [JEP 358: Helpful NullPointerExceptions](https://openjdk.org/jeps/358) — Detailed NPE messages (Java 14+)
- [Throwable.addSuppressed JavaDoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Throwable.html) — Suppressed exception API

## Related Patterns
- [Result Pattern in Java](https://www.baeldung.com/java-result-type)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Retry Pattern](https://www.baeldung.com/resilience4j)
