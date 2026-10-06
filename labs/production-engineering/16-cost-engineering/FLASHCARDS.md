# Lab 16: Cost Engineering & Cloud Optimization — Flashcards

~60 cards. Most answers are a percentage, a control, or a measurement.

---

## Where the money goes

Q: Typical cost split for a JVM platform?
A: Compute largest, then data transfer/egress, then storage (managed DBs and object storage scale fast), then managed services (Redis, Kafka, search), then NAT/ingress/observability. Get your own split from the billing export — do not assume.

Q: Utilisation vs allocation?
A: Utilisation = used; allocation = reserved. You pay for allocation. A pod at 15% CPU on a 2 vCPU request is 85% waste.

Q: The most useful cost dashboard?
A: The distribution of `actual / requested` per service. Not average CPU. It shows exactly where rightsizing pays.

Q: Common recoverable waste?
A: Over-requested pods, 24/7 dev/staging, replicas running for off-peak, unattached volumes, verbose logging, runaway retries, forgotten test infrastructure, cross-region traffic you did not mean to have.

Q: Idle environments: typical share of a platform bill?
A: Frequently 15–25%. Quantify yours first; it is usually the easiest win.

---

## Rightsizing

Q: First thing to right-size?
A: `requests` (CPU and memory), not limits. Requests drive both the bill (in request-billed providers) and scheduling density.

Q: Does your provider bill on requests or usage?
A: Establish the fact per service and per resource type. It changes the entire strategy — and it differs between on-demand, spot, and committed-use pricing in some providers.

Q: Why does memory footprint matter for a CPU-bound service?
A: Memory determines pods-per-node. Halving the memory request can halve the node count with identical CPU.

Q: Node memory headroom rule?
A: A node cannot allocate 100% of RAM (OS + kubelet + eviction headroom). Typically reserve ~10–15%; so `Σ requests ≤ allocatable × 0.85` is the practical planning number.

Q: How much headroom after rightsizing?
A: Keep ~30% for peaks and for `maxSurge` during rollouts. Rightsizing to 100% utilisation is a latency and availability regression.

Q: Rightsizing without measurement?
A: Do not guess from "it looks light". Use a full peak week of per-pod CPU and memory, take p95, and set the request from that.

Q: JVM heap vs pod memory?
A: The pod request must cover heap + native. Reducing heap where the working set is small reduces the pod size — measure the live set after full GC first.

Q: Limits and cost?
A: Usually not billed directly, but limits constrain what the pod can burst to. If a limit is too low, you get throttling and OOM-kills, which cost more than the memory.

---

## Scheduling & density

Q: Density arithmetic?
A: `Σ (pods per node × requests) ≤ allocatable × 0.85`. Exceeding it means more nodes and, eventually, unschedulable pods (Lab 07).

Q: Cost of over-requesting beyond the bill?
A: Fewer pods per node → more nodes, and a node that cannot schedule anything useful. It is a cost *and* a resilience problem.

Q: HPA min replicas at 0?
A: Reduces cost for spiky services but adds cold-start latency and, for JVM services, a real warmup. Use it only where the cold start fits the SLO (often with a "wake" ping for reviewers).

Q: Cluster autoscaler behaviour?
A: It scales nodes from pending pods; it does not remove empty nodes unless configured to. Verify node removal policy, or you pay for idle nodes.

Q: Pod disruption budgets and cost?
A: PDBs can block cluster scale-down, leaving nodes paid for but empty. Check the interaction with your autoscaler at your minimum replica count.

---

## Spot / preemptible

Q: Correct workloads for spot?
A: Batch, CI runners, preview environments, async consumers with idempotency + DLQ, and non-production. Never singletons, latency-critical paths without replicas, databases without multi-AZ replication.

Q: Spot price behaviour?
A: Spot prices are tied to available capacity, so a shortage raises the price and can hit the cap. Diversify across instance families, sizes, and AZs to decorrelate interruptions.

Q: Interruption handling?
A: A SIGTERM with ~2 minutes' notice on most providers. Handle it like graceful shutdown (Lab 07): deregister, finish in-flight, checkpoint consumer offsets, exit. On restart, resume from the committed offset.

Q: Risk of interrupting a Kubernetes consumer mid-batch?
A: Duplicate processing of the in-flight batch — which idempotency already handles. This is why at-least-once plus idempotent consumers makes spot safe for consumers.

Q: Savings-commitment / reserved pricing?
A: Buys a discount in exchange for commitment and less flexibility. Right for steady baseline production, wrong for bursty or short-lived workloads.

---

## JVM-specific

Q: Does the JVM version affect cost?
A: Yes — throughput per CPU varies by release and by collector. Measure `CPU-seconds per request`; a GC change that cuts allocation can cut CPU per request materially.

Q: GC choice and cost?
A: Lower pause targets can cost throughput (more frequent, shorter collections and more CPU). For cost, minimise allocation rate first; a lower allocation rate wins on both latency and cost.

Q: Heap vs native memory and cost?
A: Both are billed if requests include them, but heap determines the maximum useful heap. Setting `-Xmx` far above the live set wastes billed memory and lengthens GC scans in some collectors.

Q: `-XX:MaxRAMPercentage` and cost?
A: Sizing from the limit keeps the ratio explicit, but the limit itself should come from the measured live set + native overhead, not from a template.

Q: Metaspace and code cache?
A: Native and inside the pod's memory budget. Large dynamic class loading (proxies, dynamic SQL) inflates metaspace — a cost and an OOM risk.

Q: JVM flags that cost money?
A: Excessive heap (memory request), `-XX:+AlwaysPreTouch` on long-lived services (RSS up front — actually a *saving* on a request-billed provider because it removes page-fault CPU), and diagnostics enabled permanently (`NativeMemoryTracking=summary` has a small cost; keep it off in the highest-scale services if it matters).

---

## Traffic-shaped costs

Q: Egress: when is it the biggest cost?
A: API-heavy platforms, multi-region, or anything serving large payloads/responses. Cross-AZ traffic can be billed too — check your provider's data-transfer matrix.

Q: Reducing egress?
A: Compression, response caching, CDN for static and cacheable content, and staying in-region. Each is a design decision with a latency benefit as well.

Q: Ingress/LB cost?
A: Per-request or per-hour. Batching (fewer, larger requests) helps on per-request pricing and usually helps latency too.

Q: Log storage and egress?
A: Verbose logging at 2,000 rps is a storage and egress cost. Sample successes, keep errors, cap retention, and cap the payload.

Q: Metrics cardinality and cost?
A: Every series costs storage and RAM in the monitoring system, and a cardinality explosion can cost more than the service. Bound labels (Lab 08).

---

## Managed services

Q: Managed Redis/Kafka/Postgres costs?
A: Often dominated by idle capacity (provisioned replicas) and storage growth (no retention on logs/tables). Right-size instance classes and set retention/data lifecycle policies.

Q: Data lifecycle?
A: Object storage tiers + lifecycle policies (transition to infrequent access, expire after N days). Log retention and table/volume growth are the usual silent consumers.

Q: Replicas you pay for and do not use?
A: Read replicas with no read traffic; standby nodes for a small system; cross-region replicas for a single-region workload. Each is a fixed monthly cost with zero benefit until needed.

Q: Serverless/autoscaling for uneven traffic?
A: Good for spiky, low-duty-cycle work; for a steady high-throughput Java service, provisioned capacity is usually cheaper per request. Compare cost per million requests, not cost per hour.

---

## Process

Q: Attribution: how?
A: Kubernetes labels surfaced as cost-allocation tags in the billing export, plus a stated allocation rule for shared costs. Without tags you cannot prioritise.

Q: Approximate attribution by CPU share — acceptable?
A: For a first pass, yes. It misprices services with large memory footprint or heavy egress, so refine once tags exist.

Q: Unit of cost?
A: Cost per business volume — per order, per API call, per GB. Monthly spend is lagging and rewards under-investing in reliability.

Q: Cost anomaly alert?
A: Daily/hourly spend versus the expected baseline for that day-of-week, with a deviation threshold. Catches runaway releases and log explosions days before the bill.

Q: Per-service budget alerts?
A: Yes — a daily budget per team/service with a warning and a hard alert, and a defined action (someone must explain it).

Q: Who owns cost?
A: Engineering owns efficiency; finance/platform owns visibility, tags, and the commitment strategy. Both, or nobody optimises anything.

Q: Sequence of cost work?
A: Measure → attribute → remove waste (idle, over-request, unbounded logs/retries) → rightsize with headroom → optimise architecture (caching, batching, async) → consider reducing headroom (with failure tests).

Q: What never to cut?
A: Observability, backups, and tested failover. Cutting them trades a monthly cost for an unbounded tail risk.

---

## Numbers and defaults to memorize

Q: Node memory planning headroom?
A: `Σ requests ≤ allocatable × 0.85` (OS/kubelet/eviction).

Q: Rightsizing headroom?
A: ~30% above p95 usage, and always room for `maxSurge`.

Q: Spot interruption notice?
A: ~2 minutes on most providers (SIGTERM). Verify for yours.

Q: Retry budget cap?
A: ≤10% of request volume.

Q: Typical logging savings from sampling?
A: 50–100× on success-path volume; keep 100% of errors.

Q: Log retention tiers?
A: Hot 7–14 d, warm 30–90 d, cold longer; set a lifecycle policy, not "forever".

Q: Target utilisation for a latency-critical Java service?
A: 60–70% of request at peak — the cost of a much bigger instance is worse than the cost of the tail.

Q: Idle dev/staging shutdown?
A: Nights and weekends by default; scale-to-zero plus a wake path for reviewers.

Q: Rightsizing target saving?
A: 20–40% of compute for a well-over-requested estate; 0% if already tight.

Q: Cost allocation granularity?
A: Per service (and ideally per team/environment), with a documented rule for shared costs.
