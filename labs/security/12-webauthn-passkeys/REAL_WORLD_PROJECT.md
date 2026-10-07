# WebAuthn & Passkeys - REAL WORLD PROJECT

## Project: TrustSign — passkey-first authentication for a consumer payments platform

A consumer banking-style app with ~2M users. Passwords are a liability and SMS OTP is
both expensive and phishable. The goal: passkeys as the default sign-in method, with a
migration path, a device-management experience, and a recovery process that does not
create a new attack surface.

### Architecture

```
                        ┌────────────────────────────────┐
 App / Web  ───────────▶│ Passkey Service                 │
                        │  registration + assertion       │
                        │  passkey-first login            │
                        └───────┬────────────────────────┘
                                │ credential records
                                ▼
                     ┌──────────────────────┐
                     │ Postgres             │
                     │ user_passkeys        │
                     │ (cred id, COSE pk,   │
                     │  sign_count, backed- │
                     │  up flag, device     │
                     │  label, created_at)  │
                     └──────────────────────┘

  Recovery: offline codes (8, single use) ──▶ revoke all other credentials
  Fraud:    step-up passkey for payments over a threshold
  Risk:     new-device enrolment triggers a notification + a cooldown
```

### Implementation

The user experience drives the security model: users must be able to add a passkey without
a labyrinthine flow, because a hard enrolment process means most users stay on SMS.

```java
@Service
class PasskeyService {

    @Transactional
    public PublicKeyCredentialCreationOptions beginRegistration(String userId, DeviceInfo device) {
        User u = users.require(userId);
        // Rate limit enrolment: an attacker with a hijacked session must not silently
        // register their own authenticator before acting.
        enrolmentLimiter.check(u.id(), 3, Duration.ofHours(24));
        if (u.passkeyCount() >= MAX_PASSKEYS_PER_USER) throw new LimitExceeded("device limit");
        challengeStore.put(userId, randomBytes(32), Duration.ofMinutes(5));
        return PublicKeyCredentialCreationOptions.builder()
            .challenge(challengeStore.peek(userId))
            .rp(RpEntity.builder().id("trustsign.example").name("TrustSign").build())
            .user(UserEntity.builder().id(userId).name(u.maskedEmail()).displayName(u.displayName()).build())
            .pubKeyCredParams(List.of(PUBLIC_KEYCredentialType.ES256))
            .authenticatorSelection(AuthenticatorSelectionCriteria.builder()
                .residentKey(ResidentKeyRequirement.REQUIRED)   // passkey: discoverable
                .userVerification(UserVerificationRequirement.REQUIRED)   // biometric/PIN, not just touch
                .build())
            .excludeCredentials(allCredentialsFor(userId))
            .build();
    }

    @Transactional
    public void completeRegistration(String userId, RegistrationResponse r, DeviceInfo d) {
        byte[] expected = challengeStore.takeAndDelete(userId);       // single use
        verifyClientData(expected, r, "webauthn.create");
        AuthenticatorData a = AuthenticatorData.parse(r.authenticatorData());
        verifyRpId(a, "trustsign.example");
        // REQUIRED in options, so this must be true. A passkey without UV is not a passkey.
        if (!a.userVerified()) throw new PasskeyRejected("user verification is required");
        if (a.credentialDeviceType() == "singleDevice" && a.backedUp())
            throw new PasskeyRejected("backup state inconsistent with device type");

        credentialStore.insert(new Passkey(userId, r.credentialId(), coseKey(a), a.signCount(),
                a.backedUp(), deviceLabel(d), d.platform(), Instant.now(), PasskeyState.ACTIVE));
        // Notification is a real control: silent enrolment is a takeover signal.
        notify.newPasskeyEnrolled(userId, d, notifyChannelFor(userId));
    }
}
```

Passwordless discovery flow and step-up for high-value actions:

```java
@Service
class PasskeyLoginService {
    /** Passwordless: no username typed. The authenticator offers its resident credentials. */
    PublicKeyCredentialRequestOptions beginPasswordless(String sessionId) {
        byte[] ch = randomBytes(32);
        challengeStore.put(sessionId, ch, Duration.ofMinutes(5));
        return PublicKeyCredentialRequestOptions.builder()
            .challenge(ch)
            .rpId("trustsign.example")
            .allowCredentials(List.of())   // empty => discoverable credential flow
            .userVerification(UserVerificationRequirement.REQUIRED)
            .timeout(120_000)
            .build();
    }

    /** Step-up for a high-value action: constrain to credentials registered on a known device. */
    @Transactional
    void stepUpForTransfer(String userId, Transfer t, Assertion a) {
        if (t.amount().compareTo(STEP_UP_THRESHOLD) < 0) return;
        byte[] expected = challengeStore.takeAndDelete(userId);
        Passkey p = credentialStore.require(userId, a.credentialId());
        if (p.backedUp() && t.amount().compareTo(HIGH_VALUE_FOR_SYNCED_PASSKEY) > 0)
            throw new StepUpRejected("sync passkeys not sufficient for this amount");
        verifyAssertion(expected, a, "webauthn.get");
        riskEngine.evaluate(userId, p.deviceId(), t);   // a passkey step-up does not skip risk checks
    }
}
```

Recovery, designed so an attacker with mailbox access cannot downgrade the account:

```java
@Component
class RecoveryWorkflow {
    /**
     * Rules, in order of strength:
     *  1. At least one active passkey exists  -> email-only recovery is REFUSED, permanently.
     *  2. Recovery requires an offline recovery code (issued at passkey enrolment, 8 single-use codes).
     *  3. On success, every other credential is revoked and all sessions are killed.
     *  4. New sign-ins are rate-limited and every new credential triggers a notification.
     * There is no support-ticket override; that is a social-engineering vector.
     */
    @Transactional
    void recover(String userId, RecoveryCodeRequest req) {
        User u = users.require(userId);
        if (passkeys.activeCount(userId) > 0 && !recoveryCodes.consume(u, req.code()))
            throw new RecoveryRejected("valid recovery code required");

        passkeys.revokeAllExcept(userId, req.keepCredentialId());
        sessions.killAll(userId);
        recoveryCodes.rotate(u);                        // codes are now spent; issue new ones after re-enrolment
        notify.accountRecovered(userId, req.ip(), req.userAgent());
        audit.security("ACCOUNT_RECOVERED", userId, "recovery_code", req.ip());
    }
}
```

### Non-functional requirements

- **Adoption**: 60% of monthly active users on passkeys within 6 months of rollout.
  Instrumentation: enrolment funnel conversion, per-platform failure rates.
- **Latency**: authentication p95 under 400 ms (mostly the authenticator's user verification).
- **Fallback cost**: SMS retained only for accounts with zero passkeys; cost per month is
  a tracked KPI, not an afterthought.
- **Attestation policy**: `none` attestation accepted for consumer self-service (privacy
  preserving); vendor attestation (`apple`, `google`, `fido-u2f`) recorded for fraud scoring.
- **Fraud linkage**: a newly enrolled credential marks the account as "device changed";
  large transfers get a cooldown and an extra notification.
- **Availability**: passkey dependency is isolated so its outage does not block sign-in
  entirely for accounts that still have a valid session or a recovery code.
- **Compliance**: credential records are authentication data — retention, encryption, and
  access are scoped separately from transaction data, with the same audit discipline as
  security events in labs 19/20.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- W3C Web Authentication: Level 3 specification defines the registration and authentication
  ceremonies, `clientDataJSON` origin/challenge binding, and RP ID semantics implemented here.
  https://www.w3.org/TR/webauthn-3/
- OWASP Authentication Cheat Sheet and Passkey/FIDO guidance recommend phishing-resistant
  factors over OTP and warn against fallback paths that weaken an enrolled account.
  https://web.archive.org/web/20200125082857/https://web.archive.org/web/20200206085739/https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html

## Deliverables

- [x] Passkey-first registration with required user verification and discoverable credentials
- [x] Passwordless login using the resident-credential flow
- [x] Step-up passkey for high-value transfers, with synced-passkey value limits
- [x] Offline single-use recovery codes; email-only recovery permanently refused
- [x] Credential revocation on recovery, session kill, and new-credential notification
- [x] Enrolment rate limiting and device-change risk signals wired to fraud scoring
- [x] Attestation policy recorded but not used to block consumer enrolment
- [ ] 6-month adoption programme: per-platform enrolment funnel and failure dashboards
