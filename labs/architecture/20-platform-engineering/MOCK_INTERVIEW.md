# Mock Interview: Platform Engineering Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Designing an Internal Developer Platform (IDP)

**Interviewer**: "Our engineering organization has 200+ developers across 20 teams. Each team sets up its own infrastructure, CI/CD, and deployment process, causing inconsistency and wasted effort. Design an Internal Developer Platform to solve this."

**Candidate**: "I'd build an Internal Developer Platform (IDP) that provides golden paths — standardized, self-service workflows for common development tasks — while maintaining autonomy for teams that need customization."

**Interviewer**: "Define what the platform provides."

**Candidate**: "The platform provides: (1) Environment provisioning — 'Request a new staging environment' creates a Kubernetes namespace, database, and service mesh config automatically. (2) Deployment pipeline — standardized CI/CD with build, test, security scan, deploy stages. (3) Service scaffolding — 'Create a new service' generates project structure with best practices built in. (4) Observability — every service gets logging, metrics, and tracing by default. (5) Configuration management — centralized config with environment-specific overrides."

**Interviewer**: "Walk me through the platform architecture."

**Candidate**: "The platform has a user-facing layer (Backstage-like developer portal), a control plane (orchestrates workflows), and a resource plane (manages cloud resources). The developer portal is the single entry point — developers request resources through a catalog UI or CLI. The control plane runs workflows (Terraform for infrastructure, Argo Workflows for CI/CD pipelines). The resource plane is the cloud infrastructure (Kubernetes clusters, databases, message queues)."

**Interviewer**: "How do you handle team autonomy vs standardization?"

**Candidate**: "Through golden paths and paved roads. The golden path is the default — well-documented, fully automated, and supported. Teams can deviate by requesting exceptions, but exceptions require justification and have additional operational burden. The platform captures this in a 'scorecard' — teams that follow the golden path get 'gold' rating (best support, dashboards, runbooks). Teams on custom paths get 'silver' or 'bronze' with less support."

**Interviewer**: "How does the platform handle multi-tenancy?"

**Candidate**: "Each team gets a 'space' — a logical boundary with isolation. The platform manages resource quotas per space, network policies, and access control via OAuth/RBAC. Team A can't see Team B's resources. The platform also aggregates costs per space for chargeback. Each space has a `team.yaml` file defining owners, Slack channel, PagerDuty escalation, and compliance requirements."

**Interviewer**: "How do you measure platform success?"

**Candidate**: "DORA metrics per team: (1) Deployment frequency — are teams deploying more often? (2) Lead time for changes — from commit to production. (3) Mean time to recovery — how fast do teams recover from incidents? (4) Change failure rate — how often do deployments cause incidents? Additionally: developer satisfaction score, platform adoption rate, and time-to-production for new services."

**Interviewer**: "What's the biggest risk with IDP development?"

**Candidate**: "Building too much too fast, creating a platform that teams don't use. The key is to build incrementally. Start with the highest-value, lowest-effort capability — usually service scaffolding and deployment pipeline. Validate with a pilot team. Iterate based on feedback. The platform should feel like a product, not a project — with a product manager, user research, and regular releases."

**Interviewer**: "How does the platform evolve as the organization grows?"

**Candidate**: "The platform itself is a product with a roadmap. As the organization grows, the platform adds more capabilities: (1) Scorecards and governance — ensure teams follow security and compliance requirements. (2) Resource catalog — discoverability of services, APIs, and documentation. (3) Self-service infrastructure — teams can request resources without a ticket. (4) Cross-team capabilities — feature flags, A/B testing infrastructure, API gateways as shared services."

---

## Key Takeaways

- IDP provides golden paths: standardized, self-service workflows
- Platform architecture: developer portal → control plane → resource plane
- Balance standardization with team autonomy through scorecards
- Measure success with DORA metrics and developer satisfaction
- Build incrementally with a product mindset, not a project
- Platform evolves as the organization grows and needs change

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

