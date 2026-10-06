# Lab 09: AI Security — Real-World Project

## Project: Enterprise AI Security Program and Platform

Design and build the security program around an LLM platform: threat modelling,
layered guardrails, tenant isolation, supply-chain controls, a red-team programme with
intake, safety monitoring, incident response with drills, and the transparency artifacts
customers and auditors require.

## Context

Any LLM feature that touches untrusted content or takes actions is a security
boundary. This program exists to make that boundary explicit, tested, monitored, and
survivable when crossed.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Constitutional AI: Harmlessness from AI Feedback" (Bai et al., submitted 1 Dec 2022;
  rev. 21 Dec 2024) — https://arxiv.org/abs/2212.08073 — takeaway for this lab: a
  written constitution plus AI-generated critique and revision can replace human
  harmlessness labels at scale, which is how the safety preference pipeline here stays
  producible — and why the constitution is a versioned, reviewed system asset.
- "The Llama 3 Herd of Models" (Dubey et al., submitted 25 Apr 2024; v2 23 Jul 2024) —
  https://arxiv.org/abs/2407.21783 — takeaway for this lab: a production release
  documents its safety evaluation as a distinct system with per-category results and
  red-teaming methodology, which is the reporting structure this program reproduces.

## System Architecture

```
   untrusted traffic                    trusted configuration
  (user text, RAG docs,             (constitution, policy, tool
   tool output, images,               allowlist, thresholds,
   uploaded files)                     data classifications)
          |                                    |
   +------v-------------------------------------v------+
   |  L1 INPUT                                        |
   |  normalize | recursive decode | caps | limits   |
   +----------------------+----------------------------+
                          |
   +----------------------v----------------------------+
   |  L2 SYSTEM BOUNDARY                              |
   |  policy in the system message; untrusted data    |
   |  labelled; capability decided in code            |
   +----------------------+----------------------------+
                          |
   +----------------------v----------------------------+
   |  L3 TOOL GATE                                   |
   |  allowlist | read/write | schema | approvals    |
   |  side-effect caps | rate limits | breakers      |
   +----------------------+----------------------------+
                          |
   +----------------------v----------------------------+
   |  L4 OUTPUT GUARDRAILS (fail closed)             |
   |  schema | refusal | grounding | citations |    |
   |  PII scrub | policy | human review               |
   +----------------------+----------------------------+
                          |
                    +-----v------+   response
                    | RESPONSE   |
                    +-----+------+
                          |
   +----------------------v-------------------------------------------+
   |  L5 SECURITY OPERATIONS                                       |
   |  findings | abuse detection | canaries | attribution          |
   |  red-team suite | incident response | drills | audit (anchored)  |
   +--------------------------------------------------------------+

   SIDE CHANNELS
     constitution        -> critique and revision, versioned
     supply chain       -> pinned SHAs, checksums, dataset hashes
     transparency       -> safety card, policy disclosure, appeal path
```

## Component Specs

### 1. Threat Model and Asset Inventory
- Assets: user data, internal documents, credentials, system prompts, tool capabilities,
  brand and regulatory posture.
- Adversaries: curious user, malicious user, injector via our own data, exfiltrator,
  careless insider, compromised provider, poisoned corpus author.
- Trust boundaries enumerated, each with an owning team and a test.
- **New-surface review** triggered by any new data source, tool, or model provider.
- Abuse cases ranked by expected harm, each with a named owner and a red-team test.

### 2. L1 Input
- NFKC normalization, invisible and bidi stripping, control-character removal.
- **Recursive decode-and-classify** with a depth bound and cycle guard.
- Length caps per surface; rate limits per user and tenant.
- Findings returned as a typed list and written to the anchored audit log.
- PII handled at write, before logs exist.

### 3. L2 System Boundary
- Policy in the system message; untrusted content in the user message, wrapped, labelled
  as data, never concatenated into policy.
- **Privilege separation**: capability from the registry and gate. A model statement of
  permission is data.
- **Constitution**: a written, versioned principles document used for critique and
  revision and as the reference for the output critic. Review and version changes.
- Canary strings in the system prompt, tested at volume on every release.

### 4. L3 Tool Gate
- Per-role allowlists. Read-only roles have no write tools registered.
- Typed schemas with `additionalProperties: false`, enums, and patterns; validated in
  code before dispatch.
- **Argument-scoped approvals** with expiry; irreversible actions require one; timeout
  denies.
- Side-effect caps per task and session; circuit breakers per tool.
- Idempotency keys on writes; state verified before retry.
- Exfiltration defense: no tool returns raw secrets; secrets referenced, never embedded;
  canary detection on outputs.

### 5. L4 Output Guardrails
Eight stages, fail closed, each instrumented:
1. Length and format
2. Schema validation
3. Refusal appropriateness
4. Grounding verification, with numeric claims checked against extracted fields
5. Citation validity
6. PII and secret scrub, with re-scan
7. Policy classifier (harmful, self-harm, violence, illegal)
8. Human review queue for high-risk categories, with specialist reviewers

Every classifier exception or undecided result blocks.

### 6. L5 Security Operations
- Continuous signals: injection findings, refusals, escalations, abuse patterns,
  canary results, guardrail attribution.
- **Per-layer attribution** with the uncaught count published and tracked over time; a
  falling detection rate is an alert.
- **Red-team programme**: threat-modelled attack library, nightly automated mutation
  runs, monthly expert sessions, quarterly full assessment.
- **Intake SLA**: any user-reported or internally found bypass becomes a permanent test
  within one business day.
- **Triage** attributes to a layer; a fix without a test is incomplete.
- Disclosure after the fix ships.

### 7. Isolation and Data Protection
- Tenant-scoped caches, index namespaces, pre-filtered retrieval, tenant-tagged traces
  with retention, per-tenant training datasets with isolation tests in CI.
- Encryption in transit and at rest; data classification governing which models may see
  which data.
- DLP on exports and logs; retention by class with a metric; tenant deletion enforced.

### 8. Supply Chain
- Base models pinned by **commit SHA**; adapter and prompt-config checksums; dataset
  hashes recorded in provenance.
- Verification runs in CI so a moved tag fails the build, not the launch.
- Datasets scanned for poisoning and PII at ingest.
- Third-party prompts, guardrail configs, and adapters reviewed as code.

### 9. Incident Response
- Runbooks per alert with the first question, owner, decision tree, and **tested**
  containment.
- Containment menu: safe mode, disable a tool, disable retrieval, revoke credentials,
  scope a tenant, pin the previous version.
- Pre-written scope queries.
- Quarterly tabletop plus one technical drill measuring time-to-detect and
  time-to-contain.
- Post-incident review within a week; the new case enters the suite before closure.

### 10. Transparency and Governance
- Release gate: safety regression tolerance **zero**.
- Over-refusal regression beyond an agreed delta warns and requires sign-off.
- Published safety card with per-category results and methodology.
- Disclosure of what is blocked, what is logged, retention, and the appeal path.
- Data processing agreements and audit retention enforced.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Prompt injection success rate | <= 2% on the internal suite |
| Jailbreak success rate | <= 3% |
| Leakage (prompt, secrets, PII) | 0 |
| Unauthorized tool calls | 0 |
| Unapproved irreversible actions | 0 |
| Refusal on disallowed | >= 0.97 |
| Over-refusal on benign | <= 0.05 |
| New-bypass-to-test SLA | <= 1 business day |
| Time to detect (drill) | <= 15 min |
| Time to contain (drill) | <= 60 min |
| Cross-tenant leakage | 0 |
| Safety regression tolerance | 0 |
| Detection rate trend | Not declining |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Injection via our own RAG | Injection suite over real corpora | Privilege separation; data labels |
| Exfiltration via tool output | Canary; tool audit | No secrets in tools; arg-scoped approvals |
| Multi-turn assembly | Stateful accumulation | Session-level detection |
| Multimodal payload | OCR-based detection | Image text treated as data |
| Over-refusal harming users | Over-refusal metric | Category thresholds; ship the pair |
| New attack family bypasses | Nightly mutation runs | Intake SLA; adversarial retraining |
| Model moved under a tag | Provenance check in CI | Pin by commit SHA |
| Dataset poisoning | Ingest scanning | Dedupe, scan, review |
| Canary leakage | Canary suite at volume | Hard failure on any occurrence |
| Guardrail fails open | Stage instrumentation | Fail-closed design plus a test |
| Audit tampered | Anchor verification | External append-only anchoring |
| Incident too slow | Drill metrics | Pre-written queries; containment actions |
| Abuse blocks legitimate users | Throttle metrics | Throttle by default; escalate on intent |
| Safety regression from a tweak | CI safety gate | Zero tolerance block |

## Milestones

- **M1** — threat model, asset inventory, ranked abuse cases with owners.
- **M2** — new-surface review process and trust boundary inventory.
- **M3** — L1 input layer with recursive decoding.
- **M4** — L2 boundary with the constitution and canary infrastructure.
- **M5** — L3 tool gate with scoped registries and arg-scoped approvals.
- **M6** — L4 eight-stage pipeline, fail-closed, instrumented.
- **M7** — isolation: caches, indexes, traces, training data with CI tests.
- **M8** — supply chain: pinned SHAs, checksums, dataset hashes in CI.
- **M9** — red-team library, mutation harness, attribution reporting.
- **M10** — intake process and permanent-test conversion.
- **M11** — incident runbooks and the first technical drill.
- **M12** — release gate with zero safety tolerance.
- **M13** — transparency safety card published.
- **M14** — game day: live exfiltration simulation end to end.

## Deliverables

1. Threat model and abuse-case register.
2. Guardrail implementation across all five layers.
3. Isolation and supply-chain controls with CI tests.
4. Red-team library, mutation harness, and attribution reporting.
5. Runbooks and drill reports.
6. Safety card with per-category results and methodology.
7. `REPORT.md` — posture: what is blocked, what is accepted, what is planned, and the
   discovery-versus-fix sustainability metric.

## Definition of Done

- [ ] Zero leakage of prompts, secrets, or PII across 10,000 sampled requests.
- [ ] Zero unauthorized tool calls and zero unapproved irreversible actions.
- [ ] Safety regression blocks releases with zero tolerance, verified by a deliberate
      regression.
- [ ] Every found bypass is a permanent test within one business day.
- [ ] Time-to-detect and time-to-contain measured in a drill.
- [ ] Cross-tenant leakage zero across 10,000 randomized tests.
- [ ] Provenance verification fails the build on a moved tag.
- [ ] Safety card published with per-category results.