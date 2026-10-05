# Mini Project — Event-Driven Architecture (Advanced)

## Goal

Build an advanced event-driven system with event streaming, CQRS
integration, and complex event processing. Demonstrate real-time
analytics, event replay, and pattern detection across event streams.

## Requirements

### Event Streaming Platform

**Apache Kafka (or equivalent):**
- Topics: `orders`, `payments`, `inventory`, `notifications`
- Partitioned by entity ID for ordering
- Configurable retention policies

### Producers

1. **Order Service** — publishes `OrderCreated`, `OrderCancelled`, `OrderShipped`
2. **Payment Service** — publishes `PaymentReceived`, `PaymentFailed`
3. **Inventory Service** — publishes `StockReserved`, `StockReleased`

### Stream Processors

1. **Real-time Analytics**
   - Count orders per minute
   - Calculate revenue in real-time
   - Detect trending products

2. **Complex Event Processing**
   - Detect fraud patterns (multiple failed payments)
   - Identify high-value customers
   - Alert on inventory shortages

3. **CQRS Projections**
   - Build read models from event streams
   - Update projections in real-time
   - Support temporal queries

### Consumers

1. **Notification Service** — reacts to all events
2. **Audit Service** — records all events for compliance
3. **Analytics Dashboard** — real-time metrics

## Technical Specifications

1. **Event streaming**
   - Kafka topics with partitioning
   - Event schema registry (Avro)
   - Consumer groups for parallel processing

2. **Stream processing**
   - Kafka Streams or Flink for real-time processing
   - Windowed aggregations (tumbling, hopping, sliding)
   - Pattern detection with CEP library

3. **CQRS integration**
   - Event-sourced write model
   - Real-time read model projections
   - Temporal query support

4. **Event replay**
   - Replay events from any point in time
   - Rebuild projections from scratch
   - Support for debugging and recovery

## Steps

1. Set up Kafka cluster with schema registry
2. Implement event producers (Order, Payment, Inventory)
3. Build real-time analytics processor
4. Implement complex event processing patterns
5. Build CQRS projections from event streams
6. Implement notification and audit consumers
7. Add event replay capability
8. Write tests for stream processing
9. Test event replay and projection rebuilding

## Acceptance Criteria

- [ ] Events are published to Kafka topics
- [ ] Real-time analytics process events with low latency
- [ ] Complex event patterns are detected correctly
- [ ] CQRS projections update in real-time
- [ ] Events can be replayed from any point
- [ ] Projections can be rebuilt from scratch
- [ ] Consumers process events in parallel

## Stretch Goals

- Implement event sourcing with snapshots
- Add machine learning for pattern detection
- Implement event-driven sagas
- Add event stream monitoring and alerting
