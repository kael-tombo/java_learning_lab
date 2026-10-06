# Interview Questions: Shenandoah GC

## Company-Specific Focus

### Google
- Shenandoah: low-pause GC (similar goals to ZGC)
- Brooks pointer: forwarding pointer stored in object header
- Concurrent compaction: evacuation and compaction concurrent with application

### Microsoft
- Shenandoah vs ZGC: similar low-latency goals, different implementation
- Brooks pointer vs colored pointers: key difference

### Amazon
- Shenandoah region-based: similar to G1 region layout
- Concurrent evacuation: copying objects while application threads run

### Meta
- Pause times: target < 10ms, often < 1ms
- SATB: concurrent marking phase uses SATB
- Update references: concurrent phase to update references to moved objects

### Apple
- Shenandoah on ARM64: full support
- Generational Shenandoah: JDK 21+ 

### Oracle
- JEP 189: Shenandoah (Experimental), JDK 12 — production in 15 via JEP 379.
  (JEP 189 is Shenandoah; Scalable Native Memory Tracking was a JDK 8 update,
  not a separate JEP.)
- JEP 379: Shenandoah (Production)
- OpenJDK contribution from Red Hat
- Brooks pointer: forwarding pointer in object header

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Shenandoah is a low-latency GC) |

## Real Production Scenarios
- **Netflix**: Shenandoah GC for latency-sensitive streaming services — sub-10ms GC pauses
- **LinkedIn**: Shenandoah evaluation vs ZGC for search indexing system

## Interview Patterns & Tips
- **Brooks pointer**: forwarding pointer in the object header
- **Concurrent evacuation**: objects are moved while application threads run
- **Weak reference**: Shenandoah handles weak, soft, and phantom references
- **Generational**: JDK 21 adds generational mode

## Deep Dive Questions
- **Brooks pointer**: Where is the forwarding pointer stored?
- **Shenandoah vs ZGC**: What are the architectural differences?
- **Evacuation**: How does concurrent evacuation work?
- **SATB**: How does Shenandoah use SATB for marking?
- **Generational Shenandoah**: How does the generational mode improve performance?