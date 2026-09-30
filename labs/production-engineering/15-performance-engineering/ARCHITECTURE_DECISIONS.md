# ARCHITECTURE DECISIONS: High-Performance Architecture Standards
## Lab 15 | Production Engineering Academy

---

## ADR-01: Microbenchmarking & Mechanical Sympathy Design Standards

### Status: ACCEPTED

### Context
Ad-hoc manual performance benchmarks frequently caused misinformed architectural decisions, including premature optimizations that actually degraded production throughput.

### Decisions
1. **Mandatory JMH for Core Optimizations**:
   - Any algorithmic or low-latency PR claiming performance improvements must include a JMH benchmark suite.
   - PR must demonstrate statistically significant improvement with $p < 0.01$.
2. **Memory Layout & Cache Friendliness**:
   - Prefer contiguous array-backed collections (`ArrayList`, primitive arrays, or FastUtil primitive maps) over pointer-heavy structures (`LinkedList`, node trees).
   - In high-throughput concurrent shared variables, apply `@Contended` or explicit 64-byte padding to prevent False Sharing.
3. **Allocation-Free Hot Paths**:
   - Zero object allocations permitted inside inner packet/trade processing loops.

### Consequences
- Eliminates inaccurate benchmark claims.
- Maximizes hardware CPU cache utilization.
