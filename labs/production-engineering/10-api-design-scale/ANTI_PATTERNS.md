# ANTI-PATTERNS: API Design & Evolution
## Lab 10 | Production Engineering Academy

---

## Anti-Pattern 1: Offset Pagination on High-Volume Datasets

### The Mistake
Exposing `?page=N&size=50` on tables with millions of records.

### Why It Fails
- Query execution time scales linearly $O(N)$ with page depth.
- Users crawling deep pages thrash the database buffer cache.
- Records inserted or deleted while a client is browsing result in skipped or duplicate items.

### The Correct Production Fix
Use **Keyset / Cursor-Based Pagination** using indexed fields (`WHERE (created_at, id) < (cursor_ts, cursor_id)`).

---

## Anti-Pattern 2: Returning Unbounded Collections

### The Mistake
Exposing endpoints like `GET /api/v1/users/{id}/transactions` without default and maximum page size limits:
```java
@GetMapping("/transactions")
public List<Transaction> getTransactions(@PathVariable Long id) {
    return transactionRepository.findByUserId(id); // What if user has 500,000 transactions?
}
```

### Why It Fails
If a high-volume user or enterprise merchant makes a request, Hibernate fetches 500,000 entities into the JVM heap. Jackson attempts to serialize a 150 MB JSON string. The JVM heap exhausts, triggering an OutOfMemoryError and killing the pod.

### The Correct Production Fix
Always mandate pagination with a hard upper limit:
`@RequestParam(defaultValue = "20") @Max(100) int limit`.
