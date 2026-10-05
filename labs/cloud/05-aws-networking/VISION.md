# AWS Networking - Vision

## The Big Picture
Networking is the layer where cloud architecture becomes real. A VPC is not a diagram — it
is a set of route tables, security groups, and gateways whose defaults are chosen against
you and whose mistakes are invisible until traffic stops.

## Why This Matters
Most cloud outages that look like application bugs are network bugs: a security group that
was edited "temporarily", a route table that sends private traffic through an internet
gateway, DNS TTLs that hide a failover for an hour. This lab teaches you to see them.

## The Vision for This Lab
This lab builds a production-grade network topology from first principles — subnets, route
tables, NAT, endpoints, and DNS — then breaks it deliberately. The output is a design that
survives an AZ failure without anyone editing a security group at 2am.

## Learning Philosophy
1. Default-deny is the only posture that scales
2. Every routing path is explicit; implicit paths are outages waiting
3. Prefer private connectivity over public with auth on top
4. DNS is part of the network design, not an afterthought

## Future Path
- 09-aws-security — security groups, WAF, and identity in depth
- 14-multi-cloud — hybrid and cross-cloud connectivity
- 07-kubernetes — service networking inside the cluster

## Success Metrics
You have mastered AWS networking when you can:
- [ ] Lay out a three-AZ VPC and explain every route in the route tables
- [ ] Design security groups with no rule broader than necessary
- [ ] Explain what NAT Gateway does and does not protect
- [ ] Diagnose four connectivity failures from symptoms alone

## The Cloud Networking Mindset
> Assume the network will be misconfigured, because it will be. Design so that a
misconfiguration produces a clear refusal rather than a subtle, intermittent leak.