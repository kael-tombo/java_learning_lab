# Lab 04: APEX Security — Theory

## The Scenario

A client wants their APEX application to authenticate against the corporate
identity provider instead of maintaining a second set of passwords. The identity
team already runs an OIDC provider for other applications. Today's APEX app uses
internal accounts with the default password policy, and an audit has flagged that
session state contains an email address and a role name in clear text.

## Principle 1: Security is four independent layers

```
1. AUTHENTICATION   who is this person?
2. AUTHORISATION    what may they do?
3. SESSION          what is remembered between requests?
4. DATA SCOPE       what may they see?
```

**Authentication alone is not security.** An application that authenticates
everyone identically and authorises everything is more secure than nothing, but
it is not an access-controlled application.

The failure pattern in real audits:

```
Layer 1:  SSO implemented properly        ✓
Layer 2:  every authenticated user is admin  ✗
Layer 3:  session holds a credential       ✗
Layer 4:  no row scoping                   ✗
```

Each layer must be built. A control in layer 1 does not compensate for a gap in
layer 4.

## Principle 2: Choosing an authentication scheme

| Scheme | Protocol | Good fit | Cost |
|--------|----------|----------|------|
| APEX Internal | username/password | Local, no IdP | Password lifecycle yours |
| LDAP | Direct bind | Directory exists, no federation | Simple but no SSO |
| SAML 2.0 | Assertion | Enterprise IdP, mature | Assertion handling |
| **OIDC** | OAuth2 + ID token | Modern IdP, API-friendly | Client registration |
| Custom | Your PL/SQL | Legacy auth to wrap | You own the security |

### The four criteria that decide it

1. **Does an IdP exist?** If not, SSO is a larger project than the application.
2. **Compliance requirement.** SOX, PCI, and most financial-services policies
   forbid local credentials for privileged users.
3. **Operational cost.** Who resets passwords? Who handles MFA? Who offboards?
   With SSO these become the IdP's problem, which is the point.
4. **Token handling.** OIDC uses short-lived tokens; SAML assertions are longer
   lived and larger. Neither is automatically better.

**The decision is rarely technical.** It is driven by whether the organisation
has an IdP and a policy requiring SSO. Once SSO is mandated, OIDC is usually the
simplest integration because it returns a standard claims document.

## Principle 3: What OIDC actually proves

The authorization code flow:

```
1. User visits APEX → not authenticated → redirected to IdP
2. User authenticates at the IdP (password, MFA, whatever)
3. IdP redirects back with ?code=...
4. APEX exchanges the code for tokens at the IdP token endpoint:
     - access_token  (authorises API calls)
     - id_token      (proves identity, contains claims)
5. APEX validates the id_token signature against the IdP's JWKS
6. APEX reads claims (sub, email, name) and maps them to a local user
```

**Critical distinction**: an `access_token` authorises access. An `id_token`
proves identity. Only the `id_token` should be used to decide who the user is.

**Validation is not optional.** An unvalidated `id_token` is a self-signed
assertion the attacker wrote themselves. APEX performs this validation, but the
configuration must point at the correct issuer and JWKS endpoint — a wrong issuer
means you are trusting the wrong signing keys.

## Principle 4: Claim mapping must fail closed

The most dangerous line in any SSO integration:

```sql
-- DANGEROUS: fall back to "some user" if the subject is not recognised
SELECT user_id FROM app_user_directory WHERE identity_subject = :l_sub;
-- if not found → default to an admin
```

That default turns an IdP misconfiguration into a full-access account for
anyone who can create an account at the IdP. The correct behaviour:

```
Subject not found in the local directory
  → deny access
  → log the attempt
  → tell the user to contact the application owner
```

**Provisioning is an explicit act**, not a side effect of authentication. A new
employee is added to the application's directory as part of onboarding, before
their first login.

## Principle 5: The client secret must not be in application source

An APEX authentication scheme holds a client secret in configuration. That is
acceptable. A client secret pasted into a **page process** is not:

```
Page process containing a secret:
  → readable by any APEX developer with access to the application
  → appears in the application YAML export
  → captured in application exports and support bundles
  → potentially in database audit logs of process source
```

**Scheme configuration is the right place.** For outbound calls where a
process must reference a credential, use APEX Credentials (Web Credential), not
a literal.

For OIDC specifically the secret belongs in the authentication scheme, which APEX
stores securely and which is not part of an application export.

## Principle 6: Logout must end the session at the IdP

Two logouts, often confused:

```
Application logout:   clears the APEX session. The user can immediately
                      re-authenticate because the IdP session is still live.

RP-initiated logout:  tells the IdP to end its session too.
                      Next visit requires authentication again.
```

**Without RP-initiated logout**, the SSO "single sign-on" property is a security
weakness: a user who walks away from an unlocked machine can be re-authenticated
instantly without re-entering credentials. On a shared terminal that is a real
problem.

## Principle 7: Session state should be minimal

APEX session state is stored server-side, keyed by a session cookie. It is not
readable from the browser, but it is still worth minimising:

```
Do NOT put in session state:
  - credentials or tokens
  - unnecessary PII (a full email or employee record)
  - data that can be re-derived from the database

Do put in session state:
  - identifiers needed across pages
  - role and context flags
  - state that cannot be re-derived cheaply
```

**Why it matters**: session state is included in diagnostics, support bundles,
and sometimes in logs. Minimising it reduces the blast radius of any of those
leaking.

## Principle 8: CSRF protection is inherited, not earned

APEX generates a per-session token and includes it in forms. Requests without a
valid token are rejected. This protects against cross-site request forgery.

**Never disable it to make a page work.** If a legitimate request is being
rejected, the cause is nearly always one of:

- A form submitted programmatically without the token.
- A region using a raw HTML form instead of an APEX one.
- A page rendered from a cached fragment that captured an old token.

The fix is to include the token, not to remove the protection.

## Principle 9: OWASP items need evidence, not assurance

| Item | APEX default | What you must verify |
|------|--------------|----------------------|
| Injection | Parameterised regions | No string-concatenated SQL in processes |
| Broken authentication | Depends on scheme | Scheme configured correctly; no shared accounts |
| Sensitive data exposure | Session state server-side | Nothing sensitive in session state |
| XSS | Escaped output | No raw HTML from user input |
| Broken access control | **Application-dependent** | Authorisation scheme + row scoping present |
| Security misconfiguration | Default password policy | Policy changed; HTTPS enforced |
| CSRF | Token per session | Enabled on every page |
| Component vulnerabilities | APEX version | Patched |
| Logging | Minimal by default | Authentication events audited |
| SSRF | Depends on outbound calls | Outbound calls restricted |

**Five of these are APEX defaults and five depend on what you build.** "APEX is
secure" conflates the two lists.

## Principle 10: SSO is a migration, not a switch

Rollout that works:

```
1. Register the APEX app with the IdP (test tenant)
2. Configure the scheme and test in non-production
3. Map claims; verify EVERY user type, including admins
4. Handle the unmapped-subject case and test it
5. Configure RP-initiated logout and test it
6. Run both schemes in parallel during a pilot
7. Cut over; keep the internal scheme available as break-glass
```

**Keep the previous scheme.** IdP outages happen. Without a fallback, an IdP
incident becomes an application outage. With one — controlled, audited, and
monitored — it does not.

## Diagnostic Order

1. Which layer is the gap in — authentication, authorisation, session, or data?
2. What protocol does the IdP actually support?
3. Is the issuer and JWKS configured from the correct IdP metadata?
4. What happens on an unmapped subject? (Must be denial.)
5. Is any secret in a page process rather than in scheme configuration?
6. Does logout end the IdP session?
7. What is in session state that should not be?
8. Which OWASP items are defaults and which are yours?

## Anti-Patterns

- Treating authentication as the whole security model.
- Defaulting an unmapped subject to a privileged account.
- Validating an `id_token` against the wrong issuer or skipping validation.
- Pasting a client secret into a page process.
- Application logout only, with no RP-initiated logout.
- Disabling CSRF to make a form work.
- Bulk PII in session state.
- Claiming OWASP compliance without evidence per item.

## Summary

SSO replaced local passwords, but the value came from the layers around it:
failing closed on an unmapped subject so an IdP misconfiguration cannot become an
admin account, keeping the secret in scheme configuration where it is not
exported, RP-initiated logout so walking away from the machine does not leave an
instantly reusable session, minimal session state to limit diagnostic exposure,
and CSRF left enabled. The internal scheme stayed as an audited break-glass path,
because an IdP outage should not become an application outage.