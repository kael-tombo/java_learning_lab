# VISION — CSRF & XSS: The Injection-Response Pair
> Where this lab takes you: from "sanitize with `<b>`" to designing output encoding, token binding, and CSP as one system.

## The Arc
1. **XSS anatomy** — stored/reflected/DOM-based; the sink inventory; why HTML encoding is context-dependent.
2. **Encoding** — output encoding per context (HTML body, attribute, URL, JS, CSS) and the wrong-context trap.
3. **CSRF anatomy** — ambient authority (cookies), the forged-request primitive, token synchronisation.
4. **Defences** — synchroniser tokens, `SameSite`, `Origin`/`Referer` validation, double-submit.
5. **Containment** — CSP, HSTS, `frame-ancestors`, Trusted Types as the second line of defence.

## Milestones (checkable)
- [ ] M1: explain why `String.replace("<","")` is trivially bypassed and name three bypasses.
- [ ] M2: encode the same string for four contexts and show why one is not substitutable.
- [ ] M3: mount a reflected-XSS payload and then defend it with context-aware encoding.
- [ ] M4: execute a CSRF attack against a cookie-authenticated form, then add a token and watch it fail.
- [ ] M5: ship a CSP with no `unsafe-inline` and fix the resulting breakage.

## Core Competencies
- Choosing encoder by sink: HTML, attribute, JS string, URL, CSS.
- `SameSite=Lax|Strict|None` semantics and which CSRF variants they do and do not stop.
- Token storage/synchronisation trade-offs (server session vs double-submit).
- CSP as damage limitation: reporting endpoint, nonce discipline, report triage.

## Anti-Goals
- Blacklist-based filters presented as a primary defence.
- Encoding at input time instead of output time.
- Disabling CSRF globally to make a client work.

## Interview Lens
- "Why doesn't HTML-escaping fix a JavaScript-string context?"
- "`SameSite=Lax` stopped our CSRF test — is CSRF solved? Explain."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: exploit lab, then encode, then re-run the exploit.
- Wk2 QUIZ/FLASHCARDS to 90%+; model a CSP for a small app.
- Wk3 MINI_PROJECT with a real token flow and a reports endpoint.
- Wk4 REAL_WORLD_PROJECT: retrofit a legacy app without breaking integrations.

## Done = You Can
- Take an application, produce a sink inventory, and argue encoding/CSP/CSRF-token
  choices to a reviewer who asks "what breaks if we do that?"
