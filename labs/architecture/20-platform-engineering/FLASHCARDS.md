# Platform Engineering Flashcards

## Fundamentals

**Q: What is Platform Engineering?**
**A:** Building an Internal Developer Platform (IDP) as a product for internal developers. Reduces cognitive load, provides paved roads, self-service.

**Q: Platform Engineering vs DevOps?**
**A:** DevOps = culture/practices. Platform Eng = product team building reusable platform. Platform enables DevOps at scale.

**Q: What is an IDP?**
**A:** Internal Developer Platform — unified layer of tools, APIs, workflows for: deploy, infra, secrets, observability, policy.

**Q: Platform as a Product?**
**A:** Treat platform like a product: customers (developers), PM, roadmap, metrics, feedback loops, documentation, support.

**Q: Cognitive Load?**
**A:** Mental effort to complete a task. Platform reduces it by abstracting complexity (K8s, networking, infra).

---

## Golden Paths

**Q: What is a Golden Path?**
**A:** Opinionated, supported path for common tasks (e.g., "Java microservice to prod"). Includes templates, CI/CD, policies, observability.

**Q: Golden Path components?**
**A:** Template (scaffold), CI pipeline, CD pipeline, policies (guardrails), observability defaults, docs.

**Q: Why not "Golden Cage"?**
**A:** Must allow escape hatches for special cases. Guardrails, not gates. Developers can opt out with approval.

**Q: Template example (Backstage)?**
**A:** `template.yaml` → generates: Git repo, Dockerfile, Helm chart, Tekton pipeline, ArgoCD Application, README.

---

## Self-Service Infrastructure

**Q: CrossPlane core concepts?**
**A:** 
- **XRD** (CompositeResourceDefinition): Custom API (e.g., `XPostgreSQL`)
- **XR** (CompositeResource): Instance of XRD
- **Composition**: Maps XR → managed resources (RDS, CloudSQL, CNPG)
- **Provider**: K8s controller for external API (AWS, GCP, Azure, K8s)

**Q: CrossPlane vs Terraform Controller?**
**A:** CrossPlane = native K8s API, continuous reconciliation, composition engine. Terraform = plan/apply cycle, state file, less K8s-native.

**Q: GitOps for Infra?**
**A:** ArgoCD/Flux watches Git → applies manifests. Infra as Code in Git. Drift detection + auto-heal.

**Q: App of Apps pattern?**
**A:** Root Application manages child Applications (per team, env, cluster). Single source of truth for cluster state.

---

## Developer Portal (Backstage)

**Q: Backstage core plugins?**
**A:** Software Catalog, Software Templates (Scaffolder), TechDocs, Kubernetes, ArgoCD, Cost, Search.

**Q: Software Catalog?**
**A:** Graph of entities: Component, API, Resource, System, Domain, User, Group. Ingested from Git, K8s, cloud.

**Q: Scaffolder?**
**A:** Executes template → creates repo, files, CI/CD, registers in catalog. Steps: fetch, template, publish, register.

**Q: TechDocs?**
**A:** MkDocs-based, docs live in repo (`/docs`), built and published automatically on merge.

**Q: Backstage + ArgoCD?**
**A:** ArgoCD plugin shows sync status, health, history in catalog entity page. One-click sync.

---

## Policy as Code

**Q: Kyverno vs OPA Gatekeeper?**
**A:** 
- Kyverno: K8s-native, YAML policies, easier debugging (PolicyReport), mutate + validate + generate.
- OPA: Rego language, more powerful, separate audit scan, steeper learning curve.

**Q: Kyverno policy types?**
**A:** `validate` (enforce/audit), `mutate` (add defaults, labels), `generate` (create resources), `verifyImages` (sigstore).

**Q: Admission control flow?**
**A:** Request → AuthN → AuthZ → MutatingWebhook (Kyverno mutate) → ValidatingWebhook (Kyverno validate/OPA) → Etcd.

**Q: Policy testing?**
**A:** `kyverno test` (unit tests), `kyverno apply --dry-run`, PolicyReport for cluster audit.

---

## Secrets Management

**Q: SealedSecrets flow?**
**A:** `kubeseal` encrypts Secret → SealedSecret (safe in Git) → Controller in cluster decrypts → creates Secret.

**Q: External Secrets Operator (ESO)?**
**A:** `SecretStore` (Vault/AWS/GCP) + `ExternalSecret` (specifies what to sync) → Controller creates K8s Secret.

**Q: Vault Agent Injector?**
**A:** Sidecar + init container. Authenticates to Vault, writes secrets to shared volume (file/env). App reads from volume.

**Q: Rotation strategies?**
**A:** SealedSecrets: manual. ESO: auto (poll interval, webhook). Vault Agent: template re-render on change (fsnotify).

---

## Observability & Metrics

**Q: Platform metrics (DORA +)?**
**A:** Deployment Frequency, Lead Time, MTTR, Change Failure Rate + Onboarding Time, Adoption %, Self-Service Ratio.

**Q: Platform SLIs/SLOs?**
**A:** API latency (p99 < 500ms), availability (99.9%), build queue time (< 5 min), deploy success rate (> 99%).

---

## Day 2 Operations

**Q: Control plane upgrade strategy?**
**A:** Test in staging → backup etcd → upgrade K8s masters → upgrade controllers (ArgoCD, Crossplane, Kyverno) → rolling worker upgrade → validate.

**Q: Cost optimization?**
**A:** Right-sizing (VPA), spot instances, cluster autoscaler, idle resource cleanup (janitor), FinOps dashboard.

**Q: Security patching?**
**A:** Base image updates (Dependabot/Renovate), node image upgrades, CVE scanning (Trivy/Grype), policy enforcement.

**Q: Developer support?**
**A:** Slack channel, office hours, platform docs, onboarding buddy, feedback surveys, incident retrospectives.