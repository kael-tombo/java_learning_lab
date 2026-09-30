# EXERCISES: Cost Engineering & FinOps for Java
## Lab 16 | Production Engineering Academy

---

## Exercise 1: Demonstrate the 32 GB Compressed OOPs Memory Cliff

### Objective
Measure total object reference memory footprint at `-Xmx31g` vs `-Xmx32g` using Java Object Layout (JOL).

### Tasks
1. Write a Java program allocating an array of 50,000,000 object references:
   ```java
   Object[] array = new Object[50_000_000];
   ```
2. Run with `-Xmx31g`:
   Inspect pointer size using `org.openjdk.jol.info.VM.current().details()`. Verify reference size is 4 bytes.
3. Run with `-Xmx32g`:
   Verify reference size jumps to 8 bytes.
4. Calculate total memory wasted solely on reference pointers ($50,000,000 \times 4\text{ bytes} = 200\text{ MB}$ per array).

---

## Exercise 2: Calculate Cloud Cost Savings for ARM64 Graviton Migration

### Objective
Build a FinOps calculation model comparing a 100-node cluster running `c6i.2xlarge` (Intel) vs `c7g.2xlarge` (Graviton ARM64).

### Tasks
1. Gather AWS pricing:
   - `c6i.2xlarge`: $0.34/hr
   - `c7g.2xlarge`: $0.29/hr
2. Assume Graviton provides 20% higher throughput, requiring only 83 instances instead of 100 instances for equivalent work.
3. Calculate monthly and annual cost savings.
4. Add cross-AZ data reduction from Topology Aware Routing (saving 50 TB/month at $0.02/GB).
5. Produce an executive FinOps business case summary document.
