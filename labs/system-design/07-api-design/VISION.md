# API Design - Vision

## Why This Lab Exists
An API is the longest-lived artefact you will ship. A bad endpoint survives
three rewrites of the service behind it, because clients are not yours to
change. This lab exists to make the API the artefact you design first and guard
hardest, with HTTP semantics treated as a feature set rather than a transport.

## The Mental Model
Good API design is mostly *constraint adherence*. HTTP already defines the hard
parts correctly; most APIs re-invent them badly:

```
  Method  -> intent that survives method-override proxies
  Status  -> machine-actionable, not prose
  Cache   -> validators, so clients can revalidate cheaply
  Idem    -> Idempotency-Key, so retries are safe
  Version -> in the path, so it is visible in logs
```

## What You Should Be Able To Do
- Model a domain as resources with correct verbs, status codes, and error
  shapes (RFC 9457 problem details, not a bespoke envelope).
- Decide pagination style and justify it against offset drift and cost.
- Design idempotency for a `POST` that charges money, including key TTL.
- Version a breaking change and deprecate it without breaking clients.
- Define a real SLO for the endpoint and the headers that expose it.
- Say when to publish an event instead of exposing a REST resource.

## The Anti-Goals
- No 200 with a body containing `{"error": "..."}`.
- No unbounded list endpoints, ever.
- No API without an idempotency story on its side-effecting verbs.

## Success Criteria
You can hand someone a spec: resources, verbs, status codes, error model,
pagination, idempotency, versioning, auth, and rate-limit signalling — and each
choice has a one-line HTTP-rationale.

## How To Use This Lab
1. `THEORY.md` for resource modelling and HTTP semantics.
2. `MATH_FOUNDATION.md` for pagination cost, version churn, SLO math.
3. `CODE_DEEP_DIVE.md` for versioning, idempotency, and pagination in Java.
4. `MINI_PROJECT.md` to ship a versioned, idempotent API.
5. `REAL_WORLD_PROJECT.md` for a public API with an SLO and deprecation plan.
