# INTERVIEW QUESTIONS: Caching Architecture & Redis at Scale
## Lab 12 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What are Cache Penetration, Cache Breakdown, and Cache Avalanche? How do you prevent each?
**Answer**:
1. **Cache Penetration**: Requests for data that does not exist in DB or cache. Attackers exploit this to bypass cache and hit DB. *Fix*: Bloom filters or cache null values with a 60-second TTL.
2. **Cache Breakdown (Stampede)**: A single hot key expires, and thousands of concurrent requests miss cache simultaneously and hit the DB to reload it. *Fix*: Distributed mutex locking during cache rebuild or probabilistic early refresh.
3. **Cache Avalanche**: A massive number of keys expire at the exact same moment (e.g. all created with a 1-hour TTL). *Fix*: Add random jitter to TTLs so expirations are smoothly distributed across time.

---

## Staff / Principal Level (8+ Years)

### Q2: How does the XFetch algorithm prevent cache stampedes without using distributed locks?
**Answer**:
Distributed locks introduce contention, wait states, and failure modes if the lock-holding thread crashes.
The **XFetch (Probabilistic Early Expiration)** algorithm evaluates an expiration probability on every read:
$$\Delta \beta \ln(\text{random}()) > \text{expiry} - \text{now}$$
where $\Delta$ is the delta computation time (how long it took to compute the value), and $\beta > 0$ is an aggressiveness parameter.
- As the key approaches expiration, the probability that a read triggers a background asynchronous refresh increases smoothly.
- Exactly one or two concurrent read threads will probabilistically trigger the background refresh before the key actually expires.
- 99.99% of readers always receive a cache HIT with zero lock contention and zero latency penalty.
