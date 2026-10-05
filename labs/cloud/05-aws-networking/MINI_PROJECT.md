# AWS Networking - Mini Project

## Project: A Three-Tier VPC with Private Data Tier

### Objective
Build a VPC by hand — subnets across three AZs, explicit route tables, NAT for egress, and
security groups that permit only declared flows — then prove isolation with tests.

### Requirements
1. VPC `10.0.0.0/16` with public, private-app, and private-data subnets across three AZs
2. Route tables: public (IGW), private-app (NAT), private-data (no internet route)
3. Security groups: ALB, app, data — with rules derived from an explicit flow table
4. VPC Flow Logs to CloudWatch for verification
5. Tests asserting that paths you did not declare are unreachable

### Steps

**Step 1: Plan the address space and the flow table before creating anything**
```
 10.0.0.0/16  VPC
 ├── 10.0.0.0/24    public-a      (ALB, NAT GW)      az-a
 ├── 10.0.1.0/24    public-b                          az-b
 ├── 10.0.2.0/24    public-c                          az-c
 ├── 10.0.10.0/24   app-a         (EC2 app tier)     az-a   private
 ├── 10.0.11.0/24   app-b                             az-b   private
 ├── 10.0.12.0/24   app-c                             az-c   private
 ├── 10.0.20.0/24   data-a        (RDS)              az-a   private, isolated
 └── 10.0.21.0/24   data-b                             az-b   private, isolated

 Permitted flows — nothing else:
   internet:443 → ALB:443
   ALB:443 → app:8080   (only from the ALB security group, not 0.0.0.0/0)
   app:8080 → data:5432  (only from the app security group)
   app:5432 → internet:443 (AWS APIs, via NAT)
   data:* → internet      FORBIDDEN. No route exists. This is the design, not a rule.
```
Write that table down and create resources to match it. Designing rules after creation is how
`0.0.0.0/0` sneaks in.

**Step 2: Public subnets and the internet gateway**
```json
{ "Effect": "Allow", "Action": "0.0.0.0/0", "Resource": "arn:aws:ec2:route-table/rtb-public" }
```
Only public subnets route to the IGW. If you find an IGW route on a private subnet, stop —
that is the classic egress leak.

**Step 3: Private subnets and one NAT per AZ**
```json
{ "Destination": "0.0.0.0/0", "GatewayId": "nat-az-a" }
```
One NAT per AZ rather than one shared NAT. Reasons, in order of importance:
1. An AZ failure does not take egress down for the other two
2. Cross-AZ NAT data charges are avoided (or at least not on the hot path)
3. A single NAT Gateway is an AZ-wide single point of failure — the most common
   self-inflicted availability bug in this topology

Cost note: NAT gateways are billed per hour plus per GB. Three is not free. Document the
trade; if cost forces one NAT, put it in the AZ with the most critical traffic and say so.

**Step 4: The data tier has no internet route at all**
```
private-data route table:
   10.0.0.0/16  → local                      only
   (no 0.0.0.0/0 entry)
```
Absence of a route is the control. A security group rule cannot make a nonexistent route
work, which makes this the strongest control in the design.

**Step 5: Security groups referencing groups, not CIDRs**
```json
{ "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
  "SourceSecurityGroupId": "sg-app",
  "Description": "Postgres from app tier only" }
```
Referencing a security group means the rule follows the source automatically. CIDR rules go
stale when subnets change; group references do not.

**Step 6: Prove isolation with Flow Logs**
Enable VPC Flow Logs, then attempt each forbidden path and confirm a REJECT appears:
```bash
# from data-a, attempt outbound to the internet
curl -m 5 https://example.com    # expect: no route, connection never leaves
# from app-a to RDS: allowed
# from data-a to app:8080: expect REJECT in flow logs
```
A test you can run is worth more than a diagram. Record the flow-log entries as evidence.

### Deliverables
1. VPC, subnets, route tables, NAT, and IGW across three AZs
2. Three security groups with rules exactly matching the flow table
3. Flow Logs enabled, plus four connectivity tests with their outcomes
4. A topology diagram plus the address plan and the NAT placement rationale

### Extension (CHALLENGE)
Replace NAT egress with VPC endpoints for S3 and Secrets Manager, and measure the latency and
cost difference. Note that S3 gateway endpoints do not support all S3 operations.

### Estimated Time
2-3 hours