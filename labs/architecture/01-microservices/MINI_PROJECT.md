# Mini Project — Microservices Architecture

## Goal

Build a small microservices system with two services that communicate
synchronously (REST) and asynchronously (message broker), demonstrating
service decomposition, independent deployment, and inter-service communication.

## Requirements

### Service A: Order Service
- REST API to create and query orders
- Stores orders in its own database
- Publishes `OrderCreated` events to a message broker

### Service B: Notification Service
- Subscribes to `OrderCreated` events
- Sends a confirmation "email" (log to console for simplicity)
- Exposes a health check endpoint

## Technical Specifications

1. **Service decomposition**
   - Each service runs on a different port
   - Each service has its own database (or schema)
   - No shared tables between services

2. **Synchronous communication**
   - Order Service exposes `GET /orders/{id}`
   - Notification Service can call Order Service to fetch order details

3. **Asynchronous communication**
   - Use a message broker (RabbitMQ, Kafka, or in-memory queue for simplicity)
   - Order Service publishes events after persisting
   - Notification Service consumes events independently

4. **Resilience**
   - Add timeout and retry logic for inter-service calls
   - Handle message broker unavailability gracefully

5. **Observability**
   - Add structured logging with correlation IDs
   - Expose basic metrics (request count, error rate)

## Steps

1. Scaffold two separate service projects
2. Implement Order Service with CRUD operations
3. Set up message broker and event publishing
4. Implement Notification Service with event consumer
5. Add synchronous REST call from Notification to Order Service
6. Add resilience patterns (timeout, retry, circuit breaker)
7. Add logging and metrics
8. Write integration tests covering the full flow

## Acceptance Criteria

- [ ] Both services start independently
- [ ] Creating an order triggers a notification
- [ ] Services can be deployed separately
- [ ] Inter-service call has timeout and retry
- [ ] Correlation IDs appear in logs across services
- [ ] Integration test passes end-to-end

## Stretch Goals

- Add an API Gateway that routes to both services
- Implement event sourcing for the Order Service
- Add Docker Compose for local development
- Implement distributed tracing with OpenTelemetry
