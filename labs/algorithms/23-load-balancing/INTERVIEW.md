# Interview Questions: Load Balancing

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 346 Moving Average from Data Stream | Easy | Google, Amazon | Sliding window |
| LC 362 Design Hit Counter | Medium | Google, Amazon, Microsoft | Queue / circular buffer |
| LC 642 Design Search Autocomplete | Hard | Google, Microsoft | Trie + min-heap |
| LC 895 Maximum Frequency Stack | Hard | Google, Amazon | Frequency map + stack |

Note: Load balancing is primarily a **system design** topic with few direct LeetCode equivalents.

## NeetCode Reference
Not directly covered as a standalone topic. System design problems (Design WhatsApp, Design Netflix) discuss load balancing.

## Company-Specific Questions
### Google
- Design a consistent hashing ring for cache sharding across thousands of nodes
- How does Google's Global Front End (GFE) balance traffic across regions?
- Design a load balancer for YouTube live streaming with geo-affinity

### Microsoft
- How does Azure Traffic Manager distribute requests across regions?
- Design a load balancer for Office 365 that handles session affinity
- Explain NLB vs ALB vs ILB in Azure networking

### Meta
- Design the load balancing layer for Facebook's feed serving infrastructure
- How does consistent hashing work for Memcache distribution?
- Design a load balancer with weighted routing for canary deployments

### Amazon
- How does AWS ALB distribute requests across targets?
- Design a load balancer for Amazon Prime Video with Sticky Sessions
- Explain Route 53 latency-based routing vs geolocation routing

### Apple
- Design a load balancer for iCloud services with data locality constraints
- How does Apple Push Notification service scale across regions?
- Implement a health-check system for load-balanced server pools

### Oracle
- How does Oracle Cloud Load Balancer handle SSL termination?
- Design a load balancing strategy for Oracle RAC database clusters
- Explain Oracle WebLogic clustering distribution algorithms

## Real Production Scenarios
- Scenario 1: CDN edge load balancing - distributing requests across origin servers based on geographic location, health, and capacity using consistent hashing
- Scenario 2: Microservices API gateway - implementing rate limiting, circuit breakers, and request distribution for an internal service mesh
- Scenario 3: Database read replica balancing - troubleshooting uneven load distribution across PostgreSQL read replicas due to connection pooling misconfiguration

## Interview Tips
- Understand Round Robin, Least Connections, Weighted, and IP Hash algorithms
- Know the difference between L4 (transport) and L7 (application) load balancing
- Be ready to discuss consistent hashing vs rendezvous hashing for distributed caching
- Common edge cases: slow starts (warm-up), connection draining, health check failures

## Java-Specific Considerations
- Netty and Spring Cloud Gateway for building custom load balancers
- Ribbon (deprecated) / Spring Cloud LoadBalancer for client-side load balancing
- Consistent hashing: implement with TreeMap and 	ailMap(k) for ring lookups
- Pitfall: virtual nodes in consistent hashing are critical to avoid hotspotting
- Pitfall: sticky sessions cause uneven load; prefer distributed sessions (Redis)
- java.util.concurrent.atomic.AtomicInteger for round-robin counter with thread safety
