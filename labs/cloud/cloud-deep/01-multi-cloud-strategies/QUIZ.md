# Multi-Cloud Strategies Deep Dive - Quiz

Test your understanding of multi-cloud architecture, vendor lock-in mitigation, cross-cloud failover, and data sovereignty.

---

## Questions

### 1. What is the primary difference between multi-cloud and hybrid cloud?
A) Multi-cloud uses multiple public clouds; hybrid cloud combines public cloud with on-premises/private cloud
B) Multi-cloud is for cost optimization; hybrid cloud is for compliance
C) Multi-cloud requires Kubernetes; hybrid cloud does not
D) There is no difference - they are synonyms

### 2. Which pattern uses a cloud-agnostic abstraction layer to mitigate vendor lock-in?
A) Native services pattern (use each cloud's best services)
B) Lowest common denominator pattern (use only portable services)
C) Polyglot pattern (different clouds for different workloads)
D) All of the above

### 3. What is the main challenge with active-active multi-cloud deployments?
A) Higher cost
B) Data consistency and synchronization latency across clouds
C) Increased complexity
D) All of the above

### 4. Which approach provides the best portability for compute workloads across clouds?
A) Cloud-specific managed Kubernetes (EKS, AKS, GKE) with cluster API
B) VM images (AMI, VHD) baked with Packer
C) Container images deployed to any Kubernetes (CNCF certified)
D) Serverless functions (Lambda, Cloud Functions, Cloud Run)

### 5. What is "data gravity" in multi-cloud context?
A) The tendency for applications to be pulled toward where their data resides
B) The cost of data egress between clouds
C) The latency of cross-cloud replication
D) The compliance requirements for data residency

### 6. How does Terraform enable multi-cloud infrastructure as code?
A) Provider abstraction - same HCL syntax, different provider plugins (aws, azurerm, google)
B) Cloud-agnostic modules that work identically on all clouds
C) Automatic translation of AWS resources to Azure/GCP equivalents
D) Built-in multi-cloud state locking

### 7. What is the purpose of a "cloud broker" or "cloud management platform" (CMP)?
A) Single pane of glass for provisioning, governance, cost management across multiple clouds
B) Load balancing traffic across clouds
C) Data replication between clouds
D) Identity federation across clouds

### 8. Which DNS-based failover strategy routes traffic based on health checks?
A) Weighted round-robin
B) Latency-based routing
C) Failover routing (primary + secondary with health checks)
D) Geolocation routing

### 9. What is the "strangler fig" pattern in cloud migration?
A) Gradually replace legacy system by routing new functionality to cloud while keeping old system running
B) Move all workloads at once (big bang)
C) Keep legacy on-prem, build new in cloud
D) Use cloud only for disaster recovery

### 10. What are the three main categories of vendor lock-in?
A) Technical (APIs, services), Commercial (contracts, pricing), Operational (skills, processes)
B) Compute, Storage, Network
C) IaaS, PaaS, SaaS
D) Public, Private, Hybrid

---

## Answers

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **A** | Multi-cloud = multiple public cloud providers (AWS+Azure+GCP). Hybrid = public cloud + on-premises/private cloud. Can combine both. |
| 2 | **B** | Lowest common denominator = use only portable primitives (Kubernetes, containers, Terraform, standard SQL) to maximize portability. Trade-off: can't use cloud-native managed services. |
| 3 | **D** | Active-active = all challenges: data consistency (CAP theorem), latency, cost (2x+), complexity (distributed systems problems). Most use active-passive. |
| 4 | **C** | Containers on CNCF-certified Kubernetes (via Cluster API, Rancher, OpenShift) provide highest compute portability. Serverless is least portable (vendor-specific APIs). |
| 5 | **A** | Data gravity: large datasets attract applications/services. Moving compute to data is cheaper than moving data to compute. Influences cloud placement decisions. |
| 6 | **A** | Terraform providers translate HCL to cloud APIs. Same workflow (`plan`, `apply`), different providers. Modules can be cloud-agnostic but resources are provider-specific. |
| 7 | **A** | CMP (Morpheus, CloudBolt, Scalr, HashiCorp Cloud Platform) = unified API/UI for multi-cloud lifecycle: provision, govern, optimize, secure. |
| 8 | **C** | Failover routing: Route 53 / Cloud DNS / Traffic Manager health checks → fail to secondary if primary unhealthy. RTO depends on TTL and check interval. |
| 9 | **A** | Strangler Fig: Incrementally migrate by creating new cloud services alongside legacy, routing traffic via facade/API gateway, decommissioning old pieces. |
| 10 | **A** | Technical (proprietary APIs, data formats), Commercial (egress fees, committed spend, contract terms), Operational (team skills, tooling, processes). |

---

## Scoring

- **9-10**: Multi-Cloud Architect - Understands trade-offs, patterns, data gravity, migration strategies
- **7-8**: Multi-Cloud Practitioner - Solid; review active-active challenges, DNS failover, strangler fig
- **5-6**: Multi-Cloud Learner - Good foundation; focus on lock-in categories, abstraction layers
- **<5**: Beginner - Re-read README/GUIDE; deploy a simple app to two clouds with Terraform