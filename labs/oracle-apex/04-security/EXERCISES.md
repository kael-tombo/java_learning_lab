# Lab 04: APEX Security — Exercises

## Exercise 1: The Four Security Layers
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Place controls in the correct security layer.

### Steps
1. Draw authentication, authorisation, session, and data scope.
2. Place 10 APEX features across the layers.
3. Identify which layers APEX provides and which you build.
4. Explain what authenticating everyone identically achieves.

### Verification
- [ ] All 10 controls correctly placed
- [ ] APEX defaults separated from your responsibilities
- [ ] Explanation that authentication alone is not access control

---

## Exercise 2: Scheme Comparison
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Decide the authentication scheme on stated criteria.

### Steps
1. Compare internal, LDAP, SAML, and OIDC on SSO support, compliance fit,
   operational cost, and token handling.
2. State which applies to an organisation with an existing IdP.
3. State what changes if there is no IdP.
4. Justify the OIDC choice for a regulated client.

### Verification
- [ ] Four criteria used consistently
- [ ] Recommendation justified by organisational facts, not preference
- [ ] Compliance driver named explicitly

---

## Exercise 3: Configure the OIDC Scheme
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Build the scheme from IdP metadata.

### Steps
1. Register the application with exact callback URLs.
2. Copy issuer, authorization, token, userinfo, and JWKS endpoints.
3. Configure the client ID and secret in the scheme.
4. Map `sub`, `email`, and `name` claims.
5. Complete a login.

### Verification
- [ ] All endpoints from metadata, no transcription errors
- [ ] Issuer matches the registering tenant
- [ ] Secret stored in scheme configuration only
- [ ] Login succeeds and the mapped user is correct

---

## Exercise 4: Fail Closed on Unknown Subject
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Deny an unmapped identity and log it.

### Steps
1. Attempt login with a valid IdP account not in the directory.
2. Confirm access is denied.
3. Confirm a log entry exists with the outcome.
4. Inspect the code to confirm there is no default-user path.

### Verification
- [ ] Denied, not defaulted
- [ ] Log entry written with outcome DENIED
- [ ] No fallback to a privileged account anywhere in the path

---

## Exercise 5: Secret Exposure Audit
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Confirm no secret is in application source.

### Steps
1. Export the application to YAML.
2. Search the export for the client secret and any other credential.
3. Confirm the secret appears only in scheme configuration.
4. Compare exposure counts between process source and scheme config.

### Verification
- [ ] No secret in the export
- [ ] Exposure count comparison recorded
- [ ] Blast radius of a leaked secret described by what it permits

---

## Exercise 6: RP-Initiated Logout
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Confirm the session ends at the IdP, not just in APEX.

### Steps
1. Log in and log out using application logout only.
2. Re-visit the app; note whether authentication is required.
3. Configure RP-initiated logout.
4. Repeat; confirm authentication is required.

### Verification
- [ ] Behaviour difference captured before and after
- [ ] Post-logout redirect validated at the IdP
- [ ] Exposure window before and after quantified

---

## Exercise 7: Session State Audit
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Minimise session state and remove anything sensitive.

### Steps
1. List every session state key in use.
2. Classify each: required, derivable, or sensitive.
3. Remove credentials, tokens, and unnecessary PII.
4. Confirm CSRF protection still functions after removal.

### Verification
- [ ] Full key inventory produced
- [ ] Sensitive keys removed
- [ ] Nothing removed that is genuinely needed
- [ ] CSRF verified after cleanup

---

## Exercise 8: Break-Glass and IdP Outage
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Confirm availability during an IdP incident without losing control.

### Steps
1. Configure limited break-glass accounts.
2. Break the IdP endpoint.
3. Confirm fallback login works and generates an alert.
4. Confirm lockout after repeated failures.
5. Restore the IdP and confirm SSO resumes.

### Verification
- [ ] Fallback works during the simulated outage
- [ ] Usage generates an alert within the stated window
- [ ] Lockout triggers and is rate-limited
- [ ] SSO resumes without re-provisioning

---

## Exercise 9: OWASP Evidence Pack
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Produce verifiable evidence for all ten items.

### Steps
1. Walk the OWASP Top 10.
2. For each, record whether it is an APEX default or your work.
3. Record how each is verified.
4. Test the two you expect to be weakest.

### Verification
- [ ] All 10 items have an evidence entry
- [ ] Defaults separated from your responsibilities
- [ ] Weakest items tested rather than asserted

---

## Exercise 10: Authorisation After SSO
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Confirm authentication did not bypass authorisation.

### Steps
1. Authenticate as a VIEWER role.
2. Attempt to reach an ANALYST-only feature.
3. Confirm the server-side condition blocks it.
4. Attempt to read another department's rows.

### Verification
- [ ] Feature blocked at the server, not by hiding a button
- [ ] Row scoping prevents cross-department reads
- [ ] Both tests use an authenticated but low-privilege user