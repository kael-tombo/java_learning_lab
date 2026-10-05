# GCP Fundamentals - Real World Project

## Project: Multi-Project GCP Foundation for a Product Team

### Objective
Design the project hierarchy, IAM structure, network topology, and CI/CD for a team shipping
one product across production, staging, and development — with production defaults enforced
rather than recommended.

### Why This Matters
GCP projects are the security boundary, the billing boundary, and the quota boundary. Getting
the project layout wrong means a production IAM change touches development, or a quota
increase for staging is denied because production holds the limit.

### Architecture Overview
```
 Organization
   ├── orders-prod            (prod data, strict IAM, CMEK on Cloud SQL)
   │     ├── VPC: no external IPs, private Cloud SQL, Cloud NAT for egress
   │     └── SA: per-service, per-environment, no shared SA across envs
   ├── orders-staging         (synthetic data, IAM mirrors prod minus prod data access)
   └── orders-dev             (per-developer SA, free tier quotas)

 Shared: Cloud Logging sink → central project; Secret Manager per project;
         Artifact Registry per project; budget alerts at each level
```

### Phase 1: Project Structure and Budgets (Week 1)
1. Decide the project-per-environment split, and whether each service needs its own project
2. Apply labels at creation; document the label schema
3. Set up billing export so per-project and per-label cost is visible
4. Budget alerts per project **and** per label, so a runaway team is caught by label, not
   just by project
5. Document who can create projects — it is the most consequential permission you will grant

### Phase 2: IAM Structure (Week 2)
1. One service account per service per environment. Never share one across services
2. Grant predefined roles at the **resource** level, not project-wide, wherever possible
3. Separate the deploying identity from the runtime identity: CI needs deploy rights, the
   runtime needs data access and nothing more
4. Audit-log access to the org's logs sink, with a viewer role for security, not for engineers
5. Document the escalation path: who approves a role grant, and how long it takes

### Phase 3: Network Topology (Week 3)
1. Shared VPC so networking changes are separated from service deployment
2. Private IP only for Cloud SQL; no external IPs on compute
3. Egress through Cloud NAT with a controlled path; log egress
4. Private Google Access so workloads reach Google APIs without going out to the internet
5. Firewall rules: default-deny ingress, explicit allow, tagged and documented
6. Test: verify no workload has an external address, and that the data tier has no public
   endpoint

### Phase 4: Data Security (Week 4)
1. CMEK for Cloud SQL and Cloud Storage, with the key ring in a separate project
2. Secret Manager for every credential; no service account key files anywhere
3. VPC Service Controls for the data perimeter, understanding that it is a containment
   boundary, not a security boundary
4. Backup and point-in-time recovery enabled; **test a restore** — untested backups are
   wishes
5. Document the data classification per system and where each class may live

### Phase 5: Platform and Operations (Week 5+)
1. Terraform project templates so a new service is a parameter change
2. CI/CD: plan review, policy-as-code validation, and the secret-scan check
3. Deployment to GKE with workload identity, so no key files inside the cluster
4. Blue/green or canary with automated rollback on SLI breach
5. Quarterly review: unused roles revoked, projects without labels fixed, budgets recalibrated

### Deliverables
1. Project hierarchy, label schema, and budget alerts at both project and label level
2. IAM matrix mapping every principal to its roles and scopes, with escalation documented
3. Shared VPC topology with firewall rules and the isolation tests
4. CMEK and Secret Manager rollout, a verified restore, and the service template

### Success Criteria
- No service account key file exists anywhere in source, CI, or containers
- Production IAM grants are resource-scoped, reviewed, and revocable within one business day
- Every project has labels and a working budget alert; overspend is caught by label
- A restore from backup succeeds in a rehearsal within the stated RTO

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Google Cloud IAM documentation —
  https://cloud.google.com/iam/docs
  Use for: the maintained IAM model, predefined versus custom roles, and conditions. Verify
  the current list of predefined roles and any recent changes before assigning them.
- Google Cloud SQL documentation —
  https://cloud.google.com/sql/docs
  Use for: private IP configuration, the VPC peering prerequisite, and regional failover
  behaviour used in Phase 3 and the failover test.

### Estimated Time
7-8 weeks part-time