# Interview: Security

Q: How does CSRF token work? A: Server generates random token, sends to client in form/page. Client includes token in state-changing requests. Server validates token equals stored value.

Q: What is SQL injection and how to prevent? A: Injecting SQL code via user input. Prevent with parameterized queries, ORM, input validation.

Q: What is CORS? A: Browser security mechanism controlling cross-origin requests.

Q: How to rate limit an API? A: Token bucket, sliding window, or fixed window counters.
