# Vision — Strangler Fig Pattern

## The Big Picture

The Strangler Fig Pattern gradually replaces a legacy system by building
a new system around the edges of the old one. New functionality is added
to the new system while the legacy system continues to operate. Over
time, the legacy system is "strangled" until it can be decommissioned.

## Why This Matters

- **Incremental migration** — no big-bang rewrite risk.
- **Continuous delivery** — ship new functionality while migrating.
- **Risk mitigation** — legacy system keeps running during migration.
- **Business continuity** — no downtime during transition.
- **Learning opportunity** — validate new architecture incrementally.

## Guiding Principles

1. **Gradual replacement** — migrate functionality piece by piece.
2. **Coexistence** — old and new systems run in parallel.
3. **Routing layer** — intercept requests and route to old or new system.
4. **Event interception** — capture legacy system events for new system.
5. **Decommission legacy** — retire old system when fully replaced.

## Success Criteria

- New functionality is built in the new system.
- Legacy system continues to operate during migration.
- Traffic gradually shifts from old to new system.
- Legacy system is eventually decommissioned.
- No business disruption during migration.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Low risk | Temporary complexity of two systems |
| Incremental progress | Longer overall migration time |
| Business continuity | Routing and synchronization overhead |
| Learning opportunity | Dual maintenance during transition |

## The Road Ahead

The Strangler Fig Pattern is the safest approach to modernizing legacy
systems. Combined with microservices, event-driven architecture, and
domain-driven design, it enables a smooth transition to modern architecture.
