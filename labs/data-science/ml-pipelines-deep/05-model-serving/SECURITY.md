# Model Serving - Security

## Input handling
- Validate schema strictly: types, ranges, lengths, and units before scoring.
- Reject or clamp out-of-range values; log rejections with version.
- Bound request size and batch size to cap compute per call.

## Exposure
- Authenticate callers and rate-limit per key; model endpoints are abuse targets.
- Never echo training data or weights in errors; return generic failure messages.
- Version-pin responses so clients cannot force a downgrade silently.

## Supply chain
- Sign model artifacts; verify hash at load time against the registry record.
- Pin serving dependencies; rebuild images from locked files.
- Separate deploy permission from promote permission.

## Logging
- Log predictions without raw sensitive fields where policy requires redaction.
- Retain enough to replay incidents: version, timestamp, schema version, decision.

## Model extraction awareness
- Repeated near-identical queries can probe decision boundaries; watch per-key patterns.
- Rate limits plus query-diversity alarms catch systematic extraction attempts.
- Return scores at the precision clients need, not full float internals.

## Dependency and image hygiene
- Rebuild serving images from locked dependency files; test the rebuild monthly.
- Scan model-server images for known issues before promotion, not after.
- Keep a minimal base image so the attack surface stays reviewable.

## Tenant and key isolation
- Scope API keys per client with separate quotas; one compromised key must not starve others.
- Isolate per-tenant batch queues so a burst from one cannot stall the rest.
- Audit key creation, scope changes, and revocation with timestamps.

## Incident response
- Define who can revoke keys, block traffic, or roll versions during an attack.
- Practice the block-and-roll drill on staging; untested powers fail under pressure.
- Preserve forensic logs (versions, keys, timestamps) before rotating credentials.

## Privacy boundaries
- Treat feature vectors as sensitive: they may encode user behavior indirectly.
- Apply retention limits to request logs; aggregate early where detail is unnecessary.
- Document which fields are redacted and verify redaction in replay tests.
