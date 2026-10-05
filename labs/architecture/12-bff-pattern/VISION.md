# Vision — Backend for Frontend (BFF) Pattern

## The Big Picture

The Backend for Frontend (BFF) pattern creates dedicated backend services
for each frontend client (web, mobile, tablet, partner API). Each BFF
is tailored to the specific needs of its frontend, aggregating data from
multiple microservices and formatting it optimally for the client.

## Why This Matters

- **Optimized for clients** — each frontend gets exactly the data it needs.
- **Reduced over-fetching** — no unnecessary data sent to clients.
- **Simplified frontend** — frontend doesn't aggregate from multiple services.
- **Independent evolution** — each BFF evolves with its frontend.
- **Security** — client-specific authentication and authorization.

## Guiding Principles

1. **One BFF per frontend** — web BFF, mobile BFF, partner BFF.
2. **Client-specific optimization** — tailor responses to client needs.
3. **Aggregation** — BFF calls multiple microservices and combines results.
4. **Transformation** — BFF formats data for the specific client.
5. **Decoupling** — frontend doesn't know about microservice topology.

## Success Criteria

- Each frontend has a dedicated BFF.
- BFFs aggregate data from multiple microservices.
- Responses are optimized for each client type.
- Frontend code is simplified (no multi-service aggregation).
- BFFs can evolve independently with their frontends.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Client optimization | More services to maintain |
| Simplified frontend | Potential BFF duplication |
| Independent evolution | Additional network hop |
| Tailored responses | BFF can become a bottleneck |

## The Road Ahead

The BFF pattern is essential in microservices architectures with multiple
client types. It provides the right balance between service autonomy
and client-specific optimization.
