# Lab 16: Cost Engineering & Cloud Optimization — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What are the dominant cost drivers for a JVM service on Kubernetes, roughly in order?**
- A) CPU first, always
- B) Usually: compute (proportional to requested CPU × time), then data transfer/egress, then storage (especially managed DBs and object storage), then managed services (Redis, Kafka, search), then idle waste (over-provisioned replicas, never scaled to zero, unattached volumes, forgotten staging environments)
- C) Storage first
- D) Only the managed database

**Answer: B** — Compute dominates most Java estates, but *idle* compute — replicas running at night and weekends, dev/staging environments running 24/7 — is the largest recoverable category. And for API-heavy services, egress can exceed compute.

---

**Q2. Why should you optimise requests/limits before anything else in a Java service?**
- A) Because Kubernetes charges for requests
- B) Because in a managed Kubernetes offering you are billed for requested resources, and because requests determine scheduling density. A pod requesting 2 vCPU that uses 200 m wastes 90% of its reservation, and it also blocks 10× the scheduling capacity per node
- C) Because limits increase cost
- D) Because it improves latency

**Answer: B** — First find out whether your provider bills on requests or on actual usage; the answer changes the strategy, and this is a fact to establish rather than assume.

---

**Q3. What is the difference between utilisation and allocation, and why does the gap cost money?**
- A) They are the same
- B) Utilisation is what you use; allocation is what you reserve. Cost ≈ allocation. So a pod with 15% utilisation on a 2 vCPU request is 85% waste, and it is invisible on a utilisation dashboard unless you plot utilisation *against* request
- C) Allocation is usage
- D) Utilisation includes storage

**Answer: B** — The most useful cost dashboard is not utilisation; it is the distribution of `actual / requested` per service. A service whose pods average 15% has a rightsizing opportunity worth quantifying immediately.

---

**Q4. Requests vs limits and bin-packing: what does over-requesting cost beyond the bill?**
- A) Nothing
- B) It reduces the number of pods per node, so you need more nodes; and because of the memory-overcommit headroom rule (a node cannot allocate all its memory because of the OS and kubelet), an over-requested pod can leave a node permanently unable to schedule anything. Over-requesting is both a cost and a resilience problem
- C) It slows the JVM
- D) It reduces replica count

**Answer: B** — Capacity planning (`Σ requests ≤ allocatable × headroom`) is the same arithmetic as scheduling feasibility in Lab 07, and over-requesting fails it.

---

**Q5. What is the cost of an idle environment, and what is the standard control?**
- A) Environments are free
- B) A dev/staging environment with 6 services × 3 replicas running 24/7 costs a fixed amount every hour it is idle. Standard controls: scheduled shutdown (nights and weekends), `KEDA`/HPA scale-to-zero with a wake-up for reviewers, and separate low-cost node pools (spot) for non-production
- C) Only staging costs
- D) They are covered by the cloud credit

**Answer: B** — Before any micro-optimisation, quantify idle environments; they are frequently 15–25% of a platform's bill and are trivially removable.

---

**Q6. Spot/preemptible instances: what is the correct workload placement?**
- A) Anything interruptible
- B) Fault-tolerant, retryable, stateless, delay-tolerant work: batch jobs, CI runners, preview environments, async consumers with a DLQ and idempotency. Not: singletons, latency-critical request paths without replicas, databases without multi-AZ replication, or anything where a 30-second interruption causes an unrecoverable state change
- C) Only development environments
- D) Spot is always cheaper and safe

**Answer: B** — Spot also prices by capacity, so a bid that loses capacity raises the price and can hit the cap; a diversified spot pool across instance families and AZs reduces the correlated-loss risk. Verify your provider's exact interruption and pricing semantics.

---

**Q7. When does GraalVM native image actually save money for a Java service?**
- A) Always
- B) For spiky, low-duty-cycle, request-light workloads where memory dominates the bill and startup time dominates the cost of cold starts (functions, scale-to-zero services, CLI tools). For a steady, CPU-bound, high-throughput service, a JIT-compiled JVM is faster per dollar, and native image trades throughput and peak throughput for footprint and startup
- C) Only for microservices with 1000 rps
- D) Never

**Answer: B** — Compute the duty cycle: `savings = (native_cost × duty_cycle_savings) − (build_maintenance + lost_throughput)`. At high sustained load the JIT's higher throughput usually wins on cost-per-request.

---

**Q8. What is the cheapest capacity reduction that most teams miss?**
- A) Smaller instances
- B) Right-sizing the JVM heap and the pod: a service running at 8% CPU on a 2 vCPU request can often move to a smaller pod or fewer replicas with no user-visible change. And reducing `-Xmx` reduces both the pod spec and the node count needed
- C) Reserved instances
- D) Cheaper regions

**Answer: B** — Rightsizing is usually 20–40% and needs no architectural change. Do it with measurement (per-service utilisation distribution), not with a guess, and keep 30% headroom for peaks.

---

**Q9. What is the standard cost of an unbounded retry or log volume?**
- A) None
- B) Retries multiply compute during degradation, which is exactly when compute is most expensive and least useful; verbose logging multiplies storage and egress. Both are cost incidents that look like performance problems
- C) Only egress
- D) Only storage

**Answer: B** — Bound retries (≤10% of volume), sample high-volume success logs, and set `logback`/`log4j2` rotation with size caps. Also cap the payload you send to log aggregators.

---

**Q10. How do you attribute cost to a team or service reliably?**
- A) By guessing from cluster names
- B) With per-service cost tags: Kubernetes labels surfaced into the billing export (cost allocation tags), plus shared-cost allocation rules (ingress, control plane, NAT, log storage) apportioned by a stated basis. Without tags you cannot prioritise, and you can only cut indiscriminately
- C) By CPU share only
- D) By counting namespaces

**Answer: B** — CPU-share attribution is a reasonable approximation for compute but badly misprices services with large memory footprint, heavy egress, or expensive dependencies. Start with it, then refine.

---

**Q11. Why is memory footprint often the biggest JVM cost lever, given most services are CPU-bound?**
- A) It is not
- B) Because memory is what determines how many pods fit per node. A pod with a 4 Gi request fits 15 per 64 Gi node; with a 2 Gi request, 30. So halving memory can halve the node count even if CPU is unchanged — and if the provider bills on requests, the memory request is billed directly
- C) Because GC is slow
- D) Because memory is more expensive per unit

**Answer: B** — This is the non-obvious answer and the one that surprises people: memory drives density, density drives node count, node count drives the bill.

---

**Q12. What is a "cost anomaly" alert, and why is it high value?**
- A) An alert on high CPU
- B) An alert on daily spend versus the expected baseline for that day-of-week/hour, with a threshold on the deviation. It catches a runaway release, a log-volume explosion, or an un-tagged environment long before the monthly bill arrives
- C) An alert on low utilisation
- D) An alert on discounts

**Answer: B** — A single alert on total spend, plus one per service/tag, catches the majority of real cost incidents. Combine with a per-service daily budget alert.

---

**Q13. Why do savings and reliability often conflict, and how do you sequence them?**
- A) They do not conflict
- B) Reducing replicas or headroom raises the failure-mode risk. The correct order is: measure, remove waste (idle, over-requested, unbounded logs/retries), then rightsize with headroom, then optimise architecture, and only then consider reducing headroom — and never reduce headroom without a failure test
- C) Savings always hurt reliability
- D) Reliability costs nothing

**Answer: B** — Waste removal is nearly free. Headroom reduction is a risk decision and must be tested (Lab 18). Never skip from step 1 to step 4.

---

**Q14. What is the honest unit of cloud cost for a business?**
- A) Monthly spend
- B) Cost per unit of business volume (per order, per request, per GB processed, per active customer), plus the contribution margin impact. Monthly spend is a lagging indicator and rewards under-investing in reliability
- C) Cost per engineer
- D) Cost per cluster

**Answer: B** — Spend went up 10% and volume went up 40%; that is a success. Only a per-unit metric distinguishes optimisation from starvation.

---

**Q15. The single most common reason cost optimisation programmes fail is?**
- A) Engineers do not care about money
- B) No attribution, so nobody can tell whether a change helped; and no baseline, so the saving cannot be proved. Cost work without per-unit metrics and tags produces opinions rather than results
- C) Tools are expensive
- D) Vendors do not offer discounts

**Answer: B** — Measure before, measure after, attribute to a team, and report per-unit. Every other technique depends on those four things.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and find real savings.
- 12–10: revisit utilisation vs allocation, node density, and attribution; redo EXERCISES 2–5.
- <10: re-read THEORY + `FINOPS_SPOT_INTERRUPTION_DAEMON` cold and retake in 48 hours.
