# Lab 23: CQRS with Axon Framework

## Overview
Axon Framework implements CQRS (Command Query Responsibility Segregation) and Event Sourcing patterns. Learn command/query buses, event sourcing, sagas, and aggregate design.

## Topics Covered
- CQRS pattern fundamentals
- Command Bus and Query Bus
- Event Sourcing and event store
- Aggregate design and repositories
- Saga management (orchestration, choreography)
- Axon Configuration and auto-configuration
- Testing CQRS applications
- Distributed tracing with Axon

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- DDD knowledge helpful

## Getting Started
`ash
mvn spring-boot:run
# Axon Server: http://localhost:8024 (Dashboard)
`

## Key Dependencies
`xml
<dependency>
    <groupId>org.axonframework</groupId>
    <artifactId>axon-spring-boot-starter</artifactId>
    <version>4.9.3</version>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\23-cqrs-axon "THEORY.md") @"
# Theory: CQRS with Axon Framework

## 1. CQRS Pattern

CQRS separates read and write operations:
- **Commands**: Write operations that change state (CreateOrderCommand)
- **Queries**: Read operations that return state (FindOrderQuery)
- **Events**: Facts that happened (OrderCreatedEvent)

## 2. Event Sourcing

Instead of storing current state, store all events that led to current state:
- Event Store: Append-only log of all events
- Aggregate Root: Rebuilds state from event stream
- Snapshot: Periodic save of aggregate state
- Projection: Read model built from events

## 3. Axon Framework Components

- **CommandBus**: Routes commands to command handlers
- **QueryBus**: Routes queries to query handlers
- **EventBus**: Publishes events to event handlers
- **EventStore**: Persists events (appended log)
- **Aggregate**: Command model (write side)
- **Projection**: Read model (query side)
- **Saga**: Long-running business process

## 4. Aggregate Design

Aggregate is a cluster of domain objects treated as a unit:
- Annotated with @Aggregate
- @CommandHandler methods process commands
- @EventSourcingHandler methods rebuild state
- AggregateIdentifier uniquely identifies instance

## 5. Sagas

Sagas manage distributed transactions across aggregates/services:
- Choreography: Each service emits events that trigger next action
- Orchestration: Central coordinator directs each step
- Axon @Saga annotation marks saga class
- @StartSaga, @EndSaga, @SagaEventHandler
