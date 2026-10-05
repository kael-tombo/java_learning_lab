# Mini Project — Backend for Frontend (BFF) Pattern

## Goal

Build an e-commerce platform with two BFFs: one for the web frontend
and one for the mobile app. Each BFF aggregates data from multiple
microservices and formats responses optimally for its client.

## Requirements

### Microservices

1. **Product Service** — product catalog, search, details
2. **Cart Service** — shopping cart management
3. **User Service** — user profiles, authentication
4. **Order Service** — order history, order details
5. **Review Service** — product reviews and ratings

### Web BFF

**Optimized for desktop browser:**
- Rich product details with all attributes
- Full navigation and filtering options
- Comprehensive order history with pagination
- Reviews with full text and images

**Endpoints:**
- `GET /web/products` — product list with full details
- `GET /web/products/{id}` — product detail with reviews
- `GET /web/cart` — cart with product details
- `GET /web/orders` — order history with full details
- `GET /web/users/{id}` — user profile with preferences

### Mobile BFF

**Optimized for mobile app:**
- Minimal payload (only essential fields)
- Compressed images and data
- Simplified navigation
- Offline-friendly data structure

**Endpoints:**
- `GET /mobile/products` — product list with minimal fields
- `GET /mobile/products/{id}` — product detail (essential info only)
- `GET /mobile/cart` — cart with minimal product info
- `GET /mobile/orders` — recent orders (last 10)
- `GET /mobile/users/{id}` — user profile (basic info)

## Technical Specifications

1. **Aggregation**
   - BFF calls multiple microservices
   - Combines results into single response
   - Handles partial failures gracefully

2. **Transformation**
   - Web BFF: full data, rich formatting
   - Mobile BFF: minimal data, compressed
   - Different DTOs for each client type

3. **Caching**
   - Cache frequently accessed data
   - Client-specific cache keys
   - Cache invalidation on data changes

4. **Error handling**
   - Graceful degradation when services fail
   - Client-appropriate error messages
   - Fallback data where possible

## Steps

1. Set up microservices (or mocks)
2. Implement Web BFF with full aggregation
3. Implement Mobile BFF with minimal aggregation
4. Add transformation logic for each client type
5. Implement caching layer
6. Add error handling and graceful degradation
7. Write tests for each BFF
8. Compare payload sizes between BFFs

## Acceptance Criteria

- [ ] Web BFF returns full, rich data
- [ ] Mobile BFF returns minimal, optimized data
- [ ] Both BFFs aggregate from multiple services
- [ ] Mobile payload is significantly smaller than web payload
- [ ] BFFs handle service failures gracefully
- [ ] Each BFF can be deployed independently

## Stretch Goals

- Add GraphQL BFF for flexible queries
- Implement BFF for partner/third-party API
- Add real-time updates via WebSocket BFF
- Implement BFF-level authentication and authorization
