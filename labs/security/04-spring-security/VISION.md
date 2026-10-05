# VISION — Spring Security: The Filter Chain as Architecture
> Where this lab takes you: from "add the starter and it works" to reasoning about every filter, its order, and its blast radius.

## The Arc
1. **Mental model** — `SecurityFilterChain` as an ordered list of `Filter`s; servlet filter vs Spring `Interceptor`.
2. **Bootstrapping** — what the starter auto-configures, and how to see it.
3. **Authentication** — providers, managers, `UserDetailsService`, password encoding.
4. **Authorization** — request matchers, method security, URL-vs-Java-level enforcement.
5. **Composition** — multiple chains, `securityMatcher`, OAuth2/resource-server/reactive variants.

## Milestones (checkable)
- [ ] M1: print the actual filter chain at runtime and annotate each filter's job.
- [ ] M2: explain why a custom filter must be `@Component`-free or it registers twice.
- [ ] M3: replace a `hasRole` URL rule with `@PreAuthorize` and show the difference in enforcement point.
- [ ] M4: define two `SecurityFilterChain` beans with disjoint `securityMatcher` scopes and prove isolation.
- [ ] M5: diagnose why CSRF is silently disabled on one endpoint.

## Core Competencies
- Filter ordering semantics and how a mistake opens an authentication bypass.
- Choosing request-level vs method-level authorization, and enforcing both.
- Configuration-based (users/roles) vs Java-based (`UserDetailsService`) identity stores.
- Reading stack traces from `AccessDeniedException`/`AuthenticationException` to locate the rejecting filter.

## Anti-Goals
- Adding `permitAll()` to silence a failing test.
- Putting business authorization only in URL matchers while internal method calls bypass it.
- Assuming the starter's defaults match your threat model.

## Interview Lens
- "Where does authentication actually happen in a Spring Boot app, and why does order matter?"
- "Your new controller is unprotected. Which single bean did you forget to define?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES; dump the filter chain and draw it.
- Wk2 QUIZ/FLASHCARDS to 90%+; rebuild the config from scratch without docs.
- Wk3 MINI_PROJECT: custom filter chain + method security.
- Wk4 REAL_WORLD_PROJECT: multi-chain split for a mixed public/private API.

## Done = You Can
- Read any Spring Security config and predict the behaviour of an unauthenticated
  request before running it — and prove the prediction with a test.
