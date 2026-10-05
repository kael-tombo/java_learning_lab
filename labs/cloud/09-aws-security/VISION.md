# AWS Security - Vision

## The Big Picture
Cloud security is a graph of who can do what, evaluated at every request. IAM is not a
settings page; it is an authorisation system with an evaluation order, implicit grants you
cannot see, and permission boundaries that quietly cap everything.

## Why This Matters
The most common cloud breach is not an exploit. It is a role with `*:*` on `*`, created
"temporarily" during an incident, that became permanent. This lab teaches you to design
privilege so that an incident responder needs a ticket rather than an exception.

## The Vision for This Lab
This lab works from policy evaluation upward: IAM policies and their evaluation order, KMS
envelope encryption, WAF rules, and threat detection. The goal is a security posture you can
explain, not a list of services you have enabled.

## Learning Philosophy
1. Least privilege is a design constraint, not a review step
2. Deny is a safety net, not a strategy — a broken policy should be loud
3. Encryption is only as good as key policy
4. Detect and respond matter as much as prevent

## Future Path
- 13-secrets-management — where credentials actually belong
- 14-zero-trust-architecture — the architecture-level view
- 10-aws-serverless — identity in a per-request execution model

## Success Metrics
You have mastered AWS security when you can:
- [ ] Write an IAM policy that passes the policy simulator
- [ ] Explain evaluation order and why an explicit Allow cannot override a Deny
- [ ] Implement envelope encryption with a customer-managed key
- [ ] Write WAF rules for two real attack patterns

## The Security Mindset
> Every permission you grant is a decision someone must defend in an audit. If you cannot
explain why a role needs a specific action, the answer is to delete the action.