# QUIZ — Cloud overview

## 1. `-Xmx` vs `-XX:MaxRAMPercentage` in containers?
<details><summary>Answer</summary>MaxRAMPercentage tracks the cgroup limit; fixed -Xmx ignores it — same image OOMs in small containers and wastes large ones.</details>

## 2. Smaller container → higher or lower f? Why?
<details><summary>Answer</summary>Lower: non-heap N (~250 MB) doesn't shrink, so f ≤ 1 − N/L falls as L falls.</details>

## 3. Layered image benefit in one line?
<details><summary>Answer</summary>Dependency layers cache; rebuilds ship only the app layer (KB, not 100s of MB).</details>

## 4. Liveness vs readiness?
<details><summary>Answer</summary>Liveness: restart me if deadlocked. Readiness: route to me only when dependencies are up (gates deploys).</details>

## 5. Native vs CRaC vs JVM: one-line each?
<details><summary>Answer</summary>Native: ms startup, closed-world (reflection config). CRaC: ms restore, full JVM dynamism. JVM: slowest start, zero constraints.</details>

## 6. Virtual threads kill which old debate?
<details><summary>Answer</summary>Reactive-vs-simple for throughput: plain blocking code on virtual threads saturates I/O — reactive only for backpressure shaping now.</details>

## 7. `synchronized` on virtual threads: hazard?
<details><summary>Answer</summary>Carrier pinning — use ReentrantLock to let the carrier unmount during waits.</details>

## 8. Managed-service gravity + antidote?
<details><summary>Answer</summary>Managed data pulls architectures provider-ward; antidote: repository ports, standard SQL, export-tested backups, conscious per-service lock-in.</details>

## 9. Production bar (4 of 8)?
<details><summary>Answer</summary>Any four: health-gated deploys, externalized secrets, end-to-end traces, signal autoscaling, multizone data, proven backups, cost attribution, written rollback.</details>

## 10. Cold-start waste formula?
<details><summary>Answer</summary>λ·S·mem·p per event class — native/CRaC win proportionally to burstiness, not steady load.</details>
