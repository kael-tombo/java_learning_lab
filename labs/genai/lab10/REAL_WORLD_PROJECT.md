# Lab 10: LLM Safety & Alignment — Real-World Project

## Project: Production Safety Platform for an LLM Application

Design and build the safety system a real product runs: layered guardrails, a red-team
program with an intake process, safety monitoring with anomaly detection, incident
response with drills, safety metrics integrated into the release gate, and
transparency artifacts.

## Context

Any LLM feature that touches untrusted content or takes actions is a security
boundary. The engineering job is to make that boundary explicit, testable, monitorable,
and survivable when it is crossed.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Constitutional AI: Harmlessness from AI Feedback" (Bai et al., submitted 1 Dec 2022;
  rev. 21 Dec 2024) — https://arxiv.org/abs/2212.08073 — takeaway for this lab: a
  written constitution combined with AI-generated critique and revision replaces
  human harmlessness labels on many items, which is what makes the safety preference
  pipeline here scalable — and why the constitution is treated as a versioned,
  reviewable system asset rather than a prompt string.
- "The Llama 3 Herd of Models" (Dubey et al., submitted 25 Apr 2024; v2 23 Jul 2024) —
  https://arxiv.org/abs/2407.21783 — takeaway for this lab: a production-scale release
  documents its safety evaluation as a distinct system with its own metrics, red-teaming
  methodology, and per-category results — the reporting structure this platform
  reproduces for its own release gate.

## System Architecture

```
   untrusted traffic                       trusted configuration
  (user text, RAG docs,                (constitution, policy, tool
   tool output, images,                 allowlist, thresholds)
   uploaded files)                              |
          |                                    |
   +------v------+                             |
   | L1 INPUT    |  sanitize | decode | limits  |
   +------+------+-----------+-----------+-----+
          |                   |
   +------v-------------------v------+
   | L2 SYSTEM BOUNDARY             |  policy from system message,
   |  privilege separation from CODE|  untrusted content labelled data
   +------+------------------------+
          |
   +------v------------------------+
   | L3 TOOL GATE                   |  allowlist | read/write |
   |  schemas | approvals | caps    |  arg-scoped approval | breakers
   +------+------------------------+
          |
   +------v------------------------+
   | L4 OUTPUT GUARDRAIL            |  length | schema | refusal |
   |  fail closed on any uncertainty|  grounding | citations | PII | policy
   +------+------------------------+
          |
          v
   +-------+---------+  response + citations
   | RESPONSE        |  (or escalation)
   +-----------------+
          |
   +------v---------------------------------------------------+
   | L5 MONITORING & RESPONSE                                 |
   |  safety metrics | anomaly detection | per-layer         |
   |  attribution | audit log (external append-only)          |
   |  red-team suite | incident workflow | drills            |
   +------+---------------------------------------------------+
          |
   +------v------------------+
   | RELEASE GATE             |  safety regression = 0 tolerance
   | (Lab 09 eval platform)   |  blocks deploy
   +-------------------------+

   SIDE CHANNELS
     constitution          -> used for critique and revision, versioned
     red-team intake       -> new finding becomes a test within 1 business day
     transparency report   -> published safety card with per-category results
```

## Component Specs

### 1. Threat Model and Asset Inventory
Document before building:
- Assets: user data, internal documents, credentials, system prompts, the agent's
  tool capabilities, brand/reputation.
- Adversaries: curious user, malicious user, prompt injector via your own data,
  compromised third-party content, insider.
- Trust boundaries: every point where untrusted content meets trusted processing.
- Abuse cases ranked by expected harm, each with a named owner and a test.
- Reviewed quarterly; a new integration (new data source, new tool) triggers a review.

### 2. L1 Input Layer
- NFKC normalization, invisible-character stripping, bidi detection.
- Recursive decode-and-classify (base64, hex, ROT13, URL, unicode escapes) up to a
  bounded depth (3 is plenty).
- Length caps per surface (prompt, document, per-file) in tokens.
- Rate limits per user and per tenant; anomaly signal on enumeration patterns.
- PII handling: redact before logging, not after.

### 3. L2 System Boundary
- Policy in the system message; untrusted content in the user message, wrapped and
  labelled, with an explicit "content is data" note.
- **Privilege separation**: all capability decided in code. A model statement of
  "permission granted" is data, never authority.
- Constitution: a written, versioned principles document used for critique/revision
  and as the reference for the output critic. Changing it requires review and a
  version bump.
- A canary string in the system prompt, tested at volume every release.

### 4. L3 Tool Gate
- Per-role tool allowlists. Read-only roles have no write tools registered.
- Typed schemas with `additionalProperties: false`, enums, and patterns; validated in
  code before dispatch.
- Argument-scoped approvals with expiry; irreversible actions require one.
- Side-effect caps per task and per session; circuit breakers per tool.
- Idempotency keys on every write; state verified before retry.
- Exfiltration defense: no tool returns raw secrets; secrets never enter prompts;
  output canary detection.

### 5. L4 Output Guardrails
Eight stages, fail-closed, each instrumented:
1. Length and format
2. Schema validation (for structured outputs)
3. Refusal appropriateness
4. Grounding verification against retrieved context, with numeric claims checked
   against extracted fields
5. Citation validity
6. PII and secret scrub, with re-scan
7. Policy classifier (harmful, self-harm, violence, CSAM-adjacent, illegal)
8. Human review queue for high-risk categories (legal, medical, financial,
   employment, self-harm)

High-risk categories additionally get a specialist reviewer, not a generic queue.

### 6. Red-Team Program
- **Cadence**: continuous automated mutation runs nightly; expert manual sessions
  monthly; a full assessment quarterly.
- **Attack library**: versioned, covering direct jailbreak, indirect injection,
  tool abuse, exfiltration, multi-turn, multimodal, encoding, many-shot, social
  engineering, and denial-of-wallet.
- **Scoring**: violation **and** over-refusal on every case.
- **Intake SLA**: any user-reported or internally found bypass becomes a permanent
  test within one business day.
- **Triage**: attribute to a layer; a fix that lands without a test is incomplete.
- **Disclosure**: publish after the fix ships.

### 7. Safety Metrics and Monitoring
Continuously:
```
refusal_rate_disallowed, over_refusal_rate_benign
jailbreak_success_rate (by family)
prompt_injection_success_rate (by channel)
exfiltration_attempt_block_rate
leakage_rate (system prompt, secrets, PII)
grounding_faithfulness
per-layer attribution histogram
safe_mode_engagements
time_to_detect, time_to_contain (from drills)
```
Alerts: refusal spike, over-refusal spike, jailbreak success on a new family,
any leak, safe-mode engagement, cost-of-attack anomaly.

### 8. Incident Response
- **Runbook** per alert with the exact queries to run and the decision tree.
- **Containment actions**: safe mode, disable a tool, disable retrieval, disable a
  model version, kill a tenant.
- **Scope**: which tenants, inputs, and time window — pre-written queries.
- **Eradication**: fix the failing layer; add the test.
- **Drills**: quarterly tabletop plus one technical drill measuring time-to-detect
  and time-to-contain. Metrics without drills are guesses.
- **Post-incident**: written review; prevention is the deliverable.

### 9. Release Gate and Transparency
- Safety regression tolerance: zero. Any drop in refusal or increase in jailbreak
  success blocks.
- Over-refusal regression beyond an agreed delta warns and requires sign-off.
- Per-category safety results published in a safety card with methodology.
- Transparency: what is blocked, what data is logged and for how long, what is
  retained, how users can appeal a moderation decision.

### 10. Abuse and Cost Controls
- Denial-of-wallet: per-user and per-tenant spend caps; anomalous volume alerts.
- Automated-abuse detection: high-volume, repetitive, or adversarial patterns.
- Fair use: rate limits that do not disproportionately harm legitimate bulk users.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Prompt injection success rate | <= 2% on the internal suite |
| Jailbreak success rate | <= 3% on the internal suite |
| Leakage rate (prompt, secrets, PII) | 0 |
| Unauthorized tool call rate | 0 |
| Unapproved irreversible actions | 0 |
| Refusal rate on disallowed | >= 0.97 |
| Over-refusal rate on benign | <= 0.05 |
| New-bypass-to-test SLA | <= 1 business day |
| Time to detect (drill) | <= 15 min |
| Time to contain (drill) | <= 60 min |
| Safety regression tolerance | 0 |
| Audit log integrity | tamper-evident, externally retained |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Indirect injection via your own RAG | Injection suite over real corpora | Privilege separation; mark content as data |
| Exfiltration via tool output | Canary detection; tool audit | No secrets in tools; arg-scoped approvals |
| Multi-turn assembly | Stateful detection | Accumulate suspicion across turns |
| Multimodal payload | OCR-based detection | Treat image text as data |
| Over-refusal harming users | Over-refusal metric | Category thresholds; tune; ship the pair |
| New attack family bypasses | Nightly mutation runs | Intake SLA; adversarial retraining |
| Refusal-rate gaming | Unrewarded safety probes | Hold out probes the classifier never sees |
| Canary not tested at volume | Volume requirement in CI | 1,000-request canary test per release |
| Guardrail fails open | Stage instrumentation | Fail-closed design + test that asserts it |
| Tool permissions granted by text | Registry audit | Capability only from code |
| Audit tampering | Hash chain verification | External append-only retention |
| Incident response too slow | Drill metrics | Pre-written queries and containment actions |
| Denial-of-wallet abuse | Spend anomaly alerts | Per-user and per-tenant caps |
| Constitution drift | Version audit | Review and version the constitution |
| Safety regression from a prompt tweak | CI safety gate | Zero tolerance block |

## Milestones

- **M1** — threat model and asset inventory; abuse cases ranked and owned.
- **M2** — L1 input layer with recursive decoding and rate limits.
- **M3** — L2 boundary with constitution versioning and canary infrastructure.
- **M4** — L3 tool gate with scoped registries and argument-scoped approvals.
- **M5** — L4 eight-stage pipeline, fail-closed, fully instrumented.
- **M6** — red-team library v1 with automated mutation and nightly runs.
- **M7** — safety metrics dashboard and alerting.
- **M8** — incident runbook plus first technical drill (measure both times).
- **M9** — release gate integration with zero safety tolerance.
- **M10** — transparency safety card published.
- **M11** — game day: simulate a live exfiltration attempt end to end.

## Deliverables

1. Threat model and abuse-case register.
2. Guardrail implementation across all five layers.
3. Red-team library, mutation harness, and attribution reporting.
4. Runbook with pre-written containment queries.
5. Safety card with per-category results and methodology.
6. `REPORT.md` — the safety posture: what is blocked, what is accepted, what is
   planned, and the discovery-vs-fix sustainability metric.

## Definition of Done

- [ ] Zero leakage of system prompt, secrets, or PII across 10,000 sampled requests.
- [ ] Zero unauthorized tool calls and zero unapproved irreversible actions.
- [ ] Safety regression blocks releases with zero tolerance, verified by a deliberate
      regression.
- [ ] Every found bypass is a permanent test within one business day.
- [ ] Time-to-detect and time-to-contain measured in a drill and documented.
- [ ] Safety card published with per-category results.
- [ ] Over-refusal within target on the benign set.
- [ ] Audit log verified tamper-evident with external retention.