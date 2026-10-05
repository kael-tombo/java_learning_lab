# DevOps Deep Flashcards

Q: What is idempotency?
A: Running the same operation N times yields the same result as once.

Q: What is GitOps?
A: Git as the source of truth; a controller reconciles the cluster to it.

Q: What is a service mesh?
A: Infra layer of proxies handling service-to-service traffic policy.

Q: mTLS vs TLS?
A: mTLS authenticates both client and server with certificates.

Q: What is an SLO?
A: A target level of service reliability over a time window.

Q: What is an error budget?
A: The unreliability you are allowed within the SLO window.

Q: Burn rate?
A: How fast the error budget is being consumed, normalized.

Q: What is a canary deployment?
A: Route a small % of traffic to a new version, expand on health.

Q: Blue/green?
A: Two production environments, switch traffic once validated.

Q: Dynamic secret?
A: Credential issued on demand with a short TTL (e.g. Vault DB creds).

Q: Feature flag?
A: Runtime toggle gating a feature without redeploying.

Q: What is drift?
A: Actual state diverging from declared IaC state.

Q: Admission controller?
A: Webhook that validates/mutates requests to the cluster API.

Q: SBOM?
A: Software Bill of Materials — list of components in an artifact.

Q: What is a blameless postmortem?
A: Incident review focused on system fixes, not blame.

Q: PDB?
A: PodDisruptionBudget — limits voluntary evictions.

Q: What is a liveness probe?
A: Check that restarts a container when it fails.

Q: What is a readiness probe?
A: Check that gates traffic to a pod.

Q: Push vs pull deployment?
A: Push: CI pushes to cluster. Pull: cluster pulls from a repo.

Q: What is a reconciliation loop?
A: Controller cycle: observe -> diff vs desired -> act.
