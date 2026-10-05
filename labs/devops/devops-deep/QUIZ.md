# DevOps Deep Quiz

1. What is the difference between a liveness probe and a readiness probe?
2. Why does Terraform remote state need locking?
3. What is the reconciliation loop in GitOps?
4. What does mTLS give you that plain TLS-between-ingress-and-pod does not?
5. What is an error budget and what happens when it is exhausted?
6. What is the difference between a feature flag and a config value?
7. Name two advantages of dynamic secrets over static ones.
8. In a canary release, what metric decides to auto-abort?
9. What is the primary role of the incident commander?
10. Why is immutability important for images and artifacts?
11. What is a PodDisruptionBudget and when is it required?
12. How does a burn-rate alert differ from a threshold alert?
13. What does a service mesh data plane consist of?
14. What is SLSA and why does it matter?
15. What is the difference between a push model and a pull model of deployment?
16. Why is timeout configuration as important as retry configuration?
17. What is drift in infrastructure-as-code and how do you detect it?
18. What is a blameless postmortem and what does it produce?

## Answers
1. Liveness restarts a stuck container; readiness gates traffic.
2. Prevents concurrent applies from corrupting state.
3. Controller reads desired state from git and corrects actual state.
4. Mutual authentication service-to-service, including identity.
5. Budget = allowed unreliability; exhausted means freeze features.
6. Flag is runtime-toggled; config is deploy-time.
7. Short TTL and no long-lived creds to leak.
8. Error rate / SLO burn of the canary version.
9. Coordinate communication/roles, not fix things personally.
10. Same artifact, everywhere you need it; rollback is redeploy.
11. Limits voluntary evictions during drains; needed for stateful apps.
12. Burn rate measures SLO budget consumption over windows.
13. Sidecar/ambient proxies intercepting service traffic.
14. Supply-chain framework scoring artifact trust levels.
15. Push: CI deploys to cluster. Pull: cluster pulls from git.
16. Retries without timeouts cause cascades.
17. Actual infra differs from code; detect via plan/refresh.
18. Non-blaming incident review; produces action items that change the system.
