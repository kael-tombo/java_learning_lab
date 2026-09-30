# THEORY: Cost Engineering & FinOps for Java Architectures
## Lab 16 | Production Engineering Academy

---

## 1. Cloud Cost Economics of the JVM

In enterprise cloud computing (AWS, GCP, Azure), compute costs scale directly with allocated **vCPU, Memory (GB), and Cross-AZ Network Egress**:
$$\text{Annual Fleet Cost} = \sum_{\text{clusters}} \left( N_{\text{vCPU}} \times P_{\text{vCPU}} + M_{\text{GB}} \times P_{\text{GB}} + E_{\text{TB}} \times P_{\text{Egress}} \right) \times 8760\text{ hrs}$$

### The Java Memory Penalty
Java applications traditionally require significantly more memory than Go or Rust services due to:
- Object headers (12–16 bytes per object: Mark Word + Klass Word).
- Reference pointer overhead (Compressed OOPs vs 64-bit pointers).
- Garbage collection headroom (20–40% unused heap space required to prevent GC thrashing).
- Non-heap overhead (Metaspace, thread stacks, Code Cache, Netty direct memory).

---

## 2. ARM64 (AWS Graviton / GCP Tau T2A) Migration Economics

Migrating Java workloads from x86_64 (Intel Xeon / AMD EPYC) to ARM64 (AWS Graviton 3/4):
1. **Price-to-Performance Advantage**:
   - Graviton instances are **20% cheaper** per vCPU/hour than equivalent x86 instances.
   - Neoverse cores provide dedicated L2 cache per core without hyperthreading resource contention, yielding **15–25% higher Java throughput**.
   - Net efficiency gain: **35–45% cost reduction** for identical throughput.
2. **JVM Support**:
   - OpenJDK has supported AArch64 natively since Java 9.
   - Java bytecode is platform-independent; only JNI native dependencies (Netty `epoll`, RocksDB, snappy) require ARM64 `.so` libraries.

---

## 3. Kubernetes Node Bin-Packing & Pod Sizing

When Kubernetes pods have poorly matched CPU/Memory ratios (e.g. asking for 4 cores but only 1 GB RAM, or 1 core and 16 GB RAM), worker nodes experience fragmentation:
- Nodes cannot schedule new pods because either CPU or Memory is exhausted while the other resource sits 80% wasted ("Stranded Capacity").
- **Cost-Optimal Sizing**: Align pod requests with cloud instance ratios (Standard instances are $1 \text{ vCPU} : 4 \text{ GiB RAM}$). Sizing pods as `1 vCPU / 4 GiB` or `2 vCPU / 8 GiB` achieves 95%+ node bin-packing density.
