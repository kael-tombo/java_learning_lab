# Interview Questions: ZGC

## Company-Specific Focus

### Google
- ZGC: low-latency GC (sub-millisecond pause times)
- Region-based: ZPages (small, medium, large)
- Colored pointers: 42-bit address space, 4 color bits for metadata

### Microsoft
- ZGC vs .NET GC: pause time comparison
- Concurrent compaction: no STW compaction

### Amazon
- Multi-Tenancy: ZGC for large heaps (multi-TB)
- Load barriers: intercepting object references for concurrent relocation
- Generational ZGC: JDK 21+ improved performance

### Meta
- Sub-millisecond pauses: ZGC pauses typically < 1ms
- Colored pointers: mark and relocate information in pointer
- Remap: concurrent remapping of references after relocation

### Apple
- ZGC on ARM64: full support
- Non-generational vs generational: JDK 21 adds generational mode

### Oracle
- JEP 333: ZGC (Experimental)
- JEP 377: ZGC (Production) — experimental was JEP 333 in JDK 11
- JEP 439: Generational ZGC
- Colored pointers + load barriers

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — ZGC is a low-latency GC) |

## Real Production Scenarios
- **Netflix**: ZGC on 300GB heap provides <1ms pause times for recommendation engine
- **LinkedIn**: Migrating from G1 to ZGC eliminated GC pauses in latency-critical search service

## Interview Patterns & Tips
- **Colored pointers**: metadata bits in 64-bit pointer (4 bits for marking/relocation status)
- **Load barrier**: intercepts object references, ensures consistency
- **Concurrent**: all phases (mark, relocate, remap) are concurrent
- **Generational**: JDK 21 adds generational mode

## Deep Dive Questions
- **Colored pointers**: How are the 4 color bits used?
- **Load barrier**: How does the load barrier intercept object access?
- **Relocation**: How does concurrent relocation work?
- **Remap**: How does ZGC handle remapping of moved objects?
- **Generational ZGC**: How does the generational mode differ?