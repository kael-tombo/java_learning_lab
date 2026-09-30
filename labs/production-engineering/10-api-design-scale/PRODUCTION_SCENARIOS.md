# PRODUCTION SCENARIOS: API Design at Scale
## Lab 10 | Production Engineering Academy

---

## Scenario 1: The Scraping Bot & Deep Offset DB Meltdown

### Context
An e-commerce marketplace with 25 million products. The catalog search API used offset pagination:
`GET /api/v1/products?page=25000&size=50`
Which executed:
`SELECT * FROM products ORDER BY id LIMIT 50 OFFSET 1250000;`

### The Outage
A competitor deployed a distributed scraper crawling the entire catalog by incrementing `page` from 1 to 500,000 across 100 concurrent threads.
- As `OFFSET` crossed 100,000, query execution time surged from 3ms to 12,000ms.
- PostgreSQL buffer pool was thrashed as workers performed millions of disk buffer reads to discard offset rows.
- CPU hit 100%, query queue backed up, HikariCP connection pools in customer checkout services exhausted, taking down the entire website during daytime business hours.

### The Fix
1. Enforce max offset limit: `if (page * size > 1000) throw new BadRequestException("Offset exceeded. Use keyset pagination API /api/v2/products/stream?cursor=...")`.
2. Migrated the API to **Cursor-Based Pagination** using encoded base64 token `cursor=eyJpZCI6MTI1MDAwMCwidHMiOjE2OTU2MzQ1MDB9`.

---

## Scenario 2: The GraphQL Recursive Depth Denial of Service (DoS)

### Context
A social network launched a GraphQL endpoint to replace multiple REST APIs.

### The Attack
An attacker submitted a circular nested query:
```graphql
query MaliciousQuery {
  user(id: "123") {
    friends {
      friends {
        friends {
          friends {
            friends {
              id
              name
            }
          }
        }
      }
    }
  }
}
```
- The backend Java GraphQL engine recursively generated thousands of database queries (N+1 query explosion).
- A single 500-byte HTTP POST consumed 100% CPU on 8 application pods for 45 seconds, starving legitimate users.

### The Fix
1. Implemented **Max Query Depth Instrumentation** (`maxDepth = 5`).
2. Implemented **Query Complexity Scoring**: Each field has a weight; reject queries with total score $> 200$.
3. Used `DataLoader` to batch and cache identical user fetches into single `WHERE id IN (...)` SQL queries.
