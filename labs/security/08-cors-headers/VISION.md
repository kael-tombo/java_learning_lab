# VISION — CORS & Security Headers: Browser Policy as a Second Perimeter
> Where this lab takes you: from "add the CORS filter" to designing a policy where every header has a stated threat it reduces.

## The Arc
1. **Same-origin policy** — what the browser enforces, and why servers must opt in to cross-origin reads.
2. **Preflight** — the `OPTIONS` exchange, simple vs non-simple requests, why it is not a security boundary.
3. **CORS mechanics** — `Origin`, `Access-Control-Allow-*`, credentials, wildcard pitfalls.
4. **Security headers** — HSTS, CSP, `frame-ancestors`, `nosniff`, `Referrer-Policy`, COOP/COEP.
5. **Composition** — headers at app vs edge, CDN/proxy rewriting, and the misconfig audit.

## Milestones (checkable)
- [ ] M1: explain in one paragraph why CORS does not protect a non-browser client.
- [ ] M2: reproduce a preflight in devtools and read every header both sides send.
- [ ] M3: fix a broken SPA call by finding whether the failure is preflight, credentials, or wildcard.
- [ ] M4: set HSTS with preload and verify a browser refuses the HTTP fallback afterwards.
- [ ] M5: audit a set of response headers and name the attack each one mitigates.

## Core Competencies
- Why `Access-Control-Allow-Origin: *` plus credentials is invalid and what breaks.
- Origin allow-list matching (exact scheme+host+port) and why `endsWith` is a bug.
- Distinguishing CORS (browser reads) from CSRF (browser sends) — they need different fixes.
- Header precedence when an edge proxy and the app both set the same header.

## Anti-Goals
- Using CORS as an authentication or authorization control.
- Reflecting the `Origin` request header back without an allow-list check.
- Setting headers only in the app when a CDN terminates TLS in front of it.

## Interview Lens
- "Our CORS config is `allowedOrigins("*")` — what exactly is exposed?"
- "Which headers stop clickjacking, and which one stops MIME confusion?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: build a two-origin app and watch preflights in devtools.
- Wk2 QUIZ/FLASHCARDS to 90%+; header-by-header threat mapping.
- Wk3 MINI_PROJECT with an SPA, an API gateway, and a cookie-authenticated origin.
- Wk4 REAL_WORLD_PROJECT: enterprise multi-origin policy plus a header audit.

## Done = You Can
- Given a browser error about CORS, diagnose it in under five minutes, and explain the
  fix without ever widening the policy to `*`.
