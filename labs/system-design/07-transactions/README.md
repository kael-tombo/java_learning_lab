# Distributed Transactions

## Overview
This lab covers distributed transaction patterns: Two-Phase Commit (2PC), Saga (choreography & orchestration), Calvin/Spanner deterministic approaches, and compensation-based designs for microservices.

## Learning Objectives
- Implement 2PC coordinator and participants
- Design Saga orchestrators with compensation logic
- Apply exactly-once semantics with idempotency keys
- Handle partial failures and timeouts in distributed flows
- Choose the right pattern for consistency vs latency tradeoffs

## Prerequisites
- ACID transaction basics
- Message queues (Kafka, RabbitMQ)
- CAP theorem understanding

## Topics Covered
1. Two-Phase Commit (2PC) and Three-Phase Commit (3PC)
2. Saga pattern: choreography vs orchestration
3. Compensating transaction design
4. Outbox pattern for reliable event publishing
5. Idempotency and exactly-once processing
6. Calvin/Spanner deterministic transactions