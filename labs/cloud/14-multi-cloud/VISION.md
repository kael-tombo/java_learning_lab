# Multi-Cloud - Vision

## The Big Picture
Multi-cloud is not "the same app in three clouds." It is a deliberate answer to a specific
risk — provider outage, pricing change, regulatory requirement, or negotiation leverage. The
honest version is usually *selective* redundancy, and the dishonest version is three
half-finished deployments.

## Why This Matters
Most multi-cloud programmes fail at the abstraction layer: a thin wrapper that unifies
compute but leaves IAM, networking, and data completely different, so the abstraction costs
a team and saves nothing.

## The Vision for This Lab
This lab decides what "multi-cloud" should mean for a specific organisation — which capability
gets redundancy, which gets portability, and which stays single-cloud — then builds the
portable core and measures what it cost.

## Learning Philosophy
1. Name the risk you are mitigating; "we might need it later" is not a reason
2. Abstract the interface, not the semantics
3. Identity and data are the hard parts; compute is the easy part
4. Portability has a carrying cost; budget for it or it will be cut

## Future Path
- 15-cloud-cost-optimization — the cost side of a multi-cloud portfolio
- 09-aws-security / 12-azure / 13-gcp — the provider-specific security models
- 14-incident-response — cross-provider failure handling

## Success Metrics
You have mastered multi-cloud when you can:
- [ ] Write a decision document naming the risk and the redundancy scope
- [ ] Build a portable application core with a thin provider adapter
- [ ] Identify honestly which parts are not portable and why
- [ ] Estimate the ongoing carrying cost of the redundancy you chose

## The Multi-Cloud Mindset
> Portability is insurance. Know the premium, know the exclusions, and know what happens when
the claim is made. An insurance policy you have never tested is not coverage.