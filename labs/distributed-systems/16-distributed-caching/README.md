# 16 - Distributed Caching

## Overview
Distributed caching accelerates data access by storing frequently used data across multiple nodes. This lab covers Memcached, Redis Cluster, cache coherency strategies, write-behind patterns, and cache invalidation techniques.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems
- Database and caching fundamentals

## Topics Covered
- Memcached architecture and protocol
- Redis Cluster and hash slots
- Cache coherency and consistency
- Write-through, write-behind, write-around
- Cache invalidation strategies
- Cache stampede prevention
- Multi-tier caching (L1/L2)
- Cache-aside and read-through patterns

## Package Structure
- com.distributed.distributedcaching — Core implementations
  - CacheClient.java — Abstract cache client
  - RedisClusterClient.java — Redis Cluster client
  - MemcachedClient.java — Memcached client
  - CacheAsideStrategy.java — Cache-aside pattern
  - WriteBehindCache.java — Write-behind implementation
  - CacheCoherencyManager.java — Coherency management
