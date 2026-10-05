# SAML 2.0 Federated Identity - REAL WORLD PROJECT

## Project: GovConnect — SAML federation for a public-sector benefits portal

Government and large-enterprise customers federate via SAML 2.0 while staff and partner
users use OIDC. The SP must onboard new agency IdPs without a code change, survive
certificate rotation, and be auditable enough for a government security assessment.

### Architecture

```
 Agency IdP A (SAML)  ─┐
 Agency IdP B (SAML)  ─┼── metadata ──▶ GovConnect SP (Spring Boot, HA)
 Ministry IdP (SAML)  ─┤                      │
 OIDC (staff/partner)  ─┘                      ▼
                                          Service Provider
                                          metadata published at
                                    /saml2/service-provider-metadata
                                              │
                                        Agency portals (initiate SSO or receive
                                        IdP-initiated assertions)
```

### Implementation

Multi-IdP registration is the core of the service: agencies are onboarded by configuration,
never by a pull request that touches authorization code.

```java
@Service
class AgencyOnboardingService {
    private final RelyingPartyRegistrationRepository repo;
    private final MetadataCache metadata;
    private final AuditLog audit;

    /** Onboard a new agency IdP. Registration id is derived from the agency, not user input. */
    @Transactional
    public RelyingPartyRegistration onboard(AgencyRequest req) {
        String registrationId = "agency-" + req.slug();          // allow-listed charset only
        if (repo.findByRegistrationId(registrationId).isPresent())
            throw new DuplicateAgencyException(registrationId);

        Saml2Metadata md = metadata.fetchAndPin(registrationId, req.metadataUrl(), req.pinnedSha256());
        audit.record("AGENCY_ONBOARDED", registrationId, md.getEntityId(), actor());
        return repo.save(RelyingPartyRegistration.withRegistrationId(registrationId)
            .assertingPartyMetadata(md)
            .entityId(props.spEntityId(registrationId))
            .assertionConsumerServiceLocation(props.acsUrl(registrationId))
            .signatureCredentials(spCredentialStore.forSp(registrationId))
            .requireLogoutResponseSigned(true)   // LogoutResponse must be signed by the IdP
            .build());
    }
}
```

IdP-initiated SSO is the government default, and it is where identity-context assumptions
break. Mapping must be explicit and must never infer tenant from an unverified attribute:

```java
@Component
class IdpInitiatedHandler {
    @Transactional
    void handleUnsolicited(Saml2AuthenticationToken token, HttpServletRequest req) {
        Saml2AuthenticatedPrincipal p = (Saml2AuthenticatedPrincipal) token.getPrincipal();

        // Never trust the ACS path or a query parameter to identify the agency: the
        // Assertion's Audience must match a registration WE configured.
        RelyingPartyRegistration reg = resolveByAudience(p.getFirstAttribute(AUDIENCE));
        if (reg == null) { audit.security("UNKNOWN_AUDIENCE", p.getName()); throw new BadCredentialsException("no such IdP"); }

        // Federation is an explicit mapping, not a copy of whatever the IdP asserts.
        String tenant = tenantDirectory.resolveAgency(p.getFirstAttribute("agencyCode"));
        if (tenant == null) { audit.security("UNMAPPED_AGENCY", p.getName()); throw new BadCredentialsException("unmapped agency"); }

        String nameId = p.getName();
        SamlPrincipal principal = attributeMapper.map(p, tenant, reg);
        // Replay: a uniqueId / session index prevents a captured assertion being replayed.
        if (usedAssertions.putIfAbsent(nameId, p.getSessionIndexes().stream().findFirst().orElse(nameId)) != null) {
            audit.security("ASSERTION_REPLAY", nameId);
            throw new BadCredentialsException("assertion already consumed");
        }
        SecurityContextHolder.getContext().setAuthentication(createAuthentication(principal));
    }
}
```

Certificate rotation with no downtime, coordinated with each agency:

```java
@Component
class AgencyRotationCoordinator {
    /**
     * Sequence that avoids an outage:
     *  1. SP publishes BOTH old and new signing certs in metadata.
     *  2. Agency is notified and uploads our metadata (new cert added, old retained).
     *  3. Agencies confirm readiness; we start SIGNING with the new key.
     *  4. Wait = max AssertionNotOnOrAfter window (commonly 5-10 min).
     *  5. Only now remove the old cert from our metadata.
     */
    void executeRotation(String agency, KeyPair newKey) {
        spCredentialStore.publishDual(agency, newKey);                     // 1
        notifyAgency(agency, "metadata-update-required", dualCertPem(agency)); // 2
        awaitAgencyAck(agency, Duration.ofHours(72));                     // 3 - human/scheduled
        spCredentialStore.signWithNew(agency, newKey);                     // 3
        sleep(spProps.maxAssertionWindow());                              // 4
        spCredentialStore.retainOldOnly(agency, oldCert(agency));          // 5
        audit.record("AGENCY_CERT_ROTATED", agency, actor());
    }

    /** Emergency path: a compromised key must be revoked immediately, accepting some breakage. */
    void emergencyRevoke(String agency) {
        spCredentialStore.revokeSigning(agency);
        allSessionsForAgency(agency).forEach(SessionRegistry::expireNow);
        audit.security("AGENCY_CERT_COMPROMISED", agency, actor());
    }
}
```

### Non-functional requirements

- **Availability**: SP is HA; a session established on one node works on all (Spring
  Session in Redis). SSO availability target 99.9% during business hours.
- **Latency**: SP-initiated SSO round trip under 1.5 s excluding the IdP login step.
- **Onboarding SLA**: new agency federated in under 5 business days, config-only.
- **Rotation**: scheduled yearly; 72-hour ack window; emergency revoke path tested
  quarterly in a tabletop exercise.
- **Security controls**: signed requests and responses, `wantAssertionsSigned`,
  `wantAuthnRequestsSigned`, replay protection, strict clock skew, no IdP-initiated
  dynamic registration.
- **Audit**: every SSO, SLO, replay rejection, unknown audience, and admin change written
  to an immutable sink with agency, principal, and correlation id.
- **Assessment**: evidence export mapping controls to the applicable government framework.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OASIS SAML 2.0 core specification defines the assertion, `Conditions` (Audience,
  NotBefore/NotOnOrAfter), and the profile requirements for signature validation.
  https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf
- OWASP XML Security Cheat Sheet covers signature wrapping, XXE prevention, and the
  canonicalisation requirements that the validator above relies on.
  https://cheatsheetseries.owasp.org/cheatsheets/XML_Security_Cheat_Sheet.html

## Deliverables

- [x] Config-driven multi-IdP onboarding with thumbprint pinning at registration time
- [x] Explicit federation mapping (agency → tenant) with fail-closed unknown-agency path
- [x] IdP-initiated SSO with audience-based IdP resolution and assertion replay protection
- [x] Five-step certificate rotation sequence with an agency acknowledgement gate
- [x] Emergency key-compromise path: revoke, expire sessions, audit
- [x] SLO with signed `LogoutResponse` validation
- [x] Session sharing across HA nodes via Spring Session
- [x] Immutable audit of every SSO/SLO/rejection/admin action
