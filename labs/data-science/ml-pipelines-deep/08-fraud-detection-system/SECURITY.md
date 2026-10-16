# Fraud Detection System - Security

## Abuse surface
- Rate-limit scoring endpoints; attackers probe thresholds with synthetic traffic.
- Never reveal the exact threshold or rule text in responses; return generic outcomes.
- Watch for probing patterns: many near-identical low-value attempts from one source.

## Data handling
- Redact raw account identifiers in logs where policy requires; join by token.
- Restrict review-queue access; fraud labels are sensitive.
- Encrypt feature stores and decision logs at rest and in transit.

## Model and rules
- Version rules and thresholds; unauthorized edits are a direct fraud enabler.
- Validate label sources before retraining; poisoned labels become blind spots.
- Keep an emergency block path (rule kill-switch) with audited use.

## Resilience
- Safe defaults on timeout or feature outage; alert on every fallback.
- Adversarial adaptation is expected; schedule rule and feature reviews.

## Probing defenses
- Detect near-identical low-value bursts from single sources automatically.
- Slow responses to suspected probes; never confirm or deny the boundary.
- Rotate rule text and thresholds on schedule so learned boundaries expire.

## Reviewer operations
- Limit queue visibility to assigned cases; bulk export needs approval.
- Separate reviewer roles from rule-edit roles; no self-approved coverage.
- Audit label changes with before/after values and reviewer identity.

## Kill-switch governance
- Emergency block paths require two-person authorization with expiry.
- Log every kill-switch activation with scope, reason, and duration.
- Review activations weekly; stale blocks become denial of service.

## Supply-chain checks
- Verify model and rule artifact signatures at load time against the registry.
- Pin feature-store clients; unpinned reads risk silent schema drift.
- Rehearse rollback of rules, thresholds, and models independently.

## Data minimization
- Score on the minimum features the operating point actually needs.
- Purge raw identifiers after the maturity window closes where policy allows.
- Document retention per table; expired data deletes on schedule, not on request.
