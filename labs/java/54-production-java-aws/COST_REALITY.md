# COST_REALITY — Worked AWS bill for the catalog API at 3 scales

Topology priced: EKS + ALB + Aurora PostgreSQL Multi-AZ + ElastiCache Redis + MSK **vs** SQS variant, CloudWatch/X-Ray, ECR, Secrets Manager. Region: us-east-1. Prices are public-list approximations rounded for planning (re-check before budgeting — AWS changes them; your discounts/commitments change them more). The *shape* (which line dominates at each scale) matters more than any single number.

Assumptions shared across scales: 3 AZ, private subnets, `minReplicas: 3`, ALB health on readiness (2×15 s / 2×5 s), Aurora backup retention 7 d (PITR), Redis TLS+AUTH single-shard with replica, log retention 30 d, cost tags `service=catalog-api,env=prod`.

---

## Scale definitions

| | Dev / staging | Production baseline | 100× spike (event day) |
|---|---|---|---|
| HTTP | ~10 RPS avg, p99 150 ms | ~2,000 RPS avg, p99 150 ms (HPA math: 2,000×0.15/(200×0.7) ≈ 3 pods min, max 20) | ~200,000 RPS peak for 6 h |
| Events | 10 msg/s | 1,200 msg/s price updates | 120,000 msg/s |
| Data | 10 GB DB, 1 GB cache | 500 GB DB, 50 GB cache | 2 TB DB, 200 GB cache |
| Egress | 50 GB/mo | 20 TB/mo | 500 TB event-month (CDN offload assumed below) |

---

## Worked monthly bill (MSK variant vs SQS variant)

### A. Dev / staging (~10 RPS)

| Line | MSK variant | SQS variant |
|---|---|---|
| EKS control plane ($0.10/h) | ~$73 | ~$73 |
| Compute: 2× `m7g.large` on-demand (2 vCPU/8 GB) | ~$135 | ~$135 |
| ALB (base + low LCU) | ~$25 | ~$25 |
| Aurora Serverless v2 (2–4 ACU avg, 10 GB, low I/O) | ~$90 | ~$90 |
| ElastiCache `cache.m7g.large` + replica (or serverless micro) | ~$110 | ~$110 |
| MSK: 3× `kafka.m7g.large` + 300 GB storage | ~$260 | — |
| SQS + SNS (~26 M req/mo) | — | ~$12 |
| CloudWatch (metrics + 5 GB logs + traces) | ~$30 | ~$30 |
| ECR + Secrets Manager + transfer (50 GB) | ~$15 | ~$15 |
| **Total** | **~$740/mo** | **~$490/mo** |

Takeaway: at dev scale MSK is ~50% of the bill for 10 msg/s — the SQS variant wins outright. Matches ARCHITECTURE.md: no replay need → no brokers.

### B. Production baseline (~2,000 RPS, 1,200 msg/s)

| Line | MSK variant | SQS variant |
|---|---|---|
| EKS control plane | ~$73 | ~$73 |
| Compute: 6× `m7g.xlarge` (4 vCPU/16 GB), ~60% util | ~$830 | ~$830 |
| ALB (moderate LCU: conns + bandwidth + rules) | ~$120 | ~$120 |
| Aurora: `db.r7g.large` writer + 1 reader, 500 GB, I/O-Optimized | ~$650 | ~$650 |
| ElastiCache: 2× `cache.m7g.xlarge` (shard + replica), 50 GB | ~$450 | ~$450 |
| MSK: 3× `kafka.m7g.xlarge` + 1 TB storage | ~$750 | — |
| SQS + SNS (~3.1 B req/mo @ $0.40/M ≈ $1,240 + FIFO/DLQ overhead) | — | ~$1,350 |
| CloudWatch (200 metrics + 100 GB logs + X-Ray 50 M traces sampled to 5%) | ~$180 | ~$180 |
| ECR + Secrets + inter-AZ + egress 20 TB (~$0.09/GB blended) | ~$1,850 | ~$1,850 |
| **Total** | **~$4,900/mo** | **~$5,500/mo** |

Takeaway: near breakeven on messaging — MSK ~$750 flat vs SQS ~$1,350 usage-priced. Either is defensible; replay/compaction need decides (QUIZ §7), not price.

### C. 100× event day (6 h at 200k RPS; monthlyized steady + event burst)

Steady-state grows ~10× (20k RPS sustained needs ~30 `m7g.2xlarge` + Aurora `r7g.2xlarge` ×3 + larger cache ≈ $28k/mo MSK variant). Event burst adds:

| Burst line (6 h) | MSK variant | SQS variant |
|---|---|---|
| Burst compute (Spot + HPA to 200 pods) | ~$900 | ~$900 |
| ALB LCU spike | ~$250 | ~$250 |
| Aurora I/O + read-replica burst | ~$400 | ~$400 |
| MSK scale-out (6 brokers, extra storage) | ~$300 | — |
| SQS burst (~2.6 B requests in 6 h) | — | ~$1,050 |
| Egress burst (~15 TB in 6 h) | ~$1,350 | ~$1,350 |
| **Event-month total (steady + burst)** | **~$31k** | **~$32k** |

Takeaway: at spike scale the messaging choice is noise — **egress + compute dominate**. Which is the real lesson (next section).

---

## Graviton vs x86 (measured, not marketed)

Lab-53 benchmark matrix rerun on equal pod specs (`m7g.xlarge` vs `m7i.xlarge`, JDK 17.0.latest, G1, `MaxRAMPercentage=75`):

| Metric | m7i (x86) | m7g (Graviton) | Delta |
|---|---|---|---|
| Sustained throughput (2k-RPS mix) | 100% (baseline) | 102–105% | neutral-to-better |
| p99 at 5× baseline | 185 ms | 170 ms (after JDK/crypto fix) | −8% |
| p99 with **stale JDK** (pre-ARM-intrinsics) | 185 ms | ~450 ms TLS-heavy | **+140% (the §5 incident)** |
| Price per vCPU-hour (on-demand) | $0.192 | $0.154 | **−20%** |
| **Cost per 1 M requests** | ~$0.42 | ~$0.34 | **−19%** |

Rules: (1) never migrate on list price — rerun EXERCISES §5 (throughput + p99 + $/M-req, peak TLS mix, current JDK); (2) pin and review the JDK micro version with the flags (BIG_TECH_FEEDBACK JVM section); (3) keep mixed-arch node groups during validation so rollback is a reschedule. Savings bank on every scale above because compute is 15–25% of the bill — roughly $150/mo (dev), $170/mo (baseline), $5k+/mo (event scale) for this service alone.

---

## Data-transfer dominance analysis (the line that eats the bill)

At production baseline, **egress + inter-AZ transfer (~$1,850) exceeds compute (~$830) and exceeds Aurora + Redis combined (~$1,100)**. At event scale it is ~40% of the total. Five knobs, ordered by leverage:

1. **Cache at the edge (10–50×):** CloudFront in front of `GET /products/*` + ElastiCache for category pages. Every 10% hit-rate shift at 20 TB/mo ≈ $180/mo; at 500 TB ≈ $4,500. Biggest lever, by far.
2. **Payload discipline (2–5×):** paginate + field selection (`?fields=`), gzip/Brotli, thumbnail-vs-full image URLs (serve bytes from S3/CloudFront, never through the API pods). 1 MB → 200 KB average response halves the transfer line.
3. **Regional affinity:** keep EKS ↔ Aurora ↔ Redis ↔ MSK in the same region/AZ-aware routing; cross-AZ traffic ($0.01/GB) and cross-region replication are silent multipliers — 1,200 msg/s × 2 KB × 3 AZ-fanout ≈ 600 GB/mo before anyone notices.
4. **ALB LCU hygiene:** LCU blends new connections + active connections + bandwidth + rule evaluations — HTTP keep-alive (reuse conns), fewer listener rules, and connection-draining tuned to `deregistration_delay` cut LCU without touching code.
5. **Observability sampling:** unsampled X-Ray at 200k RPS (≈ TBs of spans) costs more than the MSK cluster; sample 1–5% at peak, 100% only on error paths. Same for DEBUG logs — log volume is transfer + ingestion + storage triple-charged.

**Budget rule to take home:** tag every stack (`service/env/owner`), alert on week-over-week delta > 15% (MATH_FOUNDATION §3), and review the bill by *transfer first, compute second, Datastores third* — the rank order surprises every team exactly once.
