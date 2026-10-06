# Lab 04: REST Data Sources — Vision

## Where this lab takes you
From an APEX page that calls nothing to one that consumes external REST APIs
securely, handles file upload and download, exposes ORDS services, and processes
bulk CSV with resilience.

## The Arc
1. **Web Credentials** — storing secrets outside application code.
2. **Web Source Modules** — reusable, parameterised external calls.
3. **Synchronous vs asynchronous** — choosing a pattern per use case.
4. **Authentication** — OAuth2, API keys, mTLS, and which fits.
5. **File upload** — accepting a file into the database safely.
6. **File download** — serving a stored blob to the browser.
7. **ORDS** — exposing a schema as an API from APEX metadata.
8. **Bulk CSV** — resilience patterns for volume work in a request.

## Milestones (checkable)
- [ ] M1: Create a Web Credential and reference it from a Web Source Module.
- [ ] M2: Call an external API and handle both success and error responses.
- [ ] M3: Choose the auth pattern per endpoint and justify it.
- [ ] M4: Build a file upload that validates type, size, and content.
- [ ] M5: Build a file download that serves a stored blob correctly.
- [ ] M6: Expose a schema through ORDS with a restricted privilege set.
- [ ] M7: Process a bulk CSV with validation and partial-success reporting.
- [ ] M8: Explain why secrets must never appear in an APEX process body.

## Anti-Goals
- Putting an API key in a page process where any developer can read it.
- Accepting any uploaded file type and discovering problems later.
- Calling an external API once per row in a 10,000-row loop.
- Treating an HTTP 200 as success without checking the response body.
- Building an ORDS endpoint with blanket table access.

## The one-sentence thesis
An outbound integration is a security boundary and a capacity question — store the
secret properly, authenticate deliberately, and never turn one request into
10,000 HTTP calls.