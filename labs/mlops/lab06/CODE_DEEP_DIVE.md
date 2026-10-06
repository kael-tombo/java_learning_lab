# Kubernetes for ML - Code Deep Dive

**Track:** mlops  |  **Lab:** lab06  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
src/
  KubernetesLab.java        driver: renders manifests, validates them, runs a probe simulation
  DeploymentBuilder.java    replicas, strategy, probes, resources, affinity
  ProbeBuilder.java         startup/readiness/liveness with explicit budgets
  ResourcePlanner.java      requests/limits derivation from a load-test profile
  Manifest.java             typed manifest model with validation rules
```

ProbeBuilder carries a budget field per probe. A probe whose expected cost is not stated is a probe that will eventually be made expensive by someone who did not know.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `DeploymentBuilder` | builds a Deployment manifest with strategy, probes and resources |
| `ProbeBuilder` | startup, readiness and liveness with period, threshold and budget |
| `ResourcePlanner` | derives requests and limits from a measured load profile |
| `Manifest` | typed manifest with validation: probes present, resources set, PDB defined |

---

## 3.1 Three probes with explicit budgets

Startup covers slow model loads, readiness covers warm-up, liveness is constant-time. Each carries its own cost budget.

```java
Probe startup(int failureThreshold, int periodSeconds, long budgetMs) {
    // budgetMs is the fleet-wide cost ceiling; exceeding it is a design error
    return new Probe("startup", "/readyz", periodSeconds, failureThreshold, 0, budgetMs);
}

Probe readiness(int periodSeconds, int successThreshold, long budgetMs) {
    // failing readiness removes the pod from the Service but does NOT restart it
    return new Probe("readiness", "/readyz", periodSeconds, 3, successThreshold, budgetMs);
}

Probe liveness(int periodSeconds) {
    // deliberately dependency-free: a dependency blip must not restart the fleet
    return new Probe("liveness", "/healthz", periodSeconds, 3, 1, 5);
}
```


---

## 3.2 Resource planning from a measured load profile

Requests come from p99 and limits sit above it, with native headroom for memory. The numbers are derived, not typed.

```java
ResourcePlan plan(LoadProfile p, double memoryLimitGiB) {
    // requests: p99 so the scheduler reserves enough
    double cpuRequest = Math.ceil(p.p99CpuCores * 100) / 100.0;
    double memRequestMiB = Math.ceil(p.p99RssMiB / 64) * 64;   // round up to a sane step
    // limits: above p99 so a burst is not permanently throttled
    double cpuLimit = Math.ceil(cpuRequest * 2 * 100) / 100.0;
    // memory: cap by the node profile, leaving ~25% for native allocation
    double memLimitMiB = Math.min(memoryLimitGiB * 1024 * 0.75, memRequestMiB * 1.3);
    return new ResourcePlan(cpuRequest, cpuLimit, memRequestMiB, memLimitMiB);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Pod startup | `O(model size + warm-up)` | the startup probe budget must exceed it |
| Readiness probe traffic | `O(replicas / period)` | cost per probe must be small |
| Liveness probe traffic | `O(replicas / period)` | must be constant-time |
| Horizontal scale-up | `O(replicas new)` | bounded by maxSurge and node capacity |

## 5. Correctness and Numerics

- Size requests from measured p99 and limits above it; never set them equal.
- Leave 25-30% memory headroom above the heap for native allocation.
- Make liveness constant-time; a dependency call there is a fleet-wide hazard.
- Set a PDB with a fraction plus an absolute floor, and verify a drain honours it.
- Scale on a latency-correlated signal, with a stabilisation window to avoid flapping.

## 6. Test Strategy

- A manifest without requests or limits fails validation.
- A missing readiness probe fails validation.
- Simulation shows a slow boot surviving via the startup probe, then liveness running.
- A simulated dependency outage does not trigger liveness failures.
- A simulated node drain respects the PodDisruptionBudget.
- Resource planning reproduces the measured p99 within the rounding step.

## 7. Extension Points

- Add topology spread constraints and verify replica distribution across simulated zones.
- Implement an autoscaling policy on queue depth with a stabilisation window.
- Add a chaos scenario: kill 30% of pods and measure time to full service.

## 8. Review Checklist

- [ ] Startup, readiness and liveness all defined and justified
- [ ] Liveness constant-time and dependency-free
- [ ] Requests measured; limits above p99 with memory headroom
- [ ] PDB present with a fraction and an absolute floor
- [ ] Replicas spread across zones
- [ ] Rollout strategy chosen against the latency SLO
