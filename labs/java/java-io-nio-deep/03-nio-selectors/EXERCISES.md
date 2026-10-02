# EXERCISES — Selectors

## 1. The missing `remove()` (beginner)
Comment out `it.remove()` and start the reactor with one idle client.
Observe CPU (spin). Explain why the same key re-fires forever.

## 2. Port-0 reasoning (beginner)
Hard-code port 8080, start two reactors. Record the failure
(`BindException`). Restore port 0 and explain why tests must never assume
fixed ports (recall the module-25 lesson).

## 3. Partial-write stress (intermediate)
Send a 10 KB message through the 256-byte echo path. Does the response
match? Fix `handleRead`/`write` to loop on remainder and re-register
`OP_WRITE` when `write` returns short.

## 4. Slow-client DoS (intermediate)
Add a client that connects and sends 1 byte/minute. Measure reactor
responsiveness for other clients. Then add per-connection read deadlines
and close idle channels — the standard mitigation.

## 5. Reactor + worker pool (advanced)
Move echo handling off the reactor thread into a fixed pool (reactor only
accepts/reads into a queue). Benchmark 500 concurrent clients before/after
with one blocking handler (`sleep 50ms`) — show `λ` collapse without the
pool (Little's-law prediction from MATH_FOUNDATION).
