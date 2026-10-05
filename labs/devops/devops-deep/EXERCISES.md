# DevOps Deep Exercises

## Docker & Kubernetes
1. Build a multi-stage image under 100 MB; record layer sizes.
2. Add liveness/readiness probes and force each failure mode.
3. Configure a PodDisruptionBudget; verify voluntary eviction behavior.

## CI/CD
4. Build a pipeline that fails on: failing test, HIGH CVE image, unsigned
   manifest.
5. Implement a manual approval gate before prod with audit logging.

## Terraform
6. Create two environments from one module via `for_each`; show plan diff.
7. Add a policy check (conftest/OPA) that blocks missing cost tags.

## GitOps
8. Install Argo CD; deploy a chart via an Application CR.
9. Force drift with kubectl; observe self-heal.
10. Break the app image; confirm sync failure and health degradation.

## Service mesh
11. Enable mTLS between two namespaces; show telemetry proof.
12. Split traffic 90/10; roll back by config change only.

## Secrets
13. Issue dynamic DB credentials from Vault; revoke and verify access dies.
14. Write a Vault policy scoped to one app's paths.

## Feature flags
15. Gate a new feature behind a flag; toggle it without redeploy.
16. A/B a copy change via flags; record conversion impact.

## Canary & delivery
17. Configure an Argo Rollouts canary with an analysis step.
18. Induce a 5% error rate; confirm automatic rollback.

## SRE & incidents
19. Define an SLO for a demo service; compute a burn rate for a date range.
20. Run a GameDay: kill a pod, a node, and practice the runbook.
21. Write a blameless postmortem for a self-created failure.

## Synthesis
22. Deploy the sample app end-to-end: Docker image -> Helm chart -> CI
    pipeline -> GitOps -> mesh mTLS -> flag-gated feature -> SLO.
