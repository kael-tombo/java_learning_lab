# Quiz: REST API Design

## Q1
Which HTTP method must be idempotent: POST or PUT?
a) POST b) PUT c) Both d) Neither
**Answer: b) PUT (repeated identical PUTs have the same effect; POST does not guarantee this)**

## Q2
What status code should a successful resource creation return?
a) 200 b) 201 c) 204 d) 302
**Answer: b) 201 Created (with a `Location` header pointing at the new resource)**

## Q3
In the URL-shortener lab, why Base-62 instead of Base-64 for short keys?
a) Faster hashing b) URL-safe alphabet without `+`, `/`, `=` padding c) Shorter keys d) Encryption
**Answer: b)**

## Q4
Where should pagination parameters live in a REST API?
a) Request body of GET b) Query string (`?page=2&size=20`) c) HTTP headers only d) URL fragment
**Answer: b)**

## Q5
What is the token-bucket rate limiter in this lab protecting against?
a) SQL injection b) Abuse/brute-force of `shorten`/`resolve` per client IP c) CORS errors d) Memory leaks
**Answer: b)**

## Q6
`GET /urls/abc123` returns 404 for an unknown key. What should `POST /urls` with an invalid `longUrl` return?
a) 201 b) 400 Bad Request c) 404 d) 500
**Answer: b) 400 with a validation error body**

## Q7
Why return a `Location` header on creation instead of just the JSON body?
a) Required by TCP b) Lets clients navigate to the new resource without constructing URLs; follows HTTP semantics c) Faster DNS d) Encrypts the body
**Answer: b)**

## Q8
How should the short-key namespace handle collisions?
a) Ignore them b) Retry with a new random key / counter-salted hash, bounded retries, then fail with 503/409 c) Overwrite the old mapping d) Return 200
**Answer: b)**

## Q9
Which is the better status for a rate-limited client: 429 or 503?
a) 429 Too Many Requests (client should back off; include `Retry-After`) b) 503 always c) 200 with error JSON d) 301
**Answer: a)**

## Q10
Why must `resolve` be thread-safe under concurrent access?
a) Aesthetics b) Concurrent reads/writes to the key map and rate-limiter counters must not corrupt state or double-count c) HTTP/2 requires it d) It need not be
**Answer: b)**
