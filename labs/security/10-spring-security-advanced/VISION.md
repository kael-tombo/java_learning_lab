# VISION — Spring Security Advanced: Composition at Scale
> Where this lab takes you: from one filter chain to reactive, multi-protocol, multi-tenant configurations that stay debuggable.

## The Arc
1. **Resource servers** — JWT vs opaque introspection, and the operational trade-off of each.
2. **Method & domain security** — `@PreAuthorize`, SpEL, custom permission evaluators.
3. **Reactive security** — `SecurityWebFilterChain`, non-blocking context propagation.
4. **Composition** — multiple chains, custom authentication providers, `AuthenticationManager`.
5. **Operations** — testing strategy, debug endpoints, metrics on security decisions, and
   the performance cost of every choice.

## Milestones (checkable)
- [ ] M1: choose introspection vs local JWT verification for a given constraint and defend it.
- [ ] M2: write a custom `AuthenticationProvider` for an existing credential store.
- [ ] M3: port a filter-chain rule to `SecurityWebFilterChain` without blocking the event loop.
- [ ] M4: build a custom `AuthorizationManager` and unit-test it without a servlet container.
- [ ] M5: measure the per-request cost of method security and decide whether to keep it.

## Core Competencies
- Servlet vs reactive security models and the reactive context pitfalls.
- Introspection caching, token revocation propagation, and failure-mode behaviour.
- SpEL-based authorization with custom permission evaluators, kept type-safe.
- Security-focused testing that does not accidentally bypass the chain under test.

## Anti-Goals
- Adding `@PreAuthorize` to every method by reflex with no performance measurement.
- Blocking calls inside a reactive filter chain.
- Testing security by calling the service directly and calling it covered.

## Interview Lens
- "When would you pick opaque tokens over self-contained ones, and what's the cost?"
- "How do you debug why a request got a 403 with a complex SpEL expression?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: build a resource server and a custom provider.
- Wk2 QUIZ/FLASHCARDS to 90%+; port a rule to reactive and compare.
- Wk3 MINI_PROJECT: multi-chain app with opaque and JWT chains side by side.
- Wk4 REAL_WORLD_PROJECT: mixed servlet/reactive platform with layered authorization.

## Done = You Can
- Configure, test, and reason about advanced Spring Security in a large mixed-stack
  application without guessing, and justify the cost of each enabled feature.
