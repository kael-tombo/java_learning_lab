# AWS Networking - Real World Project

## Project: Multi-Region Network Architecture with Private Connectivity

### Objective
Design the network layer for an application spanning three regions and a hybrid data centre:
inter-region peering, Transit Gateway, private DNS, hybrid connectivity, and egress controls —
with a documented failure story for every component.

### Why This Is a Real Problem
Networking is the least reversible part of a cloud architecture. Subnet CIDRs, peering
relationships, and DNS zones get baked into security rules, DR plans, and third-party
integrations. Getting it wrong means a migration, not a config change.

### Architecture Overview
```
 Region A (primary)          Region B             Region C
 ┌────────────────┐        ┌──────────┐         ┌──────────┐
 │ VPC 10.0/16    │◀──────▶│ 10.0/16  │◀──────▶│ 10.0/16  │
 │  app/data      │ Transit Gateway hub (one per region)
 └───────┬────────┘
         │ Direct Connect (private virtual interface)
 ┌───────┴────────┐
 │ On-prem 10.40/16│   ← non-overlapping CIDR, always
 └─────────────────┘

 DNS: private hosted zone, split-horizon, health-checked failover between regions
```

### Phase 1: CIDR Plan and Overlap Audit (Week 1)
1. Inventory every network you connect to: on-prem, other VPCs, third parties, future regions
2. Allocate non-overlapping CIDRs with growth headroom; document the allocation in one table
   that the whole organisation can see
3. Check overlap **before** peering — overlapping CIDRs across peered VPCs break routing and
   the error messages are unhelpful
4. Plan address space for a fourth region now, while it is free to choose

**This table is the most valuable artefact you will produce in this project.**

### Phase 2: Inter-Region Connectivity (Week 2)
1. Transit Gateway per region with attachments for each VPC
2. Route propagation and association configured explicitly; verify no unintended routes
3. Routing preference set deliberately — do not let the default preference mask a cost or
   latency problem
4. Measure inter-region latency and throughput; establish a baseline before optimising
5. Security groups reference the remote region's groups where possible — avoid CIDR rules
   across regions, since they cannot reference groups across account/region boundaries

### Phase 3: Hybrid Connectivity (Week 3)
1. Direct Connect with a private virtual interface to the Transit Gateway; VPN as backup
2. Public VIF only where S3 or other public endpoints justify it
3. Confirm the on-prem CIDR does not collide with any cloud CIDR, and document the collision
   register
4. Measure failover: pull the Direct Connect circuit and confirm traffic moves to VPN within
   the RTO you promised
5. Ask your provider for a second circuit or a diverse path if uptime demands it

### Phase 4: DNS as Architecture (Week 4)
1. Private hosted zone shared across regions via Route 53
2. Split-horizon: internal names resolve privately, external names resolve publicly
3. Health checks with a **fast** TTL (30–60s) for failover, accepting the DNS caching cost
4. Separate health-check TTL from record TTL and know which is which
5. Measure end-to-end failover including DNS caching — this is usually the slowest part of a
   regional failover, and it surprises everyone

### Phase 5: Egress Controls (Week 5+)
1. All egress through inspection: a NAT instance or a firewall appliance in the path
2. DNS filtering for egress control on resolvers
3. Per-subnet egress rules; do not rely on one wide-open egress path
4. Log egress to CloudWatch, and alert on new destinations appearing
5. Verify the data tier still has no route out — this is the control most likely to be broken
   by a well-meaning "temporary" change

### Deliverables
1. CIDR allocation table covering every connected network, published organisation-wide
2. Transit Gateway topology with explicit propagation and measured cross-region latency
3. Direct Connect plus VPN failover rehearsal with measured RTO
4. DNS design with failover timing, plus egress control and the isolation re-verification

### Success Criteria
- Single-AZ failure causes no service interruption, verified by test
- Region failover completes within the stated RTO, including DNS propagation
- Data tier has no egress route, verified by Flow Logs
- Every new network request is refused until the CIDR table is updated

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon VPC documentation —
  https://aws.amazon.com/vpc/
  Use for: the maintained definitions of subnets, route tables, security groups, and NAT
  gateways. Verify current features before relying on specific gateway endpoint behaviour —
  support for S3 operations differs by endpoint type.
- Amazon Route 53 documentation —
  https://aws.amazon.com/route53/
  Use for: health checks, failover routing policies, and the TTL/caching implications that
  determine real failover time. Verify the current failover behaviour for the routing policy
  you choose.

### Estimated Time
8-10 weeks part-time