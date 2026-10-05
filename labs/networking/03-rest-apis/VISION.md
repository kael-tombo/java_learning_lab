# VISION — REST APIs: Resource Design That Survives Its First Client
> Where this lab takes you: from "make it JSON" to designing a contract that can be versioned, cached, and evolved.

## The Arc
1. **Constraints** — client/server, stateless, cacheable, uniform interface; what each buys you.
2. **Resource modelling** — nouns not verbs, hierarchy, and why `/orders/5/items` beats
   `/getOrderItems?orderId=5`.
3. **Methods & status** — the full semantics matrix, and correct status code selection.
4. **Contracts** — pagination, filtering, sorting, error shapes, and versioning strategies.
5. **Evolution** — additive vs breaking changes, deprecation, and API gateways.

## Milestones (checkable)
- [ ] M1: model a domain as resources and defend each URI against an alternative.
- [ ] M2: return correct status codes for 10 scenarios without checking documentation.
- [ ] M3: implement cursor pagination that stays stable under concurrent inserts.
- [ ] M4: design a consistent error shape and prove a client can handle it generically.
- [ ] M1: make a backward-compatible change to a live API and document why it is safe.

## Core Competencies
- Resource hierarchy design, including when flat beats nested.
- Pagination, filtering, sorting, and their consistency and cacheability implications.
- Idempotency for safe retries, and HATEOAS where it genuinely helps.
- Versioning and deprecation as a communication problem as much as a routing one.

## Anti-Goals
- RPC-in-disguise: `/doCreateOrder`, `/getOrderList` as verbs.
- Returning 200 with an error body because "our client checks the field".
- Non-deterministic pagination that skips or duplicates rows under load.

## Interview Lens
- "Why not `POST /orders` with an action field instead of a new resource?"
- "How do you paginate a table that is being written to continuously?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: design and critique URI hierarchies.
- Wk2 QUIZ/FLASHCARDS to 90%+; status code and error-shape drills.
- Wk3 MINI_PROJECT with a full API contract and tests.
- Wk4 REAL_WORLD_PROJECT: a versioned public API with real clients and deprecation.

## Done = You Can
- Design an API a third party can integrate against from documentation alone, and
  evolve it without breaking anyone.
