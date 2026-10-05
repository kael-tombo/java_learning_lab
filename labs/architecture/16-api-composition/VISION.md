# Vision — API Composition

## The Big Picture

API Composition aggregates data from multiple services into a single
response for the client. Instead of the client making multiple calls
to different services, a composition layer fetches data from all
required services and merges the results into one unified response.

## Why This Matters

- **Reduced client complexity** — one call instead of many.
- **Optimized payload** — only the needed data is returned.
- **Network efficiency** — fewer round trips.
- **Decoupled clients** — clients don't know about service topology.
- **Flexibility** — composition logic can change without client updates.

## Guiding Principles

1. **Single entry point** — one API call returns all needed data.
2. **Parallel fetching** — fetch from multiple services concurrently.
3. **Partial failure handling** — return available data when some services fail.
4. **Caching** — cache composed responses for performance.
5. **Transformation** — merge and format data for the client.

## Success Criteria

- Clients make a single API call for composed data.
- Data from multiple services is merged correctly.
- Partial failures don't fail the entire request.
- Response time is acceptable despite multiple backend calls.
- Composition logic is centralized and maintainable.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Simplified clients | Composition layer complexity |
| Fewer round trips | Potential bottleneck |
| Optimized payload | Partial failure handling complexity |
| Decoupled topology | Data consistency challenges |

## The Road Ahead

API Composition is a fundamental pattern in microservices architectures.
It's often implemented as part of an API Gateway or BFF layer, providing
a unified interface to clients while hiding service complexity.
