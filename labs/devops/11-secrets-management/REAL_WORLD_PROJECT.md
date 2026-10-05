# Real-World Project — Secrets Management

## Scenario
A security review finds live credentials for staging and prod databases
committed in three repos, plus a wiki page with shared admin passwords.

## Requirements
- All static credentials removed from repos, images, and docs.
- Centralized secret store with audit logging.
- Rotation runbooks per secret class.
- Break-glass access documented and monitored.

## Phase plan
1. **Inventory**: scan repos and images for credential patterns; rotate
   anything found.
2. **Centralize**: adopt a secret store (Vault/cloud KMS-backed store).
3. **Integrate**: apps fetch secrets at runtime via SDK or sidecar.
4. **Rotate**: quarterly rotation drill for the top three secret types.
5. **Audit**: alert on every secret read outside expected callers.
6. **Policy**: admission control blocks pods mounting the default service account with broad secret access.

## Deliverables
- Secret inventory and rotation schedule.
- Integration guide per app runtime.
- Audit alert rules.

## Risks & mitigations
- Secret store becomes a SPOF → HA deployment documented.
- App refactor effort → phased by risk, start with crown jewels.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Secrets Management Cheat Sheet:
  https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Kubernetes docs — Secrets and encryption at rest:
  https://kubernetes.io/docs/concepts/configuration/secret/

## Definition of done
- Zero live credentials in source control.
- Rotation drill completed for DB, registry, and API keys.
