# Lab 05: RESTful Services (ORDS + APEX) — Vision

## Where this lab takes you
From an APEX application with no external interface to a versioned, OAuth2-
secured JSON API, an outbound payment-gateway call, and the ability to debug a
500 from `ords_log`.

## The Arc
1. **API shape** — versioning, resource design, and what belongs in a URL.
2. **ORDS** — exposing database objects as REST with real control.
3. **Auto-REST vs custom** — when a table endpoint is enough and when not.
4. **OAuth2** — client credentials, privileges, and token lifecycle.
5. **Outbound** — calling an external API from APEX with `APEX_WEB_SERVICE`.
6. **JSON handling** — `APEX_JSON` and the difference between parse and build.
7. **Debugging** — reading `ords_log` when the response is a 500.

## Milestones (checkable)
- [ ] M1: Design and publish `catalog/v1` endpoints with named resources.
- [ ] M2: Enable ORDS auto-REST for a table and inspect the generated schema.
- [ ] M3: Restrict privileges so one role cannot reach another's data.
- [ ] M4: Protect the service with OAuth2 client credentials.
- [ ] M5: Call an external payment gateway from APEX and handle both outcomes.
- [ ] M6: Build and parse JSON with `APEX_JSON`.
- [ ] M7: Produce a 500 deliberately and read the cause from `ords_log`.

## Anti-Goals
- Exposing tables with blanket access because auto-REST made it easy.
- Putting a version in the query string rather than the path.
- Treating a 200 response as proof the operation succeeded.
- Debugging by re-running in a browser instead of reading the server log.
- Rebuilding JSON by string concatenation.

## The one-sentence thesis
An API is a contract — version it, constrain it, authenticate it, and when it
fails, read the server log rather than guessing from the client.