# VISION — WebAuthn & Passkeys: Phishing-Proof Credentials
> Where this lab takes you: from "add a second factor" to implementing the ceremony correctly and handling the recovery paths that attackers exploit.

## The Arc
1. **Why** — the phishing problem with OTP, and the origin-binding that WebAuthn adds.
2. **Registration ceremony** — challenge, attestation, credential creation, storing the public key.
3. **Authentication ceremony** — assertion, signature verification, sign counter / UV flags.
4. **Passkeys** — discoverable credentials, synced vs device-bound, user verification.
5. **Operations** — recovery without becoming a downgrade, attestation policy, device lifecycle.

## Milestones (checkable)
- [ ] M1: draw both ceremonies and identify every value the server must generate and store.
- [ ] M2: implement registration and store the credential public key correctly.
- [ ] M3: implement authentication and verify the assertion signature and challenge freshness.
- [ ] M4: bind a credential to an RP ID and explain what a subdomain attack would achieve.
- [ ] M5: design a recovery flow that cannot be downgraded to a weaker factor.

## Core Competencies
- Attestation vs assertion, and the difference between attestation formats and what you store.
- `clientDataJSON` origin, `rpIdHash`, and challenge verification — the binding that makes
  the credential phishing-resistant.
- Discoverable (resident) credentials for passwordless flows and their UX trade-offs.
- User verification (`UV`/`UP`) flags and resident-key policy per platform.

## Anti-Goals
- Storing the private key or an attestation secret on the server.
- Accepting a challenge that is not server-generated, single-use, and time-bounded.
- Treating passkey enrolment as a replacement for a session-security plan.

## Interview Lens
- "What exactly does RP ID binding prevent?"
- "How do you handle passkey recovery without letting an attacker downgrade to SMS?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: register and authenticate with a software authenticator.
- Wk2 QUIZ/FLASHCARDS to 90%+; verify clientData manually in a test.
- Wk3 MINI_PROJECT with passwordless login and device management.
- Wk4 REAL_WORLD_PROJECT: passkey rollout with recovery and attestation policy.

## Done = You Can
- Implement both ceremonies, and explain in detail why a stolen database backup
  cannot be used to impersonate a user.
