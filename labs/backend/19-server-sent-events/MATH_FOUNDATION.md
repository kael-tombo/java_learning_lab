# Mathematical Foundation: SSE

## Connection Capacity
Max concurrent connections = thread_pool_size (MVC) or event_loop_size * N (WebFlux)

## Reconnection Probability
With retry interval r and failure probability p per attempt:
- Expected reconnection time = r / p
- Probability of reconnection within T seconds = 1 - (1-p)^(T/r)

## Bandwidth Calculation
Bandwidth = events_per_second * average_event_size
