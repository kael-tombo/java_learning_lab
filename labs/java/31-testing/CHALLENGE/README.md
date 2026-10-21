# CHALLENGE — Mocking Time

## Problem
Test code that depends on System.currentTimeMillis() or Instant.now() without modifying production code.

## Requirements
1. Create a Cache class that expires entries after a configurable TTL
2. Implement put(key, value) and get(key)
3. Implement cleanup() that removes expired entries
4. Test expiration WITHOUT using Thread.sleep()

## Hint
Use a Clock interface injected into the Cache. In production, use Clock.systemUTC(). In tests, use Clock.fixed(...).

## Extension
Test concurrent access to the cache with multiple threads calling put/get/cleanup simultaneously. Verify the cache remains consistent.
