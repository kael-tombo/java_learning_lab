# Model Registry & Versioning - Vision & Where This Is Going

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Future State

Registries converge with evaluation and deployment into a single control plane where promotion is a policy decision evaluated automatically from evidence. The interesting engineering moves from storage to linearisability, reachability and pre-authorised rollback.

The test of that future state is boring: a new engineer ships a change to model registry & versioning on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Versions are immutable and content-hashed; stages are atomic pointers.
- Promotion is a CAS against an expected current version.
- Gates are declarative and return readable reasons.
- Rollback is pre-authorised, cached locally and rehearsed on a schedule.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Store | Register versions with hashes and metadata. |
| L2 | Stage | Move pointers through environments with a gate. |
| L3 | Shadow | Compare challenger to champion on matured labels before promoting. |
| L4 | Automate | Pre-authorised rollback, scheduled drills, policy-as-code gates. |

## 4. Behaviours to Build

Promote on evidence, not confidence. Make rollback a button, not a meeting. Treat any gate you routinely bypass as a gate that needs redesign.

## 5. Anti-Vision (the failure mode we are avoiding)

- Direct database edits to stage pointers.
- Editing an artifact in place because the new one was slightly better.
- Promotion by whoever is most senior in the room.
- A rollback runbook that has never been timed.

## 6. Technology Shifts That Change the Work

1. Policy-as-code promotion gates evaluated automatically from evidence.
1. Registry, evaluation and deployment unified in one control plane.
1. Automated shadow-to-promotion with statistical promotion criteria.
1. Reachability-aware lifecycle management across regions and tenants.

## 7. Your 30/60/90 Commitment

- **30 days.** Build a registry with CAS promotion and prove concurrent promotion fails safely.
- **60 days.** Add a declarative gate and a shadow evaluation on matured labels.
- **90 days.** Run a timed rollback drill, pre-authorise rollback, and add retention with reachability.

## 8. How To Tell You Are Actually Getting Better

- Concurrent promotions cannot corrupt my stage pointers.
- Every entry traces to a run, a data version and a commit.
- Rollback is one command and I know how long it takes.
- My promotion gate blocks bad models for named reasons.

## 9. Principles That Should Not Change

- **Model model versions, stages** Model model versions, stages and their transitions explicitly
- **Define what makes a version promotable** Define what makes a version promotable and encode it as a gate
- **Implement champion/challenger promotion with shadow evaluation** Implement champion/challenger promotion with shadow evaluation

> A registry without an atomic pointer move and a rehearsed rollback is a folder with better naming.
