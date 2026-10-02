# COST_REALITY — Monthly Bill Models for One Catalog API

Worked models for the lab-05 catalog API (Spring Boot 3, virtual threads, Postgres, JSON reads, p99 < 300 ms). Assumptions are stated so you can re-derive with *your* λ/W. Prices are approximate 2025–2026 list rates (on-demand, us-east-1-class regions; ARM ~15–20% below x86 where noted); your discounts, Savings Plans, and regions will move every number — the *shapes* and break-evens are what transfer.

**Shared assumptions:** mean latency W = 60 ms; per-pod capacity C ≈ 200 RPS at 1 vCPU/2 GiB (Little's-law concurrency ≈ 12 in flight — comfortable on virtual threads); replication ×2 minimum for availability; managed Postgres (db.r6g.large-class) ≈ $250/mo at small scale; observability (logs + metrics + traces) budgeted explicitly; egress priced at $0.09/GB cloud → internet (CDN ~$0.085/GB first 10 TB, cheaper at scale).

**Line items:** compute + memory (containers) + data (DB + cache + storage) + transfer (egress) + observability. Secrets/KMS/IAM noise (<$5) folded into observability.

---

## Scale A — Startup: 10 RPS average, 50 RPS peak, ~20 GB egress/mo

Needs: 1 pod normally, 2 for HA. 2 × (0.5 vCPU / 1 GiB) suffices; DB small; traces fully sampled.

| Line | AWS (ECS Fargate + RDS) | GCP (Cloud Run + Cloud SQL) | Azure (ACA + Flexible Server) |
|------|------------------------|----------------------------|-------------------------------|
| Compute | $35 (Fargate 1 vCPU-equiv cont.) | $25 (Run, scale-to-zero idle) | $30 (ACA consumption) |
| Data (PG + storage) | $250 (db.t4g.medium + 100 GB) | $230 (db-custom-1 + 100 GB) | $240 (B2ms + 128 GB) |
| Transfer (20 GB) | $2 | $2 | $2 |
| Observability | $30 (CloudWatch logs/metrics/X-Ray) | $25 (Cloud Logging/Trace) | $30 (App Insights) |
| **Total** | **≈ $317/mo** | **≈ $282/mo** | **≈ $302/mo** |

**Runtime verdict at 10 RPS:** Classic JVM. λ·S·mem·p waste is pennies (few scale events); native build complexity never pays back. Run the layered Dockerfile from CODE_DEEP_DIVE, `MaxRAMPercentage≈60%` at 1 GiB, min-replicas 1–2, scale-to-zero optional.

## Scale B — Growth: 1k RPS average, 5k RPS peak, ~5 TB egress/mo

Needs: ~6 pods avg (1k/200 + headroom), ~30 at peak; DB primary + replica + Redis; CDN mandatory (see scenario #2).

| Line | AWS | GCP | Azure |
|------|-----|-----|-------|
| Compute (avg ~6 × 1vCPU/2GiB, peak burst) | $450 (Fargate/EKS; −20% on Graviton) | $380 (Cloud Run / GKE Autopilot) | $420 (ACA/AKS) |
| Data (PG HA + replica + Redis + storage) | $900 | $850 | $880 |
| Transfer (5 TB, ~80% via CDN) | $400 | $380 | $390 |
| Observability (higher ingest, tail sampling) | $250 | $200 | $230 |
| **Total** | **≈ $2,000/mo** | **≈ $1,810/mo** | **≈ $1,920/mo** |

**Runtime verdict at 1k RPS:** Still JVM for the steady catalog core (6 warm pods amortize startup to zero); native or CRaC **only** for the bursty edges (webhook/deals handler, nightly report jobs) where λ·S·mem·p is large. CDN + signed URLs (scenario #2 fix) is worth more than any runtime switch — uncached 5 TB at full egress price would add ~$450 alone.

## Scale C — Scale: 50k RPS average, 150k RPS peak, ~200 TB egress/mo

Needs: ~300 pods avg (50k/200 + 20% headroom), 900+ at peak; sharded/pooled Postgres (PgBouncer), multi-AZ + read replicas; multi-CDN; committed-use/Savings Plans assumed (−30–40% compute vs on-demand).

| Line | AWS | GCP | Azure |
|------|-----|-----|-------|
| Compute (300 × 1vCPU/2GiB equiv, ARM, committed) | $18,000 | $16,000 | $17,000 |
| Data (Aurora/AlloyDB/large flexible + replicas + Redis cluster) | $12,000 | $11,000 | $11,500 |
| Transfer (200 TB via CDN + private backbone tuning) | $12,000 | $11,000 | $11,500 |
| Observability (tail-sampled traces, aggregated logs) | $3,000 | $2,500 | $2,800 |
| **Total** | **≈ $45,000/mo** | **≈ $40,500/mo** | **≈ $42,800/mo** |

**Runtime verdict at 50k RPS:** Mixed fleet. Steady catalog reads stay JVM (often ZGC — see BIG_TECH_FEEDBACK.md #3) on ARM: at this scale a 15% ARM saving ≈ $2.5k/mo, dwarfing build tooling costs. Native images earn their place on autoscaled spike capacity (faster scale-out = fewer over-provisioned warm pods) and CRaC on batch/scheduled paths. Full-native for the *steady* core rarely pays: closed-world maintenance (reflection config per release) costs engineering time against a startup term that is already amortized.

---

## Break-even rules (JVM vs native vs CRaC)

1. **Steady services (utilization > 40%): JVM wins.** Startup cost ≈ 0 after warm-up; engineering effort goes to rightsizing (f per limit), ARM migration, and DB/transfer instead.
2. **Bursty / scale-to-zero (spike ratio > 10×, idle > 50% of time): native or CRaC wins** iff monthly savings `λ_spike·(S_j − S_n)·mem·p + idle_mem_savings` exceed the build-pipeline cost (native CI minutes, reflection-config maintenance, CRaC snapshot plumbing). At Scale A this is ~$5–20/mo savings vs hours of pipeline work — no. At Scale C spike tiers it is $1k+/mo — yes.
3. **CRaC beats native when** the service needs full JVM dynamism (agents, reflection-heavy libs, JFR always-on) *and* fast restore; **native beats CRaC when** memory footprint (½ RAM) dominates or the platform bills strictly per-ms with tiny memory (functions).
4. **Transfer beats everything:** above ~1 TB/mo, every architecture review starts with bytes (CDN, compression, pagination, presigned URLs) before runtimes. A missed CDN at Scale B costs more than the entire compute tier.

## How to re-derive for your service

1. Measure your λ (avg + p99 spike), W (mean + p99), and GB-out/mo from current traces/logs.
2. Pods_avg = λ_avg·W/C_per_pod + HA floor; pods_peak likewise; price with your region's per-vCPU-GB-s.
3. Add data (instance class + IOPS + backup retention + replica count) and observability ingest (GB logs + trace spans after sampling).
4. Compute the cold-start term λ·S·mem·p for each runtime; the winner is the one whose *total* (bill + engineering hours × loaded cost) is lowest.
