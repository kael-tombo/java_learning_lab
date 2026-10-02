# COST_REALITY — Worked Azure bill at 3 scales

Same lab-53 catalog service on Azure. All figures are worked examples using representative Azure list-price shapes (verify against the current pricing calculator before committing) — the *method* (split AKS vs Container Apps, stack reservations + saving plans, price observability ingest) transfers even as unit prices move. Assumes East US / West Europe class region, Linux nodes, 730 hrs/month.

Pricing assumptions used below (round, documented, adjustable): AKS management free, user pays nodes — D8as v5 (8 vCPU/32 GB) ≈ $300/mo on-demand; App Gateway v2 ≈ $140 fixed + ~$30 per capacity unit; Flexible Server GP D4ds (4 vCPU/16 GB) zone-redundant ≈ $450/mo + storage $0.115/GB-mo + backup; Azure Cache for Redis Premium P1 ≈ $400/mo (Basic C1 ≈ $50 for small); Service Bus Premium ≈ $700/messaging-unit (Standard ≈ $10 + ops for small); Event Hubs Standard ≈ $25/TU + capture storage; Monitor ingest ≈ $2.8/GB after 5 GB free, retention beyond 90 days extra; ACR Basic ≈ $5/mo; egress ≈ $0.087/GB first 10 TB.

---

## Scale A — Side project (1 service, 1 zone-ish, ~50 req/s peaks)

| Line item | Config | $/mo |
|---|---|---|
| Compute | Container Apps only: 1–3 replicas × 2 vCPU/4 GB, ~1.5 avg replicas + idle-to-1 | ~$60 |
| Ingress | Container Apps managed ingress (no App Gateway) | $0 |
| PostgreSQL | Flexible Server Burstable B2s, 100 GB, 7-day backup, no HA standby | ~$70 |
| Redis | Basic C1 (or drop cache; DB handles it at this scale) | ~$50 |
| Messaging | Service Bus Standard ($10) + ops (~$5) | ~$15 |
| Observability | App Insights ~10 GB/mo (~5 GB free) + 30-day retention | ~$15 |
| Registry + misc | ACR Basic, Key Vault ops, bandwidth (<100 GB) | ~$15 |
| **Total** | | **~$225/mo** |

No reservations, no saving plans — everything pay-as-you-go. Cheapest correct move at this scale: stay on Container Apps + Burstable, skip App Gateway and HA standby until revenue justifies them.

## Scale B — Growing SaaS (3 services, 3 zones, ~2k req/s, 99.9% SLO)

| Line item | Config | $/mo on-demand |
|---|---|---|
| AKS (steady API) | 6 × D8as v5 across 3 zones (2/zone), ~70% allocatable used | ~$1,800 |
| Container Apps (spiky webhooks) | 0–10 replicas, avg ~2 × 2 vCPU | ~$120 |
| App Gateway v2 + AGIC | Fixed + ~3 capacity units avg | ~$230 |
| Flexible Server | GP D4ds zone-redundant HA + 500 GB + PITR 30-day | ~$650 |
| Redis | Premium P1 (persistence + replication) | ~$400 |
| Service Bus | Premium 1 MU (sessions + private networking) | ~$700 |
| Event Hubs | 2 TU + Capture to storage | ~$80 |
| Monitor + App Insights | ~300 GB ingest/mo | ~$830 |
| ACR + Key Vault + egress (~2 TB) | Premium for geo-replication, ~2 TB out | ~$230 |
| **On-demand total** | | **~$5,040/mo** |

**Commitment stacking (only on the proven-steady slice):** AKS nodes are ~60% steady (baseline 4 nodes run 24/7) → 1-yr Reserved Instances on 4 × D8as v5 (~35% off ≈ −$420/mo). Flexible Server primary compute steady → 1-yr reservation (~30% off compute ≈ −$120/mo). Remainder (burst nodes, Container Apps, Gateway, messaging units) stays pay-as-you-go. **Committed total ≈ $4,500/mo (−11%).** Azure Saving Plan (compute) can substitute/combine where RI coverage is awkward (mixed SKUs) — stack rule: RI for the single-SKU steady core, saving plan for the fungible compute remainder, never both on the same hours.

## Scale C — Platform (12 services, multi-zone, ~25k req/s, 99.9%+ SLO)

| Line item | Config | $/mo on-demand |
|---|---|---|
| AKS (steady) | 40 × D8as v5 (system + user pools, ARM Cobalt mix where benchmarked) + 10 spot batch nodes (~70% discount, excluded from serving) | ~$12,000 + ~$900 spot |
| Container Apps (spiky slices) | Avg ~15 × 2 vCPU | ~$900 |
| App Gateway v2 (2 instances, autoscale) | Fixed × 2 + ~10 CU | ~$580 |
| Flexible Server | GP D16ds HA + 2 TB + read replica + 35-day PITR | ~$2,800 |
| Redis | Premium P3 cluster (3 shards) | ~$1,800 |
| Service Bus | Premium 4 MU (multi-tenant sessions) | ~$2,800 |
| Event Hubs | 10 TU + Capture + extended retention | ~$450 |
| Monitor + App Insights | ~2 TB ingest/mo (the line item everyone underestimates) | ~$5,500 |
| ACR + Defender + egress (~15 TB) | | ~$1,600 |
| **On-demand total** | | **~$29,330/mo** |

**Commitment stacking:** ~65% of AKS user-pool nodes steady → 1-yr RIs (~35–40% off ≈ −$3,200/mo); Flexible Server + Redis steady compute → reservations (≈ −$900/mo); compute saving plan over the Container Apps + burst remainder (≈ −$200/mo). **Committed total ≈ $25,000/mo (−15%).** 3-yr terms deepen the cut (~50–55% off covered hours) only if the 4-week trailing utilization proves the floor — otherwise the "saving" is a donation.

---

## The Monitor/Insights ingest lesson (all scales)

Observability is the stealth majority at Scale C (~19% of the bill) and the classic surprise at Scale B (~16%). Three controls, in order of leverage:

1. **Sample aggressively:** App Insights adaptive sampling + head-based OTel sampling (keep 100% of errors/slow traces, 5–10% of healthy 200s). Cutting ingest from 2 TB to 800 GB saves ~$3,300/mo at list — more than any reservation on the data tier.
2. **Log at the right level:** JSON `INFO` per request is a billing choice, not a default. Debug fields (headers, full payloads) go to short-retention diagnostic tables, not the default Log Analytics workspace.
3. **Retention tiers:** 30–90 days hot for incident work, then archive/export (storage account, ~$0.02/GB-mo) for compliance. Keeping 2 TB at full retention doubles the line.

## AKS vs Container Apps split — the rule

| Workload shape | Home | Why |
|---|---|---|
| Steady API, 24/7, zone-spread, custom networking/CNI | AKS | Node-hour economics win above ~60% utilization; full KEDA + AGIC control |
| Spiky webhooks, cron fan-out, cold-tolerant slices | Container Apps | Scale-to-near-zero + per-second billing; native/CRaC images cut cold starts |
| Tariff-shaped single triggers | Functions | Never the steady API (THEORY.md §1) |

Measure the crossover with the MINI_PROJECT 7-day tagged bill: if a slice averages < 25% replica utilization, it belongs on Container Apps; above ~60%, AKS nodes (reserved) win. Re-check quarterly — traffic shape drifts and takes the answer with it.
