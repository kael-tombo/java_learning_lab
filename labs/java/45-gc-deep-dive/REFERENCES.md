# References: GC Deep Dive

- **G1 GC Details** (Oracle) - https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector.html
- **ZGC Source Code** (OpenJDK) - https://github.com/openjdk/jdk/tree/master/src/hotspot/share/gc/z
- **Shenandoah GC** (OpenJDK) - https://wiki.openjdk.org/display/shenandoah
- **GC Log Analysis** (Red Hat) - https://developers.redhat.com/articles/2021/08/20/garbage-collection-log-analysis-tools-java
- **G1GC Internals** (Ivan Krylov) - https://www.oracle.com/technetwork/java/javase/tech/g1gc-20220421.html
- **ZGC Colored Pointers** (Erik Österlund) - https://openjdk.org/jeps/376 (ZGC Colored Pointers)
- **SATB Algorithm in G1** - https://www.oracle.com/technetwork/java/javase/tech/g1-general-purpose-gc-20220421.html
- **gcviewer** - https://github.com/chewiebug/GCViewer: Garbage Collection

## Official Documentation
- [HotSpot GC Tuning Guide](https://docs.oracle.com/en/java/javase/21/gc/tuning.html)
- [G1 GC Documentation](https://docs.oracle.com/en/java/javase/21/gc/g1-garbage-collector.html)
- [ZGC Documentation](https://docs.oracle.com/en/java/javase/21/gc/zgc.html)
- [Shenandoah GC Documentation](https://wiki.openjdk.org/display/shenandoah)

## JEPs
- JEP 248: Make G1 the Default Garbage Collector
- JEP 333: ZGC (Experimental)
- JEP 377: ZGC (Production)
- JEP 439: Generational ZGC

## Books
- *Java Performance: The Definitive Guide* by Scott Oaks
- *Optimizing Java* by Ben Evans and Chris Newland
- *The Garbage Collection Handbook* by Richard Jones

## Articles
- [G1 GC Internals](https://www.infoq.com/articles/G1-GC-internals/)
- [ZGC: The Next Generation Low-Latency GC](https://www.infoq.com/articles/zgc/)
- [Understanding G1 GC Logs](https://www.baeldung.com/jvm-g1-gc-logs)

## Tools
- `jstat -gc` — real-time GC statistics
- `jcmd <pid> GC.heap_info` — heap summary
- `jmap -heap` — heap configuration
- GCeasy — GC log analysis
- GCLogViewer — GC log visualization
- Eclipse MAT — heap dump analysis

## Source Code
- `src/hotspot/share/gc/g1/` (G1 collector)
- `src/hotspot/share/gc/z/` (ZGC collector)
- `src/hotspot/share/gc/shenandoah/` (Shenandoah collector)
