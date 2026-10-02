# Multi-Cloud Strategies Deep Dive - Flashcards

Spaced repetition: **Question** → **Answer**

---

## Core Concepts

**Multi-cloud vs Hybrid Cloud?**
→ **Multi-cloud**: Multiple public cloud providers (AWS + Azure + GCP)
→ **Hybrid cloud**: Public cloud + on-premises/private cloud
→ Can combine: multi-cloud hybrid = multiple publics + on-prem

**Why multi-cloud?**
→ 1. **Avoid vendor lock-in** (technical, commercial, operational)
→ 2. **Best-of-breed services** (e.g., GCP for AI, Azure for enterprise, AWS for breadth)
→ 3. **Resilience/DR** (provider outage survival)
→ 4. **Data sovereignty** (GDPR, data residency laws)
→ 5. **Cost optimization** (arbitrage, committed spend fulfillment)
→ 6. **Negotiation leverage** (multi-cloud = bargaining power)

**Three types of vendor lock-in?**
→ **Technical**: Proprietary APIs, data formats, services (e.g., DynamoDB, Cloud Functions)
→ **Commercial**: Egress fees, committed spend discounts, contract terms, renewal cliffs
→ **Operational**: Team skills, tooling, processes, certifications tied to one cloud

---

## Architecture Patterns

**Lowest Common Denominator (LCD)?**
→ Use only portable primitives: Kubernetes, containers, Terraform, standard SQL (PostgreSQL), object storage (S3 API), message queues (Kafka/RabbitMQ).
→ Trade-off: Can't use cloud-native managed services (Aurora, Cosmos DB, BigQuery, Lambda).

**Native Services (Best-of-Breed)?**
→ Use each cloud's best managed services. Higher lock-in, higher productivity.
→ Abstract via: Service mesh (Istio), API gateway (Kong, Apigee), data layer (CockroachDB, Yugabyte).

**Polyglot / Workload-Placement?**
→ Place each workload on optimal cloud: ML on GCP (Vertex AI), .NET apps on Azure, legacy lift-shift on AWS.
→ Requires: Service discovery, networking, identity federation across clouds.

**Cloud-Agnostic Abstraction Layers:**
→ **Compute**: Kubernetes (Cluster API, Rancher, OpenShift), Nomad
→ **Storage**: CSI drivers, MinIO (S3 API), Rook/Ceph, Portworx
→ **Networking**: Cilium, Istio, Consul Connect, Skupper
→ **Identity**: OIDC federation, SPIFFE/SPIRE, Keycloak
→ **Observability**: OpenTelemetry, Prometheus, Grafana, Loki, Tempo
→ **IaC**: Terraform (provider plugins), Pulumi, Crossplane

---

## Data Management

**Data Gravity?**
→ Large datasets attract compute. Moving TB/PB data is slow/expensive.
→ Strategy: Place compute near data; use edge caching; consider data locality in architecture.

**Cross-Cloud Data Replication?**
→ **Database**: CockroachDB (multi-region SQL), YugabyteDB, Cassandra, MongoDB Atlas, DynamoDB Global Tables
→ **Object Storage**: Cross-region replication (S3 CRR, GCS dual-region, Azure GRS), MinIO replication
→ **Streaming**: Kafka MirrorMaker, Confluent Replicator, Redpanda Shadow Indexing
→ **File**: NFS/GlusterFS across clouds (high latency), Azure NetApp Files, AWS FSx

**Data Sovereignty/Compliance?**
→ **GDPR**: EU data must stay in EU (or adequate country). Use EU regions only.
→ **Schrems II**: US clouds problematic for EU personal data. Use EU-only clouds (OVH, Scaleway) or sovereign clouds (AWS EU Sovereign, Azure EU).
→ **China**: ICP license required. Use Aliyun/Tencent Cloud.
→ **Strategy**: Data residency tags, encryption with customer-managed keys (CMK), tokenization.

---

## Networking & Connectivity

**Inter-Cloud Connectivity Options:**
→ **VPN**: IPsec tunnels (AWS VPN, Azure VPN Gateway, Cloud VPN). ~1-10 Gbps. Low cost.
→ **Dedicated Interconnect**: Direct Connect (AWS), ExpressRoute (Azure), Cloud Interconnect (GCP). 10-100 Gbps. Low latency, high cost.
→ **Transit Hubs**: Equinix Fabric, Megaport, PacketFabric - connect to multiple clouds via single port.
→ **Service Mesh**: Istio multi-cluster (East-West), Skupper (layer 7), Consul Connect.

**DNS Failover Strategies:**
→ **Failover Routing**: Primary + secondary with health checks (Route 53, Cloud DNS, Traffic Manager). RTO ~60s (TTL dependent).
→ **Latency-Based**: Route to lowest latency region. Good for active-active.
→ **Geolocation**: Route based on user location. Compliance-driven.
→ **Weighted**: Split traffic % for canary/migration.

**Network Architecture Models:**
→ **Hub-and-Spoke**: Central hub (transit gateway) connects to spoke VPCs/VNets across clouds.
→ **Full Mesh**: Every cloud connects to every other. N*(N-1)/2 connections.
→ **Hybrid**: On-prem connects to hub; clouds connect to hub.

---

## Identity & Security

**Identity Federation Across Clouds:**
→ **OIDC/Saml**: Azure AD / AWS IAM Identity Center / Google Cloud Identity as IdP
→ **Workload Identity**: AWS IAM Roles for Service Accounts (IRSA), Azure Workload Identity, GCP Workload Identity Federation
→ **SPIFFE/SPIRE**: Universal workload identity across clouds/clusters
→ **Cross-Cloud IAM**: AWS STS AssumeRole with external ID, Azure AD federated credentials, GCP Workload Identity Pool

**Encryption Key Management:**
→ **Cloud KMS**: Each cloud has own KMS (AWS KMS, Azure Key Vault, GCP KMS)
→ **External KMS**: HashiCorp Vault, Thales CipherTrust, Fortanix - central key management
→ **Customer-Managed Keys (CMK)**: Bring your own key (BYOK) or hold your own key (HYOK)
→ **Envelope Encryption**: Data encrypted with DEK, DEK encrypted with KEK in KMS

---

## Disaster Recovery & Failover

**DR Patterns (RTO/RPO):**
→ **Backup & Restore**: RPO=hours, RTO=hours. Cheapest. Cross-cloud backup (AWS Backup, Azure Backup, GCP Backup).
→ **Pilot Light**: Core infra running (DB replica), scale up on failover. RPO=minutes, RTO=minutes.
→ **Warm Standby**: Scaled-down full environment. RPO=seconds, RTO=minutes.
→ **Active-Active**: Full capacity in multiple clouds. RPO=0, RTO=0. Most expensive, complex.

**Database Failover:**
→ **Sync Replication**: RPO=0, high latency impact (CockroachDB, PostgreSQL synchronous)
→ **Async Replication**: RPO=seconds-minutes, lower latency (Aurora Global, Cosmos DB, Cloud SQL)
→ **Multi-Master**: Write anywhere, conflict resolution (Cassandra, DynamoDB Global, Yugabyte)

---

## Cost Management

**Multi-Cloud Cost Challenges:**
→ **Egress fees**: $0.02-0.09/GB between clouds. Major cost driver.
→ **Committed spend**: Savings Plans (AWS), Reserved Instances (Azure), CUDs (GCP) - per cloud.
→ **Lack of unified view**: Need CMP or FinOps tool (CloudHealth, Cloudability, Kubecost, Finout).
→ **Tagging consistency**: Enforce tag policies across clouds (Terraform, Policy as Code).

**Cost Optimization Strategies:**
→ **Rightsizing**: Per-cloud instance recommendations (Compute Optimizer, Azure Advisor, Recommender)
→ **Spot/Preemptible**: Up to 90% discount. Use for fault-tolerant workloads.
→ **Serverless**: Pay-per-use for variable workloads.
→ **Data transfer optimization**: CloudFront/Cloudflare caching, VPC endpoints, PrivateLink.

---

## Migration Strategies

**Strangler Fig Pattern:**
→ 1. Identify domain boundary
→ 2. Create new service in cloud
→ 3. Route traffic via API Gateway / Service Mesh (canary)
→ 4. Gradually shift traffic
→ 5. Decommission legacy

**6 Rs of Migration:**
→ **Rehost** (lift-and-shift): VMs to cloud (AWS MGN, Azure Migrate)
→ **Replatform** (lift-tinker-shift): Minor optimizations (EC2 → RDS)
→ **Repurchase**: Move to SaaS (on-prem CRM → Salesforce)
→ **Refactor**: Re-architect for cloud-native (monolith → microservices)
→ **Retire**: Decommission unused
→ **Retain**: Keep on-prem (for now)

---

## Tools & Platforms

| Category | Tools |
|----------|-------|
| **IaC** | Terraform, Pulumi, Crossplane, Terragrunt |
| **Kubernetes Multi-Cluster** | Cluster API, Rancher, OpenShift, GKE Hub, AKS Fleet, EKS Anywhere |
| **Service Mesh** | Istio, Linkerd, Consul Connect, Skupper |
| **CMP** | Morpheus, CloudBolt, Scalr, HashiCorp Cloud Platform, VMware Aria |
| **FinOps** | CloudHealth, Cloudability, Kubecost, Finout, Vantage |
| **Networking** | Aviatrix, Alkira, Equinix Fabric, Megaport |
| **Identity** | Keycloak, Auth0, Azure AD, AWS IAM Identity Center, SPIRE |
| **Observability** | Datadog, New Relic, Grafana Cloud, Elastic, Honeycomb |
| **Policy** | OPA/Gatekeeper, Kyverno, Terraform Sentinel, Crossplane Compositions |

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Terraform multi-cloud init | `terraform init -backend-config="key=multi-cloud"` |
| Terraform apply specific provider | `terraform apply -target=aws_instance.web` |
| Cluster API create cluster | `clusterctl generate cluster my-cluster --infrastructure aws > cluster.yaml` |
| Istio multi-cluster join | `istioctl x create-remote-secret --name=cluster2 | kubectl apply -f -` |
| Check cross-cloud latency | `ping -c 10 <other-cloud-endpoint>` |
| Test DNS failover | `dig @resolver1.opendns.com myapp.example.com` |
| Estimate egress cost | `aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics UnblendedCost --group-by Type=DIMENSION,Key=USAGE_TYPE` |