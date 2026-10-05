# VISION — HTTP Protocol: The Contract Every Web API Is Built On
> Where this lab takes you: from "it's just a GET" to reading a request line and header set and knowing what a proxy will do with it.

## The Arc
1. **Message syntax** — request line, status line, headers, CRLF rules, and the `Host` requirement.
2. **Methods & semantics** — safe/idempotent, status code families, and what "POST is wrong here" costs.
3. **Headers that matter** — `Content-Type`, `Transfer-Encoding` vs `Content-Length`, caching, `Vary`.
4. **Connection management** — persistent connections, keep-alive, pipelining, and their failure modes.
5. **Proxies & intermediaries** — request smuggling, hop-by-hop headers, and why the message on the wire differs from what your code sent.

## Milestones (checkable)
- [ ] M1: write a valid HTTP/1.1 request by hand over a raw socket and get a response.
- [ ] M2: explain what breaks if `Host` is missing, and how a server may respond.
- [ ] M3: describe a request smuggling scenario using `Content-Length` vs `Transfer-Encoding`.
- [ ] M4: choose correct status codes for a set of scenarios and defend each.
- [ ] M5: identify every hop-by-hop header and explain why a proxy must strip them.

## Core Competencies
- Message framing: what determines the end of headers and the end of the body.
- Method semantics (safe, idempotent, cacheable) and correct status code selection.
- Content negotiation, conditional requests (`If-None-Match`, `If-Modified-Since`), and caching.
- How intermediaries transform messages, and the security implications of that.

## Anti-Goals
- Assuming your library handles framing correctly without you knowing why.
- Using 200 for errors because the client "handles it anyway".
- Sending hop-by-hop headers end to end by accident.

## Interview Lens
- "What's the difference between idempotent and safe? Give me a method that breaks it."
- "Explain a request smuggling attack in terms of message framing."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: raw socket request, header experiments.
- Wk2 QUIZ/FLASHCARDS to 90%+; status code and caching drills.
- Wk3 MINI_PROJECT with a real HTTP server and a client you wrote.
- Wk4 REAL_WORLD_PROJECT: an API gateway sitting in front of a fragile upstream.

## Done = You Can
- Read any HTTP exchange at the byte level, explain its framing, and identify where
  a proxy or a caching layer would change its meaning.
