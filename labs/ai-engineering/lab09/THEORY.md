# Lab 09: AI Security — Theory

## 1. Threat Model

| Actor | Goal | Channel |
|-------|------|---------|
| Curious user | Bypass restrictions harmlessly | Prompt |
| Malicious user | Harmful content, illegal instructions | Prompt |
| Prompt injector | Hijack an agent through untrusted data | Retrieved docs, tool output, images |
| Exfiltrator | Steal secrets via the model | Prompt + tool access |
| Insider / careless team | Leak data through logs | Logging, exports |
| Compromised provider | Data exposure, supply chain | API, weights |
| Adversarial corpus author | Poison retrieval | Ingested content |

**Jailbreak** is the user persuading the model to violate policy. **Prompt injection** is
an attacker smuggling instructions through content the application did not treat as
instruction-bearing. Applications are broken by injection far more often, because the
application itself supplies the channel.

## 2. Security Boundaries

Only three things are real boundaries:

1. **Capability control in code** — the tool registry and the gate. A model that says
   "permission granted" has granted nothing.
2. **Data isolation** — tenant namespaces, pre-filtered indexes, scoped caches.
3. **Verified computation** — schema validation, arithmetic recomputation, signature
   checks.

Everything else — prompts, classifiers, regexes — is a **defence in depth layer** that
raises cost and buys time. Treat them as such and you will design them honestly.

## 3. Input Attacks

```
  obfuscation     base64 | hex | rot13 | leetspeak | unicode homoglyphs
                  zero-width chars | bidi overrides | spacing
  framing         role play | hypothetical | "for a novel" | "debug mode"
                  many-shot | authority spoofing | code-comment hiding
  collision       benign document + trailing instruction block
  exfiltration    "summarize this" on a document containing system prompts
  multi-turn      payload split so no single turn trips a filter
  multimodal      instructions rendered inside an image
  resource        oversized input | huge files | nested archives
```

Defenses: normalization (NFKC), invisible-character stripping, recursive decoding with a
depth limit, length caps, rate limits, and — most importantly — treating decoded content
as **data**, never as instructions.

## 4. Privilege Separation

```
  TRUSTED channel  -> system message: policy, output contract, permissions
  UNTRUSTED        -> user message: retrieved docs, tool results, images
                      wrapped, labelled, explicitly "data, never instructions"

  capability comes from the REGISTRY and the GATE (code)
  not from the prompt, not from the model, not from retrieved content
```

Corollary: a read-only agent has no write tools registered. Nothing to inject into.
Irreversible tools require argument-scoped approvals with a timeout that denies.

## 5. Tool Security

- **Allowlist** per role. No shell, no generic SQL, no arbitrary HTTP.
- **Typed schemas** with `additionalProperties: false`, enums, and patterns, validated in
  code before dispatch.
- **Approval gates** on irreversible actions, scoped to normalized arguments, expiring.
- **Side-effect caps** and idempotency keys so retries cannot duplicate writes.
- **Circuit breakers** so a compromised or broken tool cannot be hammered.
- **Rate limits** per tool and per tenant.
- **Result sanitization**: tools never return secrets; references, not values.

## 6. Output Attacks

Data leaving the system is the other half of the threat:

```
  PII / secret leakage      emails, phone numbers, keys, account numbers
  system prompt leakage     a canary in the system prompt appearing in output
  cross-tenant leakage      cached or retrieved content from another tenant
  harmful content           policy categories
  malformed output          breaking downstream parsers
  ungrounded output         confident claims with no evidence
```

Defenses: output guardrail chain (schema, refusal, grounding, citations, PII scrub,
policy classifier, human review for high-risk categories), **fail closed**, and
tenant-scoped caches.

## 7. Data Protection

| Control | Purpose |
|---------|---------|
| Encryption in transit and at rest | Third-party exposure |
| PII scrub at write | Logs and traces become non-sensitive |
| Retention by data class | Minimise exposure window |
| Tenant-scoped caches and indexes | Isolation |
| Pre-filtered retrieval | Unauthorized content never influences ranking |
| Content hash audit | Prove what was indexed and served |
| DLP on exports and logs | Accidental disclosure |
| Model/data classification | Governs which models may see which data |

## 8. Supply Chain

Treat models, datasets, and adapters as third-party code:

- Pin base models by **commit SHA**, not a floating tag.
- Verify adapter checksums; record provenance.
- Scan datasets for poisoned content and PII at ingest.
- Review third-party prompts and guardrail configs as code.
- Reproducible build metadata for any artifact you serve.

## 9. Abuse Detection

- Rate limits and per-tenant quotas (denial-of-wallet protection).
- Anomaly detection on usage patterns: bursts, repeated identical long inputs,
  systematic probing of tool arguments.
- Content-based signals aggregated per tenant: injection attempts, refusals, escalations.
- Automated abuse detection that responds by **restricting** rather than blocking
  outright, so a legitimate user behind a shared NAT is not punished.

## 10. Incident Response

```
  detect     -> signal (injection findings, leakage canary, refusal spike,
                unusual tool-call patterns)
  contain   -> disable a tool | safe mode | revoke credentials | scope a tenant
  scope     -> which tenants, inputs, window; pre-written queries
  eradicate -> fix the failing layer; add the case to the red-team suite
  recover   -> verify guardrails before restoring traffic
  review    -> write it down; the write-up is the prevention
```

Measure **time to detect** and **time to contain** in drills. Untested runbooks are
fiction.

## 11. Threat Modelling Practice

For every new integration (a new data source, a new tool, a new model provider):

```
  1. What new data enters? Whose trust does it carry?
  2. What new capability is exposed?
  3. What is the new blast radius if compromised?
  4. What existing control assumed this did not exist?
  5. What test proves the new surface is guarded?
```

Skipping this is how "we added a PDF upload" becomes an exfiltration channel.

## Key Principles

1. Capability from code, never from text.
2. Untrusted content is data; label it and enforce it.
3. Fail closed; fail visibly.
4. Isolation enforced in the query, not in the API wrapper.
5. Every security control is tested by a red-team case that must fail without it.
6. Every incident produces a permanent regression test.
7. Assume the perimeter will be crossed; design for containment and detection.

## Key Equations

```
P(detect per attempt) = d
P(undetected after m attempts) = (1-d)^m
refusal_rate vs over_refusal_rate  (weighted cost)
detection_rate = 1 - uncaught/total
blast_radius = fraction of requests a change affects
```