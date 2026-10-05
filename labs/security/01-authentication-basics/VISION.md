# VISION — Authentication Basics: From Passwords to Multi-Factor
> Where this lab takes you: from "who are you?" as a hand-rolled string compare to a hardened, observable identity layer.

## The Arc
1. **Identity** — authentication vs authorization, the factor taxonomy (something you know / have / are).
2. **Storage** — why fast hashes are the wrong tool; salted slow hashing; peppering; rotation.
3. **Sessions** — server-side state, cookies, fixation defence, idle vs absolute timeouts.
4. **Elevation** — TOTP, WebAuthn, recovery codes, and why SMS-MFA is the weakest tier.
5. **Hardening** — throttling, lockout, enumeration-safe responses, and audit trails.

## Milestones (checkable)
- [ ] M1: implement Argon2id (or BCrypt) hashing with a per-user random salt and constant-time verification.
- [ ] M2: explain in one sentence why an unsalted SHA-256 password table is offline-crackable in seconds.
- [ ] M3: defend against session fixation and reproduce the attack against a naive filter chain.
- [ ] M4: implement TOTP verification from scratch and explain the ±1 window tolerance.
- [ ] M5: design a lockout + throttle policy that survives distributed credential stuffing.

## Core Competencies
- Password hashing API selection driven by memory-hardness, not habit.
- Session lifecycle design: create-on-authenticate, rotate ID, destroy on logout.
- Identity-proofing strength comparisons you can defend to a non-security stakeholder.
- Enumeration-resistant error handling (identical response and timing for unknown user).

## Anti-Goals
- Treating "authentication" as a boolean flag in a request-scoped bean.
- Storing plaintext, reversibly-encrypted, or unsalted password material anywhere.
- Locking accounts without logging and alerting the event as a security signal.

## Interview Lens
- "Why bcrypt over SHA-256?" "How do you prevent session fixation?"
- "Your login endpoint leaks which usernames exist — walk me through the fix."

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1–L3; build the hashing utility blind.
- Wk2 QUIZ/FLASHCARDS to 90%+, then MINI_PROJECT end-to-end.
- Wk3 REAL_WORLD_PROJECT war-story + teach-back (5-min whiteboard).
- Wk4 attack the finished system: credential stuffing harness + write the findings.

## Done = You Can
- Ship an authentication layer that survives enumeration, brute force, and session
  hijack attempts, and explain each defensive choice to an auditor.
