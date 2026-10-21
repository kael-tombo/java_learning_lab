# Reactive Streams -- Common Mistakes
## Top 10 Common Mistakes
1. Blocking in reactive pipeline (subscribe().block())
2. Not handling backpressure
3. Using subscribe() without error handler
4. Leaking connections in WebClient
5. Missing Scheduler for blocking operations
6. Cold vs hot confusion
7. Not disposing subscriptions
8. Deeply nested flatMap chains
9. Testing with real time (not virtual time)
10. Assuming single-threaded execution
