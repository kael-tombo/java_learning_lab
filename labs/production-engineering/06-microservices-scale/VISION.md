# VISION — Lab 06: Microservices at Scale

> From "we split the monolith, so we can scale" to "scaling is a budget, and here is mine."

---

## The Arc

1. **Connection reality** — file descriptors, ephemeral ports, `TIME_WAIT`, `CLOSE_WAIT`, and why the kernel is often the real constraint.
2. **Fleet-wide budgets** — `Σ replicas × pool` against downstream capacity, and the arithmetic that forces architecture changes.
3. **Container accounting** — memory composition, CPU throttling periods, requests vs limits, JVM container awareness.
4. **JVM in the cluster** — heap share, NMT verification, `maxLifetime` jitter, ZGC for tail latency, crash-loop safety.
5. **Call-graph math** — availability multiplication, retry amplification across depth, deadline propagation, global retry budgets.
6. **Traffic surgery** — load balancers, health/readiness semantics, draining, rollback as an SLO.
7. **Finding the ceiling** — locating the shared bottleneck that makes replicas ineffective.
8. **Fleet diagnosis** — per-pod vs fleet signals, socket-state inspection, connection storms.

---

## Why this lab exists

Splitting a monolith into services creates a new engineering surface: connections between processes, resource budgets multiplied by replica count, and kernel limits that were never a concern when everything was in one JVM.

The specific goal here: **when someone says "let's scale up," you can say what will actually improve and what will break first — with numbers.** And you can find the shared bottleneck before scaling cost without capacity.

---

## Milestones (checkable)

- [ ] M1: Read `ss -tan` output and classify `CLOSE_WAIT` vs `TIME_WAIT` vs `FIN_WAIT_2`, naming the responsible code path for each.
- [ ] M2: Compute a fleet-wide connection budget for a 6-service × 20-replica deployment and conclude whether a pooler is mandatory.
- [ ] M3: Size `nofile`, ephemeral range, and socket buffers for a service with 3,000 concurrent connections; justify every number.
- [ ] M4: Produce a container memory budget (heap, metaspace, stacks, direct, native) with NMT-verified numbers.
- [ ] M5: Explain a CFS throttle event as a latency incident, with the `ΔL = λ·ΔW` amplification calculation.
- [ ] M6: Calculate availability and latency budgets for a 3-hop sync chain, and state where the design must become async.
- [ ] M7: Run a scale-out experiment that demonstrates either linear scaling or the shared bottleneck, with evidence.

---

## Anti-Goals

- Adding replicas without a connection budget for the downstream.
- Setting pool sizes once and never revisiting them at a different replica count.
- Un-jittered pool `maxLifetime` (a deploy-time connection storm waiting to happen).
- Liveness probes that depend on downstream health.
- Believing more pods always means more capacity.
- `-Xmx` equal to the container memory limit (guaranteed OOM-kill).

---

## Interview Lens

- "We scaled from 20 to 60 pods and the database fell over. Explain what happened."
- "How do you size a connection pool when replica count is elastic?"
- "What is `CLOSE_WAIT` telling you and where do you look for the bug?"
- "How do you find out whether your service scales linearly?"
- "Why is `TIME_WAIT` a scaling problem and not just a nuisance?"

---

## 30-Day Plan

- **Week 1** — THEORY + `LINUX_SOCKET_TUNING.md`: socket states, FD/port math, container memory; hands-on with `ss`, `/proc/<pid>/fd`, cgroup files. M1–M3.
- **Week 2** — EXERCISES: budget calculations, throttle math, chain availability; QUIZ to 13/15; FLASHCARDS daily. M4–M6.
- **Week 3** — MINI_PROJECT: build the scale-out harness and reproduce a connection storm and a shared-bottleneck plateau. M7.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a capacity review document for a real service; teach-back: "our budgets, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A fleet connection budget with `Σ replicas × pool` versus downstream capacity.
2. An FD/port/socket-buffer sizing table with the arithmetic.
3. A container memory budget verified by NMT.
4. A CFS-throttle analysis tying kernel throttling to observed p99.
5. A scale-out experiment showing linear scaling or the named ceiling.

---

## Done = You Can

- Look at a deployment manifest and compute the connection, memory, and FD budgets it implies.
- Diagnose a socket-state problem and attribute it to a code path.
- Tell a team "adding replicas will not help; here is the bottleneck" with evidence.
- Design a service's resource configuration so a deploy does not become an incident.
