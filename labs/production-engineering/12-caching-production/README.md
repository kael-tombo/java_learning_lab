# Lab 12: Caching Strategies & Cache Invalidation
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 8 hours | **Level**: Advanced | **Domain**: Performance

---

## 🎯 Objectives

- Choose the right caching strategy (write-through, write-behind, cache-aside)
- Implement multi-level caching (L1 local + L2 Redis)
- Handle cache stampede (thundering herd) and dog-pile effect
- Design cache invalidation without downtime
- Configure Caffeine and Redis cache in Spring Boot
- Monitor cache hit rates and identify cache misses
- Understand when caching makes things worse

---

## 📖 Real-World Context

**"Cache Invalidation: The Second Hard Problem"**: An e-commerce site cached product prices for 60 minutes. During a flash sale, prices were updated in the database. But cached prices showed old prices for up to 60 minutes — customers bought at the wrong price. The company had to honor those prices (legal requirement), losing $240,000. Cache invalidation design is a business-critical architectural decision.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Cache patterns, invalidation strategies, cache math |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) — | Cache stampede, stale data incidents, Redis failures |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Caffeine, Redis, Spring Cache abstraction |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Cache topology decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Cache failure and stale data runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Caching interview questions |
| [EXERCISES.md](./EXERCISES.md) | Implement cache stampede prevention |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Caching anti-patterns |
| [CHECKLIST.md](./CHECKLIST.md) | Cache production readiness |

---

## ⚙️ Multi-Level Cache Configuration

```java
@Configuration
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redis) {
        // L1: Local Caffeine cache (per-instance, fastest)
        CaffeineCacheManager l1 = new CaffeineCacheManager();
        l1.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(Duration.ofSeconds(30))  // Short TTL — freshness
            .recordStats());  // Enable hit/miss metrics
        
        // L2: Redis cache (shared across all instances)
        RedisCacheManager l2 = RedisCacheManager.builder(redis)
            .cacheDefaults(RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(10))
                .disableCachingNullValues()
                .serializeValuesWith(RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer())))
            .build();
        
        // Combine: check L1 first, then L2
        return new CompositeCacheManager(l1, l2);
    }
}
```

---

## 🔗 Related Labs
- Lab 05: [Database Production](../05-database-production/)
- Lab 15: [Performance Engineering](../15-performance-engineering/)
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
