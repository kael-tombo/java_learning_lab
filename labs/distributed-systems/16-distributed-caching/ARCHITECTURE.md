# Architecture — Distributed Caching

## Cache Topology
`
Application -> Cache Client (library)
                  |
        +---------+---------+
        |         |         |
    Redis        Memcached  Local (Caffeine)
    Cluster      Cluster    Cache
`

## Deployment Patterns
- **Co-located**: Cache on same node as application
- **Remote**: Cache cluster as separate service
- **Hybrid**: Local L1 + remote L2

## Redis Cluster Architecture
- 3-9 master nodes, each with 1+ replicas
- 16384 hash slots distributed across masters
- Automatic failover via Redis Sentinel or Cluster bus
