# Exercises: REST API Design (URL Shortener)

## Exercise 1: Design the API Contract
Write an OpenAPI sketch for `POST /urls` (shorten) and `GET /{key}` (resolve):
request/response shapes, status codes (201/400/404/429), and error envelope.
Include the `Location` header on creation.

## Exercise 2: Collision Handling
Implement `shorten` with counter-salted Base-62 keys and bounded retry on
collision (e.g. 5 attempts). Write a test that forces collisions with a stubbed
key generator and asserts eventual success or a clean `409`.

## Exercise 3: Rate Limiting
Add an IP-based token-bucket limiter to `shorten`. Write a test: burst of N
requests → first K succeed, rest get `429` with a `Retry-After` header.

## Exercise 4: Custom Aliases
Support `customAlias` with validation (length, charset `[A-Za-z0-9_-]`,
reserved words like `health`, `urls`). Return `409` when taken.

## Exercise 5: Expiry + Analytics
Add optional TTL per short URL (expired keys → `404`/`410`) and an atomic
click counter on `resolve`. Load-test `resolve` with 50 threads and assert no
lost increments.
