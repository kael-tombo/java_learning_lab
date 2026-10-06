# Lab 04: APEX Security — Flashcards

## Four Layers

---
**Q**: Four APEX security layers?
**A**: Authentication · Authorisation · Session · Data scope.

---
**Q**: Which layer does APEX provide least of?
**A**: Authorisation and logging. Access control is essentially yours to build.

---
**Q**: What layer does row scoping belong to?
**A**: Data scope — and it is entirely your responsibility.

---
**Q**: Why doesn't authentication imply authorisation?
**A**: Every authenticated user may still be authorised for everything and see everything.

---

## Scheme Choice

---
**Q**: Five authentication schemes to compare?
**A**: APEX Internal · LDAP · SAML 2.0 · OIDC · Custom.

---
**Q**: Four decision criteria?
**A**: Does an IdP exist · compliance requirement · operational cost · token handling.

---
**Q**: Most important operational benefit of SSO?
**A**: Offboarding — revocation happens at the IdP. Eliminates stale leaver accounts.

---
**Q**: SSO support cost (local vs SSO)?
**A**: ~21.3 support hours/month → ~2.4/month. Plus ~16 stale accounts/year eliminated.

---

## OIDC

---
**Q**: Five IdP metadata endpoints used?
**A**: issuer · authorization_endpoint · token_endpoint · userinfo_endpoint · jwks_uri.

---
**Q**: `id_token` vs `access_token`?
**A**: `id_token` proves identity (claims). `access_token` authorises API calls.

---
**Q**: Why is `jwks_uri` critical?
**A**: It provides the signing keys for `id_token` validation. A wrong value means
trusting the wrong keys.

---
**Q**: Most common SSO misconfiguration?
**A**: Issuer or callback URL from the wrong tenant.

---

## Claim Mapping

---
**Q**: Unmapped subject behaviour?
**A**: Deny, log, direct to the application owner. **Fail closed.**

---
**Q**: Why no default user?
**A**: An IdP misconfiguration becomes a full-access account for a stranger.

---
**Q**: Key the directory on?
**A**: The `sub` claim — stable and unique per identity.

---
**Q**: Provision when?
**A**: Before first login, explicitly. Never as a side effect of authentication.

---

## Secrets

---
**Q**: Where does the client secret belong?
**A**: Authentication scheme configuration — not exported, not in process source.

---
**Q**: Exposure comparison, process vs scheme?
**A**: ~42 instances over 6 months (process) vs ~3 (scheme). ~14× reduction.

---
**Q**: What does a leaked IdP client secret permit?
**A**: Impersonating the application at the IdP and minting tokens.

---
**Q**: Outbound API credentials?
**A**: APEX Credentials (Web Credential), referenced by name.

---

## Logout

---
**Q**: Application logout vs RP-initiated logout?
**A**: App logout clears the APEX session; RP-initiated also ends the IdP session.

---
**Q**: Risk without RP-initiated logout?
**A**: 8-hour window where a walked-away-from machine re-authenticates silently.

---
**Q**: Reduction from 15-minute session?
**A**: 480/15 = **32× less unattended exposure**.

---

## Session State

---
**Q**: What must never be in session state?
**A**: Credentials, tokens, secrets. Also unnecessary or derivable PII.

---
**Q**: What should stay?
**A**: Identifiers needed across pages, role and context flags.

---
**Q**: Why minimise?
**A**: It appears in diagnostics and support bundles — less state, smaller blast radius.

---
**Q**: CSRF?
**A**: Leave it on. Fix the form, not the protection.

---

## OWASP

---
**Q**: How many OWASP items are APEX defaults?
**A**: 7 of 10.

---
**Q**: Which two are essentially yours?
**A**: Broken access control and logging.

---
**Q**: Evidence means what?
**A**: A recorded verification method per item — not an assertion.

---

## Availability

---
**Q**: Break-glass design?
**A**: Max 3 named accounts, rate-limited, every use alerted and reviewed.

---
**Q**: Why keep the internal scheme?
**A**: An IdP outage should not become an application outage. Controlled, audited fallback.

---
**Q**: Risk of keeping it too long?
**A**: It becomes the de facto default and the original problem returns. Alert on every use.

---

## Quick Reference

| Task | Object / Value |
|------|----------------|
| Scheme config | Shared Components → Authentication Schemes |
| Workspace roles | `APEX_SECURITY_ROLES` |
| Session read | `APEX_UTIL.SESSION_STATE` |
| Session write | `APEX_UTIL.SET_SESSION_STATE` |
| Authorize user | `APEX_UTIL.SECURITY.AUTHORIZE` |
| Client IP | `OWA_SECURITY.c_get_client_ip` |
| IdP token | `APEX_AUTHENTICATION.IDP_TOKENS` |
| Append-only pattern | `BEFORE UPDATE OR DELETE` trigger |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Support hours saved / year | ~232 |
| Stale leaver accounts eliminated | ~16/yr |
| Secret exposure reduction | 42 → 3 (~14×) |
| Unattended exposure reduction | 8 h → 15 min (32×) |
| PBKDF2 vs SHA-256 crack time (8 chars) | 89 years vs 78 hours |
| Unmapped subject rate | ~1% (24/day at 2,400 users) |
| OWASP items from APEX defaults | 7 of 10 |

**For a compliance conversation, the two numbers that matter are stale accounts
(0) and audit coverage (100%). The rest are efficiency.**

---

## Anti-Patterns

1. Authentication treated as the whole model.
2. Default user for an unmapped subject.
3. Create-on-first-login.
4. Secret in a page process.
5. Application-only logout.
6. CSRF disabled to fix a form.
7. PII bulk in session state.
8. OWASP compliance claimed without evidence.
9. Break-glass used routinely and unmonitored.

---

## Study Tips
1. Draw the four layers and place 10 controls from memory.
2. Explain `id_token` versus `access_token` in one sentence.
3. State the unmapped-subject behaviour and why fail-open is dangerous.
4. Recall the two numbers that matter for compliance, not the efficiency ones.