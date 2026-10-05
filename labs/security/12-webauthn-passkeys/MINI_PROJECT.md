# WebAuthn & Passkeys - MINI PROJECT

## Project: PassKeyGate — passwordless login with passkeys, and a recovery path you can defend

Add a WebAuthn credential to a user account, then implement passwordless login using a
discoverable credential. Include the device-management screen and a recovery flow that
cannot be silently downgraded to a weaker factor.

### Architecture

```
REGISTER (once per device)
  Server: challenge = 32 random bytes, stored, 5 min TTL
  Client: navigator.credentials.create({publicKey: {challenge, rp: {id, name}, user,
            pubKeyCredParams: [{alg:-7},{alg:-257}]}})
  Server: verify response.clientDataJSON (type, origin, challenge)
          verify authData.rpIdHash == SHA256(rpId), flags UP/UV set as required
          store credentialId (base64url), publicKey (COSE), signCount

AUTHENTICATE (passwordless)
  Server: challenge = random, single use, DELETE after consumption
  Client: navigator.credentials.get({publicKey: {challenge, rpId, allowCredentials: []}})
  Server: lookup credential, verify signature over authData||SHA256(clientDataJSON),
          update signCount, issue session
```

### Implementation

```java
@Service
class WebAuthnRegistrationService {
    private final ChallengeStore challenges;   // single-use, 5-minute TTL

    PublicKeyCredentialCreationOptions start(String userHandle) {
        byte[] challenge = randomBytes(32);
        challenges.put(userHandle, challenge, Duration.ofMinutes(5));
        return PublicKeyCredentialCreationOptions.builder()
            .challenge(challenge)
            .rp(RpEntity.builder().id("login.gateway.local").name("Gateway").build())  // RP ID = registrable domain
            .user(UserEntity.builder()
                .name(userHandle).displayName(displayName(userHandle))
                .id(sha256(userHandle))          // opaque, stable, not a PII leak
                .build())
            .pubKeyCredParams(List.of(  // prefer ES256 (-7), accept RS256 (-257)
                PublicKeyCredentialParameters.PUBLIC_KEYCredentialType.ES256,
                PublicKeyCredentialParameters.PUBLIC_KEYCredentialType.RS256))
            .authenticatorSelection(AuthenticatorSelectionCriteria.builder()
                .residentKey(ResidentKeyRequirement.PREFERRED)   // discoverable for passwordless
                .userVerification(UserVerificationRequirement.PREFERRED)
                .build())
            .timeout(60_000)
            .excludeCredentials(existingCredentialsFor(userHandle))  // prevents re-registration
            .build();
    }

    @Transactional
    RegisteredCredential finish(String userHandle, PublicKeyCredentialResponse response) {
        byte[] expected = challenges.takeAndDelete(userHandle);    // single use
        if (expected == null) throw new WebAuthnException("challenge missing or already used");

        ClientData clientData = parseClientData(response.getClientDataJSON());
        // 1. The client echoes our challenge. Without this, a captured assertion is replayable.
        if (!Arrays.equals(expected, base64UrlDecode(clientData.challenge()))) throw forged();
        // 2. type must be webauthn.create
        if (!"webauthn.create".equals(clientData.type())) throw forged();
        // 3. origin must be ours, exactly.
        if (!ALLOWED_ORIGINS.contains(clientData.origin())) throw forged();

        AuthenticatorData authData = parseAuthData(response.getAuthenticatorData());
        // 4. rpIdHash proves the credential was created for our RP ID, not another site.
        if (!Arrays.equals(sha256("login.gateway.local"), authData.rpIdHash())) throw forged();
        if (!authData.userPresent()) throw new WebAuthnException("user presence required");
        // 5. Server-side verification of the attestation signature.
        AttestationVerifier.verify(response, clientData, authData);

        return credentialStore.save(new RegisteredCredential(
            userHandle, base64UrlEncode(response.getId()), cosePublicKey(authData),
            authData.signCount(), attestationFormat(response), Instant.now()));
    }
}
```

Authentication, including the sign-count policy that catches cloned authenticators:

```java
@Service
class WebAuthnAuthenticationService {
    @Transactional
    AuthenticationResult finish(String userHandle, PublicKeyCredentialAssertion a) {
        byte[] expected = challenges.takeAndDelete(userHandle);
        RegisteredCredential cred = credentialStore.require(userHandle, base64UrlEncode(a.getId()));

        ClientData clientData = parseClientData(a.getClientDataJSON());
        if (!MessageDigest.isEqual(expected, base64UrlDecode(clientData.challenge()))) throw forged();
        if (!"webauthn.get".equals(clientData.type())) throw forged();
        if (!ALLOWED_ORIGINS.contains(clientData.origin())) throw forged();

        AuthenticatorData authData = parseAuthData(a.getAuthenticatorData());
        if (!Arrays.equals(sha256("login.gateway.local"), authData.rpIdHash())) throw forged();
        if (!authData.userPresent()) throw new WebAuthnException("user presence required");

        // Signature covers authData || SHA-256(clientDataJSON) - both halves matter.
        byte[] signedBytes = concat(a.getAuthenticatorData(), sha256(a.getClientDataJSON()));
        if (!cose.verify(cred.cosePublicKey(), signedBytes, base64UrlDecode(a.getSignature())))
            throw new WebAuthnException("bad signature");

        // signCount behaviour is platform-dependent: 0 means the authenticator does not
        // support a counter. A counter that goes BACKWARDS is the clone signal.
        long previous = cred.signCount();
        long current  = authData.signCount();
        if (previous != 0 && current != 0 && current <= previous) {
            alert.possibleClonedAuthenticator(userHandle, cred.id());
            throw new WebAuthnException("sign counter did not advance");
        }
        credentialStore.updateSignCount(cred.id(), current);
        return AuthenticationResult.ok(userHandle);
    }
}
```

Recovery is the downgrade path an attacker wants. The design refuses to weaken silently:

```java
@Service
class RecoveryService {
    /**
     * Recovery deliberately still requires a passkey or an offline code.
     * There is no "email me a link" path once a passkey is enrolled, because that path
     * is exactly what an attacker with mailbox control will abuse to downgrade the account.
     */
    @Transactional
    void recover(String userHandle, RecoveryRequest req) {
        User u = users.require(userHandle);
        if (u.passkeyCount() == 0) { legacyPasswordRecovery(u, req); return; }  // pre-passkey users

        if (req.offlineRecoveryCode() != null) {
            if (!consumeRecoveryCode(u, req.offlineRecoveryCode())) throw new RecoveryRejected();
        } else {
            throw new RecoveryRejected("a registered passkey or offline recovery code is required");
        }
        // After recovery the OTHER credentials are revoked: if the account was compromised,
        // the attacker's passkey must not survive the legitimate user's recovery.
        credentialStore.revokeAllExcept(u, req.retainedCredentialId());
        audit.security("ACCOUNT_RECOVERED_PASSKEY", u.id(), req.method());
    }
}
```

### Test It

```java
@Test void challengeIsSingleUse() {
    options();                       // start -> server stores challenge
    assertDoesNotThrow(() -> finish(validResponse()));
    assertThrows(WebAuthnException.class, () -> finish(validResponse()));  // replay rejected
}

@Test void wrongOriginIsRejected() {
    assertThrows(WebAuthnException.class, () -> finish(responseWithOrigin("https://evil.local")));
}

@Test void wrongRpIdIsRejected() {
    assertThrows(WebAuthnException.class, () -> finish(responseWithRpId("other.gateway.local")));
}

@Test void clonedAuthenticatorIsDetected() {
    credentialStore.save(cred(userHandle, signCount: 10));
    assertThrows(WebAuthnException.class, () -> finish(assertionWithSignCount(5)));
}

@Test void recoveryCannotDowngradeToEmail() {
    credentials.save(cred("alice", 1));
    assertThrows(RecoveryRejected.class, () -> recovery.recover("alice", emailLinkRequest()));
}
```

## Deliverables

- [ ] Registration and authentication ceremonies with single-use challenges
- [ ] Verification of `clientDataJSON` type, origin, and challenge on every response
- [ ] `rpIdHash` verification and an explicit RP ID configuration
- [ ] Credential store holding credential id, COSE public key, sign count, attestation format
- [ ] Sign-count regression detection with a security alert
- [ ] Discoverable-credential support for passwordless login (no username needed)
- [ ] Recovery flow that revokes other credentials and refuses email downgrade
- [ ] Tests: replay, wrong origin, wrong RP ID, clone detection, recovery refusal
