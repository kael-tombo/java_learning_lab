# References: JVM Tuning

- **Java GC Tuning Guide** (Oracle) - https://docs.oracle.com/en/java/javase/21/gctuning/
- **Compressed OOPs** (John Rose) - https://wiki.openjdk.org/display/HotSpot/CompressedOops
- **JVM Ergonomics** - https://docs.oracle.com/en/java/javase/21/vm/ergonomics.html
- **Large Pages in HotSpot** - https://docs.oracle.com/en/java/javase/21/vm/large-pages.html
- **Container awareness (JEP 312, Thread-Local Handshakes, JDK 10)**
  - https://openjdk.org/jeps/312
  (No JEP is titled "Container Support"; JDK 10 container awareness arrived via
  JEP 312 plus the `UseContainerSupport` VM options.)
- **TLAB Sizing** (Sanjeev Krishnan) - https://shipilev.net/jvm/anatomy-park/4-tlab-allocation/
- **Biased Locking Removal (JEP 374)** - https://openjdk.org/jeps/374
- **Java Performance Tuning Guide** (Scott Oaks) - O'Reilly, *Java Performance: The Definitive Guide*: JVM Tuning

## Official Documentation
- [Java HotSpot VM Options](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html)
- [JVM Tuning Guide](https://docs.oracle.com/en/java/javase/21/gc/tuning.html)
- [JVM Command-Line Options](https://docs.oracle.com/en/java/javase/21/docs/specs/java/vm-options.html)

## JEPs
- JEP 122: Remove the Permanent Generation
- JEP 158: Unified JVM Logging
- JEP 310: Application Class-Data Sharing
- JEP 350: Dynamic CDS Archives
- JEP 439: Generational ZGC

## Books
- *Java Performance: The Definitive Guide* by Scott Oaks
- *Optimizing Java* by Ben Evans and Chris Newland
- *Java Performance Companion* by Charlie Hunt
- *The Well-Grounded Java Developer* by Evans and Verburg

## Tools
- `jstat` — JVM statistics monitoring
- `jcmd` — diagnostic commands for JVM
- `jmap` — memory map and heap dump
- `JMC (Java Mission Control)` — JFR-based monitoring
- `JITWatch` — JIT compilation analysis
- `GCeasy` — GC log analysis
- `async-profiler` — CPU and allocation profiling

## Articles
- [JVM Tuning for High Performance](https://www.baeldung.com/jvm-tuning)
- [Understanding Java Code Cache](https://www.baeldung.com/jvm-code-cache)
- [Java Metaspace Guide](https://www.baeldung.com/java-metaspace)

## Source Code
- `src/hotspot/share/runtime/arguments.cpp` (flag parsing)
- `src/hotspot/share/memory/metaspace/` (Metaspace)
- `src/hotspot/share/code/codeCache.cpp` (Code Cache)
- `src/hotspot/share/gc/shared/stringDedup/` (String Dedup)
