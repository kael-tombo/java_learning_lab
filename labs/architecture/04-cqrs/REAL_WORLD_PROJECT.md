# Real-World Project — CQRS

## Scenario

A social media platform handles millions of posts, comments, and
interactions daily. The write path must enforce complex business rules
(content moderation, rate limits, privacy settings), while the read
path must serve personalized feeds, search results, and analytics with
sub-100ms latency. A single data model cannot optimize for both.

## System Overview

The platform separates command and query responsibilities:

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Command API | Accept and validate commands | Node.js/Go |
| Write Model | Enforce business rules, store events | PostgreSQL + Event Store |
| Event Bus | Propagate domain events | Apache Kafka |
| Read Model Builders | Project events into read models | Kafka Consumers |
| Read Model Stores | Serve queries | Elasticsearch, Redis, Cassandra |
| Query API | Serve read models | GraphQL/REST |

## Architecture Decisions

### Command Side
- Commands represent user intent: `CreatePost`, `AddComment`, `LikePost`
- Write model enforces invariants: rate limits, privacy, moderation
- Commands produce domain events stored in event store
- Synchronous validation with immediate feedback to users

### Query Side
- Multiple read models optimized for different queries:
  - **Feed Service**: Personalized timeline (Redis sorted sets)
  - **Search Service**: Full-text search (Elasticsearch)
  - **Analytics Service**: Aggregated metrics (ClickHouse)
  - **Profile Service**: User profiles and stats (Cassandra)
- Read models are updated asynchronously via Kafka consumers
- Eventual consistency: feed updates within 1-2 seconds

### Consistency Strategy
- **Strong consistency** for command validation (check before write)
- **Eventual consistency** for read models (acceptable lag)
- **Read-your-writes** consistency via temporary cache after command

## Implementation Phases

### Phase 1: Foundation
1. Implement command handling with validation
2. Set up event store and event bus
3. Build first read model (feed)
4. Implement read model projection from events

### Phase 2: Scale
5. Add search read model with Elasticsearch
6. Implement read model rebuild tooling
7. Add caching layer for hot queries
8. Implement read-your-writes consistency

### Phase 3: Optimize
9. Optimize read model projections for throughput
10. Add read model monitoring and lag alerting
11. Implement query result caching with invalidation
12. Add read model sharding for scale

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Martin Fowler — CQRS**: https://martinfowler.com/bliki/CQRS.html
  Martin Fowler's overview of CQRS, explaining when to use it,
  the separation of commands and queries, and trade-offs involved.

- **Microsoft Azure — CQRS Pattern**: https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
  Microsoft's Azure architecture center guidance on CQRS,
  including implementation patterns and when to apply the pattern.

## Success Metrics

- Command processing latency: p99 under 200ms
- Query latency: p99 under 100ms
- Read model lag: under 2 seconds
- Read model rebuild time: under 30 minutes
- Zero data loss in read model projections

## Lessons from Production

1. **Don't start with CQRS** — begin with a simpler architecture and
   introduce CQRS when read/write divergence justifies the complexity.

2. **Plan for read model rebuilds** — projections will have bugs; the
   ability to rebuild read models from the event log is essential.

3. **Monitor projection lag** — stale read models erode user trust;
   alert on lag before users notice.

4. **Read-your-writes matters** — users expect to see their own changes
   immediately; implement this even if the rest is eventually consistent.
