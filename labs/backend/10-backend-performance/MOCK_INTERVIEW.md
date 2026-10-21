# Mock Interview: Rate Limiter (Token Bucket + Sliding Window) (Lab 10)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Problem Understanding (5 min)

**Interviewer:** Design a rate limiter supporting both Token Bucket and Sliding Window strategies. What problem are we solving?

**Candidate:** Rate limiting controls the rate of requests to an API or service to prevent abuse, ensure fair resource allocation, and protect downstream systems. Common strategies include Token Bucket (burst-friendly smooth refill), Sliding Window Log (precise but memory-intensive), Fixed Window (simple but allows edge bursts), and Leaky Bucket (constant drain rate).

**Interviewer:** Compare Token Bucket and Sliding Window. When would you use each?

**Candidate:** Token Bucket allows bursts up to bucket size. Great for APIs that need to absorb traffic spikes like a login endpoint after password reset. Sliding Window Log provides precise control tracking the exact count of requests in the last N seconds. Better for strict rate adherence like 100 requests per minute exactly. Token Bucket uses O(1) memory per client. Sliding Window uses O(windowSize) because it stores timestamps.

**Interviewer:** What is the fixed window problem?

**Candidate:** Fixed window divides time into discrete windows (e.g., per minute). At the boundary of a window a burst can occur: 100 requests at 11:59:59 and 100 more at 12:00:00. This allows 200 requests in a two-second span despite a 100/minute limit. Sliding window solves this by evaluating the window continuously. Mixed approaches like sliding window counters approximate the sliding window using the previous window count and current window progress.

---

## Round 2: Medium Token Bucket Deep Dive (10 min)

**Interviewer:** Explain the Token Bucket algorithm in detail.

**Candidate:** The bucket holds up to maxTokens tokens. Each request consumes one token. A refill mechanism adds tokensPerRefill tokens every refillIntervalMs. My implementation uses lazy refill on tryConsume() compute elapsed = now - lastRefillTimestamp, calculate tokensToAdd = elapsed / refillIntervalMs, and top up the bucket capped at maxTokens. This avoids a background thread for refill.

**Interviewer:** How do you handle concurrency in token consumption?

**Candidate:** I use AtomicLong for available tokens and a compareAndSet loop. If availableTokens > 0 I CAS decrement. If CAS fails due to contention I retry. This is lock-free and scales well under high concurrency. The updateAndGet approach is availableTokens.updateAndGet(v -> v > 0 ? v - 1 : v) then checking if the result was a decrement.

**Interviewer:** Can you have race conditions between refill and consumption?

**Candidate:** The refill is also atomic it uses compareAndSet on lastRefillTimestamp to ensure only one thread performs the refill calculation. The token count is then updated with getAndUpdate. Between the refill and the consumption CAS there is a tiny window where the value could be stale but since both use atomic operations the final state is always consistent no token is created or destroyed.

**Interviewer:** How do you determine the optimal bucket size and refill rate?

**Candidate:** Bucket size = max allowed burst. If the API can handle 100 requests in a burst set bucket size to 100. Refill rate = steady state limit. If limit is 100 per minute refill rate = 100 / 60 tokens per second or about 1.67 tokens/sec. The refill interval is 1 / refillRate. For 100/min I set refillIntervalMs = 60000/100 = 600ms and tokensPerRefill = 1. This smooths the rate over time.

---

## Round 3: Medium-Hard Sliding Window Log (10 min)

**Interviewer:** Explain the Sliding Window Log approach.

**Candidate:** Each client has a queue of request timestamps. On each request I clean up expired timestamps older than now - windowSizeMs then check if the queue size is less than maxRequests. If so I add the current timestamp and allow. If queue is full I reject.

**Interviewer:** The cleanup sounds expensive. How do you optimize?

**Candidate:** I use ConcurrentLinkedDeque which is a lock-free doubly-linked list. Cleanup polls from the head while peekFirst() < cutoff. Since timestamps are monotonically increasing each timestamp is cleaned exactly once. Amortized cost is O(1) per request each timestamp is inserted once and removed once.

**Interviewer:** What is the memory cost and how do you prevent unbounded growth?

**Candidate:** Each client stores up to maxRequests timestamps. For 100 requests/second that is 100 Long values about 800 bytes. With 10,000 clients that is about 8MB acceptable. The risk is a client requests up to the limit then stops leaving stale timestamps. Cleanup handles this on the next request. For abandoned clients I add an idle timeout that evicts the entire client entry.

**Interviewer:** How does the sliding window counter approximation work as an alternative?

**Candidate:** Instead of storing all timestamps, store two counters: the count in the current fixed window and the count in the previous window. The estimate = previousCount * (1 - elapsedInCurrentWindow / windowSize) + currentCount. This uses O(1) memory per client and provides a good approximation. It is the approach used by Redis for rate limiting. The trade-off is slight imprecision at window boundaries vs O(windowSize) memory.

---

## Round 4: Hard Production and Distribution (15 min)

**Interviewer:** How would this rate limiter scale across multiple application instances?

**Candidate:** For distributed rate limiting the token count or timestamp queue must be shared. I use Redis with Lua scripts for atomic operations. Token Bucket becomes: local tokens = redis.call(GET, key) if tokens then if tokens > 0 then redis.call(DECR, key) return 1 else return 0 end else redis.call(SET, key, maxTokens-1, PX, windowMs) return 1 end. For Sliding Window, Redis ZREMRANGEBYSCORE + ZCARD on a sorted set handles timestamp management. Lua ensures atomicity.

**Interviewer:** How do you handle synchronized clocks in a distributed setting?

**Candidate:** Absolute time synchronization is hard but for rate limiting tight precision is not critical. A few hundred milliseconds of skew will not meaningfully affect a 1-minute window. If skew is severe (multi-second) I use Redis TIME command to get a consistent server timestamp rather than relying on application server clocks.

**Interviewer:** What metrics should a rate limiter expose?

**Candidate:** Per-client: allowed count, rejected count, remaining tokens, current rate (allowed / window). Global: active client count, total allowed/rejected, rejection rate. These are critical for capacity planning and identifying abusive clients. The RateLimitMetrics record captures all of these and can be serialized for monitoring systems.

**Interviewer:** How would you implement burst vs steady-state distinction?

**Candidate:** Hybrid approach: Token Bucket for burst allowance (e.g., 20 tokens) plus Sliding Window for steady-state rate (e.g., 100/min). A request passes if the token bucket has tokens AND the sliding window is under limit. This gives burst tolerance while preventing sustained abuse. It is the approach used by AWS API Gateway and Stripe.

**Interviewer:** How do you handle rate limiting for authenticated vs unauthenticated users?

**Candidate:** Different limits for different tiers. Unauthenticated: 10 req/min per IP. Authenticated basic: 100 req/min per API key. Premium: 1000 req/min. The rate limiter key combines client identifier and tier: ratelimit:ip:1.2.3.4 or ratelimit:apikey:abc123. The limit values come from configuration that maps tier to rate limit parameters. I also allow per-endpoint overrides for expensive operations.

---

## Round 5: Summary (5 min)

**Interviewer:** Summarize the key design decisions and trade-offs.

**Candidate:** (1) Token Bucket for burst tolerance vs Sliding Window for precision choose based on use case. (2) O(1) memory Token Bucket per client vs O(windowSize) Sliding Window. (3) AtomicLong CAS for in-memory lock-free rate limiting vs Redis Lua for distributed. (4) Exact sliding window log vs approximate sliding window counter trade memory for precision. (5) Per-client isolation ensures one abusive client does not affect others. The most important principle is fail-closed: when the rate limiter itself fails (e.g., Redis down), default to rejecting requests to protect downstream systems.
