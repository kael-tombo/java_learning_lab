# BIG_TECH_FEEDBACK — Microsoft / LinkedIn / GitHub / Stack Overflow lessons

Quotable principles from how the Microsoft-ecosystem hyperscalers actually run Java and .NET-adjacent production estates — safe deployment (ExP rings), Entra federation at scale, Postgres-vs-SQL-Server calls, and on-call health. Each principle states the rule, the reasoning, and the Azure-Java application.

---

## 1. Safe deployment: ring it or regret it

> "If it isn't ringed, it isn't shipped." — paraphrase of Microsoft ExP (Experimentation Platform) safe-deployment practice

**Reasoning.** Microsoft deploys via concentric exposure rings (Ring 0: internal dogfood → early tenants → broad regions), each gated on health signals before the next opens. LinkedIn's deploy windows and GitHub's progressive delivery encode the same law: blast radius is a *budgeted quantity*, not a hope. A single "roll to all zones at once" step converts any config typo (see PRODUCTION_SCENARIOS.md §1, the probe incident) into a global event.

**Application.** AKS rollouts in this lab use `maxUnavailable: 0` + AGIC health gating per batch, then promote the same image across Deployment-Stack environments (dev → canary region/subscription → prod) with burn-rate alerts as the ring gate. Container Apps revisions serve as cheap Ring-0 slices for spiky endpoints.

## 2. Health gates beat human judgment at 2 a.m.

> "Automate the rollback decision; humans confirm the rollout decision." — SRE norm across Microsoft and LinkedIn on-call cultures

**Reasoning.** Microsoft's safe-deployment pipelines auto-halt on SLO regression (availability, latency, throttling) without waiting for a human to interpret dashboards. LinkedIn's on-call reviews repeatedly found that "wait and see" during a burn costs more than an automatic revert. Alert-on-symptoms (burn rate, healthy-host count, DLQ growth) rather than on causes.

**Application.** Azure Monitor burn-rate alerts auto-pause the Deployment Stack rollout (pipeline gate), App Gateway healthy-host-count drop pages immediately, and every deploy carries a rollback bundle (previous image + reversibility proof) per THEORY.md §4 — tested by the MINI_PROJECT rollback drill, not trusted on paper.

## 3. Entra federation at scale: trust is infrastructure, not setup

> "Every secret you store is a breach you scheduled." — Microsoft identity guidance behind workload identity federation

**Reasoning.** At Microsoft/LinkedIn scale, client secrets and connection-string passwords are unmanageable: rotation windows drift, vault replication lags, and one leaked secret fans out across regions. Entra workload identity federation replaces stored credentials with short-lived tokens bound to the cluster OIDC issuer — but the *binding itself* (issuer URL, subject claim) becomes load-bearing infrastructure. PRODUCTION_SCENARIOS.md §4 shows the failure mode: federation removes secret rotation and replaces it with trust-pointer management.

**Application.** Federated credentials live in Bicep next to the AKS resource (issuer wired by reference, never pasted), preflight checks assert issuer match before Flyway runs, and the EXERCISES.md §1 drill (break the trust, record the exact error, restore) is onboarding-required. Flexible Server Entra auth extends the same posture to the data plane: token-as-password, no DB passwords anywhere.

## 4. Postgres vs SQL Server: pick by workload shape, not by habit

> "Postgres for portable OLTP and open-source gravity; SQL Server where the enterprise contract (T-SQL surface, existing licensing, Always On tooling) already exists." — synthesis of Stack Overflow and Microsoft field guidance

**Reasoning.** Stack Overflow's public architecture writing documents the SQL Server → Postgres evaluation dimensions honestly: license cost vs operational familiarity, T-SQL stored-procedure surface vs portable SQL + Flyway, and managed-HA semantics (Always On availability groups vs Flexible Server zone-redundant standby). Microsoft's own guidance positions Flexible Server as the default for new cloud-native OLTP while keeping Azure SQL (SQL Server engine) for estates with deep T-SQL investment. The wrong call in either direction is expensive: rewriting stored procedures late, or paying per-core SQL licensing for a stateless catalog that Postgres serves identically.

**Application.** This lab defaults to Flexible Server PostgreSQL (zone-redundant HA + PITR, Entra auth, Flyway migrations, read replicas for analytics) precisely because the lab-53 catalog is portable OLTP with no T-SQL surface. The decision is recorded with its reversal condition: "revisit if stored-procedure or Always On requirements appear; until then Postgres + PgBouncer + PITR drill."

## 5. On-call health is a reliability control, not a perk

> "Pager fatigue is a leading indicator of a monitoring bug, not a staffing bug." — LinkedIn/Microsoft SRE consensus

**Reasoning.** LinkedIn's on-call health reviews and Microsoft's "learn from every page" culture converge: each page should be actionable, novel, and tied to a symptom-based alert. Pages caused by known scaler sawtooth (PRODUCTION_SCENARIOS.md §5), chronic hot sessions (§3), or unactionable CPU thresholds are monitoring defects — they train on-call to ignore the pager, which is how the next real zone-loss event gets missed. GitHub's incident reviews similarly track "pages per deploy" as a deployment-safety metric.

**Application.** This lab's alert set is symptom-first: burn-rate (availability/latency), App Gateway healthy hosts, PgBouncer `cl_waiting`, per-session backlog skew, scaler replica-hour anomalies — each with a runbook entry in REAL_WORLD_PROJECT.md. Weekly review asks three questions: was every page actionable, did any known condition page twice, and which alert should have fired but didn't. KEDA threshold and session-sharding fixes come out of this review, not out of heroics.

## 6. Cost is an architecture review input, not a finance afterthought

> "Untagged spend is undebuggable spend." — Microsoft FinOps practice (resource tags + Cost Management budgets as deploy artifacts)

**Reasoning.** Microsoft's internal FinOps and the Azure Cost Management model agree: per-service attribution (tags on every resource group, Budgets + anomaly alerts wired to the owning team) turns cost into a code-reviewable signal. Reservation and saving-plan purchases follow *measured-steady* baselines only (MATH_FOUNDATION.md §4) — buying down hoped-for load is repeatedly documented as the classic enterprise waste motion. LinkedIn's capacity planning makes the same point with utilization-gated commitments.

**Application.** Every resource in the lab's Bicep carries `service/env/owner` tags; the MINI_PROJECT 7-day tagged bill (AKS vs Container Apps split) is the reservation input, and COST_REALITY.md works the three-scale math showing exactly where reservations vs pay-as-you-go win.
