# Memory Model — Internal Mechanics

## JVM Memory Model Implementation

### Happens-Before Implementation

The JMM is implemented through memory barriers:
- **LoadLoad**: Prevents reordering of loads
- **StoreStore**: Prevents reordering of stores
- **LoadStore**: Prevents reordering of loads with subsequent stores
- **StoreLoad**: Full barrier (most expensive)

### Volatile Implementation

Reading a volatile field inserts a LoadLoad+LoadStore barrier. Writing a volatile field inserts a StoreStore+StoreLoad barrier.

### Final Field Semantics

The JMM guarantees that a properly constructed object's final fields are visible to all threads without synchronization. The compiler ensures the constructor's final field writes are not reordered past the constructor's publication.

### GC Generations

HotSpot heap generation structure:
- **Young Generation**: Eden + two Survivor spaces (minor GC)
- **Old Generation**: Tenured objects (major GC)
- **Metaspace**: Class metadata (no longer in heap)

### Cache Coherence

Modern CPUs use MESI/MESIF protocols:
- Modified: Cache line is dirty in this core
- Exclusive: Cache line is clean and exclusive
- Shared: Cache line may exist in multiple caches
- Invalid: Cache line must be re-read

False sharing occurs when unrelated variables share a cache line, causing unnecessary coherence traffic.
