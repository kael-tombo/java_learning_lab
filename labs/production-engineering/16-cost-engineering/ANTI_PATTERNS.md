# ANTI-PATTERNS: Cost Engineering & FinOps
## Lab 16 | Production Engineering Academy

---

## Anti-Pattern 1: Sizing JVM Heap to Exactly 32 GB (Compressed OOPs Cliff)

### The Mistake
Configuring `-Xmx32g`.

### Why It Fails
- Java uses **Compressed OOPs (Ordinary Object Pointers)** for heaps $< 32\text{ GB}$. Pointers are compressed into 32 bits (4 bytes) by taking advantage of 8-byte object alignment ($2^{32} \times 8 = 32\text{ GB}$).
- The moment heap reaches or crosses $32\text{ GB}$, the JVM is forced to use uncompressed **64-bit pointers (8 bytes)**!
- Every single object reference in memory doubles in size!
- An application moving from `-Xmx31g` to `-Xmx32g` actually has **LESS usable object capacity** because references consume 40% more RAM. A 32 GB heap has less effective capacity than a 30 GB heap!

### The Correct Production Fix
Always cap heap at **`-Xmx31g`** or `-Xmx30g` to stay below the 32 GB Compressed OOPs boundary. If more memory is required, jump straight to 48 GB+.

---

## Anti-Pattern 2: Uncompressed High-Throughput Network Communication

### The Mistake
Publishing millions of JSON events to Kafka or over HTTP without wire compression.

### Why It Fails
Cross-AZ and internet data egress charges are among the highest hidden costs in cloud providers. Uncompressed JSON contains repetitive keys, resulting in gigabytes of redundant wire transfer billed at $0.02/GB.

### The Correct Production Fix
Enable Snappy, lz4, or zstd compression on Kafka producers and HTTP clients. Compression reduces wire egress volume by 70–85% with negligible CPU overhead.
