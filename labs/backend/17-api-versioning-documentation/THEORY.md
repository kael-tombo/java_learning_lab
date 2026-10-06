# Theory: API Versioning & Documentation

## Why Versioning Exists

An API is a published contract. Once clients depend on a response shape, changing it
breaks their code at runtime — often silently (a missing field becomes `null` in
deserialization) rather than loudly. Versioning is the mechanism for evolving the
contract without breaking existing consumers. The alternative, "always change the
API in place," is what causes the classic production incident where a JavaScript
SPA deploys at the same moment the backend does and every client gets 500s or,
worse, `null` fields rendered into the UI.

## The Compatibility Boundary

A change is **backward compatible** when old clients keep working:
- Adding a new endpoint or a new optional request field: safe.
- Adding a new field to a response: safe for JSON clients that ignore unknown
  fields (Jackson, `Gson` by default); unsafe for strict XML or generated clients
  with `additionalProperties` rejection.
- Removing a field, renaming a field, changing a type (`int` -> `string`),
  changing nullability, tightening validation: **breaking** — needs a new version.

## Versioning Strategies

1. **URI path versioning** (`/v1/users`): most visible, easiest to route, easiest
   to cache at CDN/edge, simplest for load balancers. Cost: controller
   duplication unless you factor shared logic into versioned services.
2. **Header versioning** (`Accept-Version: 2`): keeps URIs stable, but is invisible
   in browsers/curl one-liners and harder to cache (cache key must include the
   header).
3. **Media type versioning** (`Accept: application/vnd.acme.v2+json`): the most
   REST-pure; used by GitHub's custom media types. Highest friction for ad-hoc
   testing.
4. **Query parameter** (`?version=2`): should be avoided; pollutes caches and
   analytics and is easy to accidentally drop in one call site.

In practice most teams standardize on URI versioning and document the choice.

## Deprecation Lifecycle

Versioning without deprecation just accumulates dead versions. A sane policy:

1. Announce the new version and mark the old one deprecated in OpenAPI
   (`deprecated: true`, `@Operation(deprecated = true)`).
2. Emit `Deprecation` and `Sunset` response headers on old-version calls.
3. Monitor traffic to the old version; when it reaches zero (or below an
   agreed trickle), remove it. A common failure is deleting on a calendar date
   instead of on measured usage, and instead a straggler nightly ETL job owned
   by a team that no longer exists starts failing.

## Documentation as Contract

OpenAPI serves three roles: human-readable reference (Swagger UI via SpringDoc),
client/server stub generation (openapi-generator), and runtime validation. The
production-grade move is **contract-first**: the spec is the source of truth,
controllers implement generated interfaces, and a contract test
(Spring Cloud Contract / Pact) fails the build when the running API deviates
from the spec. Reverse-engineering the spec from annotations (SpringDoc's
default) drifts from what clients actually see.

## Failure Modes in Production

- **Silent nullability change**: server starts returning `null` for a field no
  one versioned; clients only notice when a downstream job computes garbage.
- **Version skew across replicas**: rolling deploy means v1 and v2 handlers
  coexist; a routing rule that keys on the wrong header strands some users on
  the new controller without the new fields populated.
- **Cache poisoning across versions**: a CDN keyed only on URL serves v1 payloads
  to v2 clients when header-based versioning is used.
- **Sunset ignored**: the `Sunset` header is emitted but nobody alerts on it;
  the old version is removed while a meaningful percentage of clients still
  call it.
- **Undocumented default change**: the "default version" is silently moved when
  `/v2/...` is added; every unversioned client jumps two major versions.

## References

- OpenAPI Specification 3.1
- SpringDoc OpenAPI documentation
- "Versioning in the Open Source Distribution" — Semantic Versioning 2.0.0
