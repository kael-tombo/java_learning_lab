# Quiz: Spring Security (JWT + Refresh Rotation)

## Q1
Why are access tokens short-lived (e.g. 15 min) while refresh tokens are long-lived?
a) Convention only b) Limits damage from a stolen access token; the refresh token stays server-tracked and revocable c) JWTs cannot be long d) Cookies require it
**Answer: b)**

## Q2
What is refresh-token rotation?
a) Changing the signing key hourly b) Each refresh issues a NEW refresh token and invalidates the old one c) Rotating log files d) Re-hashing passwords
**Answer: b)**

## Q3
What is refresh-token reuse detection?
a) Caching tokens b) If an already-rotated (old) refresh token is presented, treat it as theft: revoke the whole token family for that user c) Retrying requests d) Load balancing
**Answer: b)**

## Q4
How are JWTs verified with HMAC-SHA256?
a) Decryption b) Recompute the signature over `header.payload` with the secret and compare (constant-time) + check `exp`/`nbf` with clock-skew tolerance c) Ask the client d) Base64-decode only
**Answer: b)**

## Q5
Where should token revocation (blacklist) live?
a) In the JWT itself b) Server-side store (e.g. Redis) checked on each request, with TTL = token expiry c) LocalStorage d) Nowhere
**Answer: b)**

## Q6
Access token in `Authorization: Bearer` header vs refresh token in HttpOnly cookie — why the split?
a) No reason b) Bearer header = easy for APIsSPA fetch; HttpOnly+Secure cookie = JS cannot steal the long-lived refresh token via XSS c) Cookies are faster d) Headers cannot hold JWTs
**Answer: b)**

## Q7
What clock-skew tolerance is for?
a) DST parties b) `exp`/`nbf`/`iat` validation allows small drift (e.g. ±60s) between servers c) Slowing attackers d) Token compression
**Answer: b)**

## Q8
In Spring Security, where does JWT validation belong?
a) In the controller b) A `OncePerRequestFilter` populating `SecurityContextHolder` before authorization c) In `main()` d) In the view layer
**Answer: b)**

## Q9
Why must token comparison use constant-time equality?
a) Speed b) Prevent timing side-channels on signatures/hashes c) Style d) UTF-8
**Answer: b)**

## Q10
On logout, what must happen?
a) Nothing b) Revoke the refresh-token family AND blacklist the access token until its `exp` (or use very short access TTL) c) Delete the user d) Restart the server
**Answer: b)**
