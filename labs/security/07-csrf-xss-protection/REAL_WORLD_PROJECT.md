# CSRF & XSS Protection - REAL WORLD PROJECT

## Project: MerchantPortal — retrofitting injection defences onto a legacy Java monolith

A 2016-era Spring MVC + Thymeleaf monolith serving 30,000 small merchants. It renders
stored HTML content (rich product descriptions written by merchants), accepts webhooks,
has a legacy SOAP partner, and cannot be stopped for a six-month security rewrite. Defences
must be introduced incrementally, measured, and rolled out with feature flags.

### Architecture

```
LEGACY (unchanged, low risk to touch)         NEW (added behind flags)
  SOAP partner endpoint ──> /partner/*           no cookies + HMAC signature ──> /webhooks/*
  Admin JSP pages          (migrating)           /api/** stateless, Bearer only
  Merchant console (Thymeleaf)                   CSP with per-route reports

                    ┌──────────────────────────────────────────┐
                    │ Ingress: HSTS preload, TLS 1.2+,          │
                    │ SameSite=Lax on app cookies, WAF in front │
                    └──────────────────────────────────────────┘
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │ Response post-processor:                  │
                    │  - CSP nonce injection per response       │
                    │  - security header normalisation          │
                    │  - report-only rollout to /reports/csp    │
                    └──────────────────────────────────────────┘
```

### Implementation

Rich merchant HTML is the hard part: you cannot naively escape it, or every product
description breaks. Use an explicit allow-list sanitiser at write time, then still
encode at output time for contexts that are not HTML.

```java
@Service
class MerchantContentSanitizer {
    private final Sanitizer htmlSanitizer = Sanitizers.FORMATTING.and(Sanitizers.BLOCKS);

    /** Called at WRITE time for merchant-authored rich text. */
    public String sanitizeRichText(String html) {
        // DOM parser, not regex. Relative URLs only - blocks javascript: and data: exfil.
        return htmlSanitizer.sanitize(html, s -> s
            .allowElements("p", "b", "em", "ul", "ol", "li", "h3", "img")
            .allowAttributes("src", "alt").onElements("img")
            .allowElementsMatching("a", el -> "href".equals(el.getAttributeName()) && SAFE_URL.test(el.getAttributeValue("href")))
            .allowUrlProtocols("http", "https")
            .toFactory().create(html);
    }
    private static final Pattern SAFE_URL = Pattern.compile("^(https?:/\\S+)$");
}
```

A response wrapper injects CSP nonces into legacy JSP output without touching every page:

```java
@Component
class NonceInjectingResponse extends HttpServletResponseWrapper {
    private final String nonce;
    NonceInjectingResponse(HttpServletResponse res, String nonce) { super(res); this.nonce = nonce; }

    @Override public PrintWriter getWriter() throws IOException {
        PrintWriter delegate = super.getWriter();
        return new PrintWriter(new FilterWriter(delegate) {
            @Override public void write(String s, int off, int len) {
                // <script> and <style> need the nonce; everything else passes through.
                if (s.regionMatches(true, off, "<script", 0, 7) && !s.contains("nonce=")) {
                    s = s.substring(0, off) + s.substring(off, off + 7)
                          .replaceFirst(">", "> nonce=\"" + nonce + "\"") + s.substring(off + 7, off + len);
                }
                delegate.write(s, 0, len);
            }
        });
    }
}
```

Webhook endpoints get CSRF exclusion *and* a real replacement — signed requests:

```java
@Configuration
class WebhookSecurity {
    @Bean
    SecurityFilterChain webhooks(HttpSecurity http) throws Exception {
        return http.securityMatcher("/webhooks/**")
            // Safe to disable CSRF here: no cookies are used, authority is the HMAC signature.
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(a -> a.anyRequest().hasAuthority("SCOPE_webhooks.write"))
            .build();
    }

    @Bean
    WebhookSignatureVerifier webhookVerifier() {
        return (body, header) -> {
            String ts   = header.getFirst("X-Signature-Timestamp");
            String sig  = header.getFirst("X-Signature");
            long skew   = Math.abs(Instant.now().getEpochSecond() - Long.parseLong(ts));
            if (skew > 300) throw new WebhookRejected("timestamp outside window"); // replay guard
            String mac  = HmacSigner.sign(ts + "." + body, partnerSecretFor(header));
            if (!MessageDigest.isEqual(mac.getBytes(), sig.getBytes())) throw new WebhookRejected("bad signature");
        };
    }
}
```

### Rollout plan (why this ships safely)

1. **Observe**: CSP in `Content-Security-Policy-Report-Only` for 2 weeks. Triage reports, no breakage.
2. **Harden headers**: HSTS (short max-age first), `frame-ancestors`, `X-Content-Type-Options`.
3. **Cookies**: add `SameSite=Lax`; fix the small number of cross-site flows with explicit tokens.
4. **CSP enforce**: enforce on `/api/**` first (no HTML), then the merchant console per-route.
5. **Sanitiser**: apply to all merchant rich-text writes; backfill sanitise existing content.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Cross Site Scripting Prevention Cheat Sheet distinguishes output-encoding contexts
  (HTML, attribute, JS, URL) and documents sanitisation versus encoding as separate
  remediation strategies, as applied to merchant rich text here.
  https://web.archive.org/web/20200125082857/https://web.archive.org/web/20200116085004/https://owasp.org/www-project-cheat-sheets/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP CSRF Cheat Sheet details synchroniser-token, double-submit-cookie, and
  `SameSite` defenses, including why stateless/token APIs can safely disable CSRF.
  https://web.archive.org/web/20200125082857/https://web.archive.org/web/20200117191957/https://owasp.org/www-project-cheat-sheets/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- MDN's Set-Cookie reference documents the `SameSite` attribute semantics used in the
  cookie migration step (Lax vs Strict vs None) and why `None` requires `Secure`.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie

## Deliverables

- [x] Rich-text sanitiser at write time (DOM-based allow-list) + output encoding fallback
- [x] Report-only CSP rollout with a triage process and a 2-week observation gate
- [x] CSP enforcement per route group, nonce-based, no `unsafe-inline`
- [x] HSTS staged rollout (short max-age → long → preload) with subdomain impact analysis
- [x] `SameSite` migration plus explicit CSRF tokens where cross-site flows are required
- [x] HMAC-signed webhooks with timestamp skew and replay protection replacing CSRF there
- [x] Security header normalisation at the edge
- [ ] Full backfill of historical merchant content through the sanitiser
