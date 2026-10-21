# REAL_WORLD_PROJECT — Testing a REST API Service

## Goal
Create a complete test suite for an e-commerce REST API (OrderService, PaymentService, InventoryService).

## Structure
- OrderServiceTest — Mock PaymentService and InventoryService, test order lifecycle (create, cancel, refund)
- PaymentGatewayIntegrationTest — Use WireMock to stub payment provider responses
- InventoryIntegrationTest — Use Testcontainers with PostgreSQL for inventory repository tests
- E2ETest — Complete order-to-delivery workflow through all layers

## Deliverables
- 30+ unit tests
- 10+ integration tests
- 2 E2E smoke tests
- 80%+ branch coverage
- CI pipeline configuration

## Duration
2-3 hours
