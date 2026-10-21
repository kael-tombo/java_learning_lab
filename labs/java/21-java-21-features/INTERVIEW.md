# Interview Questions: Java 21 Features

## Company-Specific Focus

### Google
- Virtual threads (JEP 444): how structured concurrency simplifies high-throughput server architecture
- Pattern matching for switch (JEP 441): eliminating boilerplate instanceof-cast patterns
- Record patterns (JEP 440): destructuring records for data-centric code

### Microsoft
- Sequenced collections (JEP 431): the new interface hierarchy for ordered collections
- String templates (JEP 430, previewed JDK 21/22 then withdrawn before JDK 23): what safe interpolation was designed to solve, and today's substitutes
- Java 21 LTS adoption strategy for enterprise customers

### Amazon
- Virtual threads impact on service latency: handling 10K+ concurrent requests on minimal carrier threads
- Scoped values (JEP 446, preview): replacing ThreadLocal in async processing
- Record patterns for stream processing in analytics pipelines

### Meta
- Pattern matching to replace visitor pattern in large codebases
- Unnamed patterns and variables (JEP 443, preview): reducing boilerplate
- What's not in Java 21 yet: value types (Valhalla), universal generics

### Apple
- Immutable by design: records, sealed interfaces, and finality
- Pattern matching for sealed hierarchies: exhaustive type analysis
- Memory consumption: impact of compact strings, records, and primitive patterns

### Oracle
- The full JEP list for Java 21: 444, 441, 440, 443, 445, 446, 431
- JLS updates: pattern matching in switch (JLS 14.30), record patterns (JLS 14.30.2)
- LTS release: what qualifies a feature for LTS vs preview
- Project Amber (pattern matching, records, sealed classes) culmination

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 1930 Unique Length-3 Palindromic Subsequences | Medium | Google, Amazon | Pattern matching on char positions |
| 205 Isomorphic Strings | Easy | Amazon, Google, Apple | Map-based character replacement (record pair) |
| 226 Invert Binary Tree | Easy | Meta, Google | Record patterns for tree nodes |
| 104 Maximum Depth of Binary Tree | Easy | Amazon, Apple, Google | Sealed class with height computation |
| 199 Binary Tree Right Side View | Medium | Amazon, Google, Apple | Tree node record traversal |

## Real Production Scenarios
- **Amazon**: Migrating 2000+ Tomcat threads to virtual threads in S3 gateway — P99 latency dropped 60%, memory dropped 80%
- **Twitter/X**: Pattern matching for switch refactored 500+ instanceof-cast patterns in the timeline service — 30% less code
- **LinkedIn**: Record-based DTOs reduced serialization overhead by 15% compared to mutable POJOs in Kafka pipelines

## Interview Patterns & Tips
- **Virtual threads are not faster**: they increase throughput by reducing thread memory overhead, not by adding CPU speed
- **Pattern matching is exhaustive**: the compiler checks that all cases are covered; unmatched types result in compilation error
- **Record patterns + sealed classes**: the perfect combination for algebraic data type modeling
- **Switch on null**: Before Java 21, switch would NPE on null; now with pattern matching, null can be a case
- **String templates**: Interpolation with \{expr\} — previewed in JDK 21/22, withdrawn before JDK 23, so say this in interviews; on current JDKs use `String.formatted`, SLF4J-style or MessageFormat in production

## Deep Dive Questions
- **JVM continuation**: How does the JVM implement virtual threads? Use the Continuation class for yield/mount
- **Pattern matching compilation**: How is a record pattern compiled? Destructure and match via invokedynamic
- **VT pinning**: What conditions pin a virtual thread to a carrier thread? synchronized blocks, native frames
- **Scoped values vs ThreadLocal**: How do scoped values avoid the memory leak problem of ThreadLocal?
- **Sequenced collections**: How does the new interface hierarchy differ from the existing one? What is the performance of reversed()?
