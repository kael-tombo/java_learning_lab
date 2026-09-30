# RUNBOOK: Hardware-Level Performance Triage with Linux `perf`
## Lab 15 | Production Engineering Academy

---

## RUNBOOK 01: Diagnosing CPU Cache Misses & CPI (Cycles Per Instruction)

**Tooling**: Linux `perf` stat

### Step 1: Collect Hardware Performance Counters
Attach `perf stat` to running Java process for 10 seconds:
```bash
perf stat -p $(pgrep -f "java.*app.jar") \
  -e cycles,instructions,cache-references,cache-misses,branches,branch-misses \
  sleep 10
```

### Step 2: Analyze Results
- **IPC (Instructions Per Cycle)**:
  $$\text{IPC} = \frac{\text{instructions}}{\text{cycles}}$$
  - If $\text{IPC} > 1.5$: Code is compute-efficient and executing fast instructions.
  - If $\text{IPC} < 0.5$: CPU is **stalled 50%+ of cycles** waiting for memory DRAM / cache misses!
- **Cache Miss Rate**:
  $$\frac{\text{cache-misses}}{\text{cache-references}} \times 100\%$$
  If $> 15\%$, code is pointer-chasing (linked lists, node graphs) and cache-unfriendly.

---

## RUNBOOK 02: Detecting False Sharing with `perf c2c`
```bash
# Record cache-to-cache events for 20 seconds
perf c2c record -p $(pgrep -f "java.*app.jar") -- sleep 20
# Generate analysis report
perf c2c report --stdio
```
Look for lines with high **HITM (Hit on Modified Cache Line)**. Note the data address and trace back to Java field layout with JOL (Java Object Layout).
