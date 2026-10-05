# Vision — Sidecar and Ambassador Patterns

## The Big Picture

The Sidecar pattern deploys a helper component alongside the main
application in the same container (or pod), providing cross-cutting
concerns like logging, monitoring, proxying, and configuration. The
Ambassador pattern is a specialized sidecar that proxies network
calls to external services, handling retries, circuit breaking,
and logging.

## Why This Matters

- **Separation of concerns** — cross-cutting concerns live in the sidecar.
- **Language independence** — sidecar can be written in a different language.
- **Reusability** — same sidecar works with multiple services.
- **Consistency** — all services get the same cross-cutting behavior.
- **Operational simplicity** — infrastructure concerns are centralized.

## Guiding Principles

1. **Co-location** — sidecar runs alongside the main application.
2. **Shared lifecycle** — sidecar starts and stops with the main app.
3. **Network proxy** — ambassador proxies all outbound calls.
4. **Transparency** — main app is unaware of the sidecar's presence.
5. **Standardization** — same sidecar pattern across all services.

## Success Criteria

- Sidecar handles cross-cutting concerns transparently.
- Main application code is unchanged by sidecar addition.
- Sidecar can be updated independently of the main application.
- All services use the same sidecar pattern consistently.
- Sidecar failures don't crash the main application.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Separation of concerns | Additional resource consumption |
| Language independence | Operational complexity |
| Reusability | Network hop for proxied calls |
| Consistency | Debugging complexity |

## The Road Ahead

Sidecar and Ambassador patterns are foundational for service mesh
architectures. They enable consistent, reusable infrastructure
behavior across all services without code changes.
