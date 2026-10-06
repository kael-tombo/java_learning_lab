# Lab 04: APEX Security — Quiz

**1.** What are APEX's four security layers?

A. Login, password, session, timeout
B. Authentication, authorisation, session, data scope
C. Oracle, APEX, schema, page
D. SSO, LDAP, SAML, OIDC

<details><summary>Answer</summary><b>B</b> — Authentication decides who you are; authorisation what you may do; session what is remembered; data scope what you may see.</details>

---

**2.** Why does authentication alone not make an application secure?

A. It is expensive
B. Every authenticated user may still be authorised for everything and see everything
C. It can be bypassed
D. It is not an APEX concept

<details><summary>Answer</summary><b>B</b> — A fully SSO application with no authorisation scheme and no row scoping is barely more controlled than an open app.</details>

---

**3.** What does an `id_token` prove that an `access_token` does not?

A. Nothing
B. Identity — the `access_token` authorises API calls, the `id_token` proves who the user is
C. Authorisation
D. Currency

<details><summary>Answer</summary><b>B</b> — Using the wrong token for identity decisions is a design error.</details>

---

**4.** What happens on an unmapped IdP subject?

A. Create an account automatically
B. Assign a default role
C. Deny access, log the attempt, and direct the user to the application owner
D. Fall back to local authentication

<details><summary>Answer</summary><b>C</b> — Fail closed. A default role turns an IdP misconfiguration into an access-control failure.</details>

---

**5.** Why is create-on-first-login a problem?

A. It is slow
B. It makes provisioning a side effect of authentication, so anyone who can
   create an IdP account gets access
C. It duplicates usernames
D. APEX does not support it

<details><summary>Answer</summary><b>B</b> — Provisioning must be an explicit onboarding act.</details>

---

**6.** Where does the OIDC client secret belong?

A. A page process
B. Authentication scheme configuration
C. A comment in the application export
D. A LOV

<details><summary>Answer</summary><b>B</b> — Scheme config is not exported and not readable by application developers. A process secret is.</details>

---

**7.** What is wrong with an application-only logout?

A. It does not clear cookies
B. The IdP session survives, so the next visit re-authenticates silently with no
   credential — SSO becomes an unattended-access weakness
C. It is slower
D. It logs the user out everywhere

<details><summary>Answer</summary><b>B</b> — 8 hours of instant reusable access on a shared machine. RP-initiated logout fixes it.</details>

---

**8.** Why minimise session state?

A. It uses less memory
B. It appears in diagnostics and support bundles, so anything unnecessary enlarges
   the blast radius of a leak
C. APEX limits its size
D. It is faster

<details><summary>Answer</summary><b>B</b> — No credentials, tokens, or derivable PII. Keep identifiers and context flags.</details>

---

**9:** Why not disable CSRF protection when a form fails?

A. It is slower
B. The cause is nearly always a form submitted without the token — fix the form,
   not the protection
C. APEX requires it
D. It is a performance cost

<details><summary>Answer</summary><b>B</b> — One of APEX's highest-value defaults, protecting ~96,000 requests a day at no cost.</details>

---

**10.** In the OWASP list, which items are entirely your responsibility?

A. Injection and XSS
B. Broken access control and logging — both are APEX defaults you must build on
C. CSRF and known vulnerabilities
D. Sensitive data exposure

<details><summary>Answer</summary><b>B</b> — APEX provides 7 of 10 defaults; access control and logging are essentially empty without your work.</details>

---

## Scoring
- **9–10**: Ready to deliver APEX SSO securely.
- **7–8**: Solid; revisit claim mapping and logout.
- **5–6**: Re-read THEORY on the four layers and OIDC flow.
- **<5**: Work through EXERCISES 3, 4, and 6 again.