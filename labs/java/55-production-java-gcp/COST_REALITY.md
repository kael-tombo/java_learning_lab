# COST_REALITY — worked GCP bill at 3 scales (Java catalog API)

Pricing moves; the method doesn't. All figures are illustrative
(list-price order-of-magnitude, us-central1-ish, 730 h/mo) so the
Autopilot-vs-Standard-vs-Run tradeoff and the discount stack stay
auditable. Recompute with current list prices before committing; attach
the labeled 7-day bill (MINI_PROJECT step 4) as evidence.

Assumed service shape (from lab-53 profile): steady API slice + spiky
webhook slice, AlloyDB or Cloud SQL PG, Memorystore Redis, Pub/Sub
events, Cloud Monitoring/Trace ingest. Labels `service/env/owner` on
everything.

---

## 1. Compute split at 3 scales

Baseline sizing: API pod `1 vCPU / 2 Gi`; Run instance `1 vCPU / 1 Gi`,
concurrency 80.

### Hobby (dev, ~10 RPS, 2 pods, mostly idle)

| Line | Math | ≈ $/mo |
|---|---|---|
| GKE Autopilot (2 × 1vCPU/2Gi) | ~2 vCPU (~$0.0445/vCPU-h) + 4 Gi (~$0.0049/Gi-h) | ~$80 |
| Cloud SQL db-f1-micro + 10 Gi | instance + storage + 7-day PITR | ~$15 |
| Memorystore basic 1 Gi | smallest tier | ~$35 |
| Pub/Sub (~1M msgs) | first 10 Gi free-ish, negligible | ~$1 |
| Monitoring/Trace | under free ingest | ~$0 |
| **Total** | | **~$130** |

Lesson: at hobby scale the database + Redis floor dominates; Standard
nodes or Run-only would be cheaper but the HA/PITR shape is the point.

### Growth (~500 RPS steady + webhook spikes to 3K, 12 pods + Run)

| Line | Math | ≈ $/mo |
|---|---|---|
| Autopilot (12 × 1vCPU/2Gi) | 12 vCPU + 24 Gi × 730 h | ~$475 |
| …or Standard equivalent | 3× e2-standard-4 nodes (~$0.13/h) at ~65% binpack | ~$285 |
| Cloud Run webhook slice | avg 3 instances × 1 Gi, bursty 200 h-equiv | ~$25 |
| GCLB + egress | forwarding rules + ~2 TB | ~$60 |
| AlloyDB smallest HA (2 vCPU primary + replica) + 100 Gi + PITR | instance-hours + storage + backup | ~$450 |
| Memorystore 5 Gi standard | HA tier | ~$150 |
| Pub/Sub (~300M msgs, ~500 Gi) | publish/subscribe ops + transfer | ~$120 |
| Monitoring/Trace/Profiler | metrics + 50 Gi spans + profiles | ~$60 |
| **Total Autopilot path** | | **~$1,340** |
| **Total Standard path** | (~$190 saved on compute) | **~$1,150** |

Break-even check (MATH_FOUNDATION.md §1): Standard wins past ~60–70%
sustained binpack — growth scale with 12 steady pods clears it, hence
the ~$190 gap. Keep spiky webhooks on Run either way.

### Scale (~5K RPS, 60 pods, multi-service)

| Line | Math | ≈ $/mo |
|---|---|---|
| Standard (15× e2-standard-8, committed) | nodes before discount | ~$1,450 |
| Cloud Run slices | warm floors + bursts | ~$150 |
| GCLB + egress (~20 TB) | data-dominated | ~$500 |
| AlloyDB (8 vCPU + 2 read pools) + 1 Ti + PITR | instance + storage + backup | ~$2,200 |
| Memorystore 25 Gi cluster | sharded tier | ~$600 |
| Pub/Sub (~3B msgs, ~5 Ti) | ops + transfer | ~$900 |
| Observability (500 Gi spans, metrics) | ingest + retention | ~$350 |
| **Total before discounts** | | **~$6,150** |

## 2. Discount stacking (the order matters)

1. **Sustained-use discounts** (automatic): GCE-based Standard nodes
   running most of the month earn up to ~30% off — no action, but only
   helps always-on nodes, never Autopilot pods or Run.
2. **Committed-use discounts (CUDs)** (1- or 3-year): ~37–55% off
   committed vCPU/RAM for the proven-steady baseline. Buy only what
   Autopilot/Monitoring history proves steady for 3+ months
   (FLASHCARDS.md #14) — commit the 60-pod floor, not the spike headroom.
3. **Stacking rule:** CUDs apply first to committed usage; sustained-use
   covers the uncommitted remainder. Autopilot has its own committed
   options — compare against Standard+CUD before renewing.

Worked example (scale tier, Standard $1,450 compute):

```
Committed baseline (70% of nodes, 1-yr CUD ~37%):  $1,015 × 0.63 ≈ $640
Uncommitted remainder with sustained-use (~20%):    $435 × 0.80 ≈ $348
Effective compute: ≈ $988  (vs $1,450 list → ~32% saved)
New scale total: ≈ $5,700/mo
```

Never commit Pub/Sub, Trace, or egress — they scale with traffic and
carry no CUDs. Never commit the Run burst slice.

## 3. Pub/Sub + Trace ingest costs (the surprise lines)

**Pub/Sub:** charged per publish/subscribe/delivery operation + data
transfer. Ordering keys cost nothing directly but hot-key redeliveries
(PRODUCTION_SCENARIOS.md §2) double-charge: every redelivery is a
billed delivery. DLQ quarantine + replay of 10M duplicates ≈
10M extra deliveries (~$4–8 at list) plus the engineering day — cheap
in dollars, expensive in latency SLO. Size `maxDeliveryAttempts` and ack
deadlines to minimize redelivery, not just to quarantine poison.

**Cloud Trace:** charged per GiB of spans ingested + retention. A Java
OTel agent at 100% sampling on 5K RPS with chunky Spring spans can emit
200–500 GiB/mo (~$100–300). Standard controls:

- Head-based sampling 5–10% + tail-based capture of errors/slow traces.
- Drop health-check/readiness spans at the collector.
- Keep Profiler always-on (cheap, CPU-sampled) and Trace sampled —
  profiles find the hot method, traces find the slow hop.

Budget rule: observability ≈ 5–8% of compute at growth/scale. Past 10%,
sample harder before buying more ingest.

## 4. Review checklist (monthly, per REAL_WORLD_PROJECT.md)

- [ ] Labeled bill exported; Autopilot-vs-Standard recomputed from
      last 30 days of pod-request hours.
- [ ] Committed baseline still ≤ steady floor (no over-commit after
      the CRaC migration shrank requests).
- [ ] Pub/Sub redelivery ratio < 1% (else fix ack/deadline/key design).
- [ ] Trace ingest within budget; sampling policy in repo, not console.
