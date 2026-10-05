# Mini Project — API Composition

## Goal

Build an API composition layer that aggregates data from multiple
microservices into a single response. Demonstrate parallel fetching,
partial failure handling, and response transformation.

## Requirements

### Microservices

1. **User Service** — user profiles, preferences
2. **Order Service** — order history, order details
3. **Product Service** — product catalog, pricing
4. **Review Service** — product reviews and ratings

### Composition API

**Endpoint: `GET /dashboard/{userId}`**

Composed response includes:
- User profile (from User Service)
- Recent orders (from Order Service)
- Order details with product info (from Order + Product Services)
- Product reviews (from Review Service)

**Response structure:**
```json
{
  "user": { "id": 1, "name": "John", "email": "john@example.com" },
  "recentOrders": [
    {
      "id": 101, "date": "2026-10-01", "total": 150.00,
      "items": [
        { "productId": 5, "name": "Widget", "price": 50.00, "qty": 3 }
      ]
    }
  ],
  "recommendedProducts": [
    { "id": 10, "name": "Gadget", "price": 99.99, "rating": 4.5 }
  ]
}
```

## Technical Specifications

1. **Parallel fetching**
   - Fetch from all services concurrently
   - Use CompletableFuture or reactive programming
   - Set timeout for each service call

2. **Partial failure handling**
   - If one service fails, return data from others
   - Include error indicator for failed sections
   - Log failures for monitoring

3. **Data merging**
   - Merge order data with product data
   - Calculate derived fields (totals, ratings)
   - Format for client consumption

4. **Caching**
   - Cache individual service responses
   - Cache composed responses with short TTL
   - Invalidate cache on data changes

## Steps

1. Set up microservices (or mocks)
2. Implement composition layer with parallel fetching
3. Add data merging logic
4. Implement partial failure handling
5. Add caching layer
6. Add timeout handling
7. Write tests for happy path
8. Write tests for partial failures
9. Test caching behavior

## Acceptance Criteria

- [ ] Dashboard returns composed data from all services
- [ ] Service calls execute in parallel
- [ ] Partial failure returns available data with error indicator
- [ ] Composed response is correctly formatted
- [ ] Caching improves response time
- [ ] Timeouts prevent slow services from blocking

## Stretch Goals

- Implement GraphQL composition layer
- Add field-level caching
- Implement request batching
- Add composition-level rate limiting
