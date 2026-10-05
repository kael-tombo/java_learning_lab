# VISION — API Security Testing: Proving the Absence of Defects
> Where this lab takes you: from "run a scanner" to a testing strategy where you know what your tools do *not* cover.

## The Arc
1. **Mental model** — security testing as evidence, not as a scan result; what you are proving.
2. **SAST** — static analysis of source and dependencies; rules, false positives, and baselines.
3. **DAST** — dynamic probing, auth-state handling, and safe active scanning.
4. **API-specific** — BOLA/IDOR, mass assignment, rate limits, schema trust, and the OWASP API Top 10.
5. **Fuzzing & supply** — grammar-based fuzzing, contract testing, and pipeline gating.

## Milestones (checkable)
- [ ] M1: demonstrate BOLA on a naive endpoint and write a regression test that fails without the fix.
- [ ] M2: run a SAST tool and explain one true and one false positive in detail.
- [ ] M3: set up an authenticated DAST scan that actually holds a session.
- [ ] M4: write a fuzz target that finds a parser bug the unit tests missed.
- [ ] M5: produce a coverage statement naming what your pipeline does not test.

## Core Competencies
- Choosing the right test layer for each defect class (design, implementation, runtime, dependency).
- Authenticated scanning: session replay, token handling, multi-step flows.
- BOLA/IDOR test design using two identities and an ID matrix.
- Triaging findings: true positive, false positive, accepted risk with an expiry.

## Anti-Goals
- Reporting "scanner is green" as evidence of security.
- Unauthenticated DAST that only exercises public pages.
- Shipping a fix with no regression test, so the bug returns.

## Interview Lens
- "Your scanner found nothing. What did it not test?"
- "Walk me through finding an IDOR in an API you were given."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: run SAST, read the rules, fix one real bug.
- Wk2 QUIZ/FLASHCARDS to 90%+; set up authenticated DAST.
- Wk3 MINI_PROJECT: full local pipeline with BOLA regression tests.
- Wk4 REAL_WORLD_PROJECT: staging security test programme with gating and triage.

## Done = You Can
- Design and run a security test programme, and honestly state its coverage gaps
  to a reviewer who knows what you did not test.
