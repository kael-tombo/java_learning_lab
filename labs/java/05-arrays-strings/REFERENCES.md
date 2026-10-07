# Arrays & Strings — References

## Official Documentation
- [Java Language Specification — Chapter 10: Arrays](https://docs.oracle.com/javase/specs/jls/se21/html/jls-10.html)
- [Java SE Docs — java.lang.String](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html)
- [Java SE Docs — java.lang.StringBuilder](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html)
- [Oracle Tutorial — Arrays](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html)
- [Oracle Tutorial — Strings](https://docs.oracle.com/javase/tutorial/java/data/strings.html)

## Books
- *Core Java Volume I* — Cay S. Horstmann (Chapter 3: Arrays and Strings)
- *Effective Java* — Joshua Bloch (Items 62-65: Strings, concat, StringBuilder)
- *Java Performance* — Scott Oaks (String performance, compact strings)

## JEPs
- JEP 254: Compact Strings — Java 9
- JEP 280: Indify String Concatenation — Java 9
- JEP 355: Text Blocks (Preview) — Java 13
- JEP 378: Text Blocks (Standard) — Java 15

## Deep Dive References
- [JVMS §2.7 — Array Types](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html#jvms-2.7) — Array types in the JVM
- [JVMS §newarray / anewarray](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-6.html) — Array allocation instructions
- [String Deduplication in G1 GC](https://docs.oracle.com/en/java/javase/21/gctuning/g1-garbage-collector.html) — G1 string deduplication
- [Aleksey Shipilëv: String Concatenation](https://shipilev.net/jvm/anatomy-quarks/17-string-concatenation/) — Deep analysis of concatenation strategies
- [String Table Tuning](https://docs.oracle.com/en/java/javase/21/vm/string-table-tuning.html) — String pool sizing and performance

## Tools
- [fastutil](https://fastutil.di.unimi.it/) — Type-specific collections (avoids boxing)
- [Apache Commons Lang — StringUtils](https://commons.apache.org/proper/commons-lang/) — Enhanced string utilities
