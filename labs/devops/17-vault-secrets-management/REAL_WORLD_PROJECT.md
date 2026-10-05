# Real-World Project — Vault

## Scenario
Hundreds of static DB passwords live in CI variables. A breach of one
env variable would expose many systems.

## Requirements
- Vault deployed HA with auto-unseal via cloud KMS.
- Dynamic DB credentials for all app tiers.
- AppRole/JWT auth per workload identity.
- Audit logs shipped to SIEM with alerts on anomalies.

## Phase plan
1. **HA deploy**: 3-node Raft cluster, auto-unseal, TLS everywhere.
2. **Enable engines**: KV for static config, DB engine for credentials,
   transit for app-level encryption.
3. **Migrations**: move static secrets tier by tier; revoke old ones.
4. **Workload identity**: JWT auth from Kubernetes service accounts.
5. **Audit & alert**: anomalies like mass reads page on-call.
6. **DR drill**: snapshot restore to a new cluster; unseal; verify paths.

## Deliverables
- Vault cluster runbook.
- Secret migration tracker.
- Audit alert rules.

## Risks & mitigations
- Blast radius of Vault outage → caching via Vault Agent.
- Team adoption → templates for common app patterns.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Vault docs — dynamic secrets:
  https://developer.hashicorp.com/vault/docs/secrets
- Vault docs — audit devices:
  https://developer.hashicorp.com/vault/docs/audit

## Definition of done
- Zero static DB passwords in CI variables.
- Dynamic creds in use for all tiers.
- Restore drill passed.
