# THEORY: Chaos Engineering & Failure Injection
## Lab 18 | Production Engineering Academy

---

## 1. Principles of Chaos Engineering

Chaos engineering is the discipline of experimenting on a system in order to build confidence in the system's capability to withstand turbulent conditions in production (originated by Netflix Chaos Monkey):

1. **Define Steady State**: Establish measurable baseline metrics indicating normal system health (e.g. 99.9% HTTP success, p99 latency $< 150\text{ms}$).
2. **Formulate a Hypothesis**: "If we inject 2,000ms latency to the recommendation engine, checkout throughput will not degrade and error rate will remain $< 0.1\%$."
3. **Introduce Real-World Turbulence**: Inject hardware faults, network partitions, disk exhaustion, or thread pool stalls.
4. **Attempt to Disprove Hypothesis**: Compare steady state metrics during the experiment against the baseline.
5. **Automate Experiments & Minimize Blast Radius**: Always have an automated emergency abort mechanism if customer error budget burns.

---

## 2. Taxonomy of Injected Chaos Faults

```
+-------------------------------------------------------------------+
|                        CHAOS TAXONOMY                             |
+-------------------+-----------------------+-----------------------+
|  INFRASTRUCTURE   |        NETWORK        |      APPLICATION      |
+-------------------+-----------------------+-----------------------+
| Pod termination   | Packet latency (1-5s) | OutOfMemoryError      |
| Node drain / kill | Packet drop / loss    | Thread pool lockup    |
| Disk fill (100%)  | DNS failure           | Database conn leak    |
| CPU burn (100%)   | TCP reset (RST)       | Unhandled runtime ex  |
+-------------------+-----------------------+-----------------------+
```

---

## 3. Bytecode Fault Injection vs Network-Level Fault Injection

- **Network-Level (Chaos Mesh / Toxiproxy / iptables)**:
  - Modifies network packets using Linux kernel `tc` (traffic control) and `iptables`.
  - Non-invasive to the JVM process; language agnostic; tests socket timeouts and circuit breakers.
- **Bytecode / JVM-Level (Chaos Monkey for Spring Boot / Byte-Buddy)**:
  - Dynamically rewrites Java bytecode at runtime using JVM TI agents or Spring AOP.
  - Can inject exceptions into specific internal Java methods, simulate garbage collection freezes, or artificially mutate returned objects.
