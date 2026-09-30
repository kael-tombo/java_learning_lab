# EXERCISES: Production Diagnostics & Profiling
## Lab 03 | Production Engineering Academy

---

## Exercise 1: Pinpoint the Catastrophic Regex Backtracking Bug

### Objective
Diagnose a CPU spike causing 100% core usage in a simulated web worker using thread dumps and async-profiler.

### The Broken Code
```java
package com.learning.production.lab03;

import java.util.regex.Pattern;

public class RegexCpuSpikeSimulator {
    // Evil Regex: Vulnerable to exponential catastrophic backtracking
    private static final Pattern EVIL_REGEX = Pattern.compile("^([a-zA-Z0-9]+)+$");

    public static void main(String[] args) {
        System.out.println("Starting Regex CPU Spike simulator. PID: " + ProcessHandle.current().pid());

        // Harmless looking input that triggers 2^n backtrack evaluations
        String maliciousPayload = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

        Runnable task = () -> {
            boolean matches = EVIL_REGEX.matcher(maliciousPayload).matches();
            System.out.println("Result: " + matches);
        };

        Thread thread = new Thread(task, "worker-regex-validator-01");
        thread.start();
    }
}
```

### Lab Instructions
1. Run the simulator. Notice that one CPU core immediately hits 100%.
2. In another terminal, use `top -H` or `ps` to find the thread ID consuming 100% CPU.
3. Convert the TID to hex and run `jcmd <PID> Thread.print`. Match the `nid` to locate the stack trace.
4. Replace the exponential regex with an atomic group or possessive quantifier:
   `^([a-zA-Z0-9]++)+$` or standard input validation.
5. Re-run and verify execution completes in $< 1\text{ms}$.

---

## Exercise 2: Flamegraph Analysis of Lock Contention

### Scenario
An e-commerce order service suffers high p99 latency during flash sales. Threads are blocked on a synchronized singleton.

### Tasks
1. Run `LockContentionHarness` simulating 64 concurrent threads trying to acquire a coarse-grained synchronized lock.
2. Run `async-profiler` targeting lock contention:
   ```bash
   asprof -e lock -d 15 -f /tmp/lock_flamegraph.html <PID>
   ```
3. Open `lock_flamegraph.html` and identify the offending lock class and method.
4. Refactor the code to use `LongAdder` or a striped lock pattern (`Striped<Lock>`).
5. Re-profile and prove that lock wait duration drops from seconds to zero.
