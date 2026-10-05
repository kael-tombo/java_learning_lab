# REST APIs - MINI PROJECT

## Project: TaskForge — a complete REST API with a contract, pagination, and versioning

Build an issue-tracker API with resource design, correct status codes, cursor pagination,
a consistent error shape, idempotency keys, and a documented deprecation path.

### Architecture

```
  Resources (nouns, hierarchy where it aids navigation)
    /api/v1/users/{userId}/projects
    /api/v1/projects/{projectId}/issues            GET (list)  POST (create)
    /api/v1/issues/{issueId}                       GET PATCH DELETE
    /api/v1/issues/{issueId}/comments              GET POST
    /api/v1/issues/{issueId}/transitions            POST  (state change as a subresource)
    /api/v1/projects/{projectId}/search?q=&state=&assignee=&cursor=&limit=

  Cross-cutting:
    - RFC 9457 problem+json for every 4xx/5xx
    - Idempotency-Key on all POSTs
    - ETag + If-Match on PATCH (optimistic concurrency)
    - Cursor pagination, stable under concurrent writes
    - Deprecation headers on the v0 alias
```

### Implementation

Resource design with correct status codes, including the ones people get wrong:

```java
@RestController
@RequestMapping("/api/v1/projects/{projectId}/issues")
class IssueController {

    /** 200 with a collection + a next cursor. Not 204 - there IS a body. */
    @GetMapping
    ResponseEntity<Page<IssueSummary>> list(@PathVariable String projectId,
                                            @RequestParam(required = false) IssueState state,
                                            @RequestParam(required = false) String cursor,
                                            @RequestParam(defaultValue = "50") @Max(200) int limit) {
        return ResponseEntity.ok(issueService.list(projectId, state, cursor, limit));
    }

    /**
     * 201 Created + Location header. The client learns the canonical URI and can immediately
     * GET it - no need for the client to reconstruct a URL, which is where most API bugs live.
     * 409 if the client-supplied idempotency key was used with a different body.
     */
    @PostMapping
    ResponseEntity<URI> create(@PathVariable String projectId,
                               @RequestHeader("Idempotency-Key") UUID key,
                               @RequestBody @Valid CreateIssueRequest body,
                               @AuthenticationPrincipal UserPrincipal caller) {
        var existing = idempotency.find(key);
        if (existing.isPresent()) {
            if (!existing.get().requestFingerprint().equals(fingerprint(body)))
                throw new Problem(ErrorType.IDEMPOTENCY_KEY_REUSE,
                        "key reused with a different request body", HttpStatus.CONFLICT);
            return ResponseEntity.status(HttpStatus.OK).location(existing.get().location()).build();
        }
        Issue issue = service.create(projectId, body, caller);
        return ResponseEntity.created(URI.create("/api/v1/issues/" + issue.id())).build();
    }

    /**
     * PATCH = partial update, so absent fields are untouched. 412 Precondition Failed when
     * If-Match does not match: the client's view is stale and silently overwriting it is
     * how lost-update bugs reach production.
     */
    @PatchMapping(path = "/{issueId}")
    ResponseEntity<Void> patch(@PathVariable String issueId,
                               @RequestHeader(value = "If-Match", required = false) String ifMatch,
                               @RequestBody PatchIssueRequest patch) {
        if (ifMatch != null && !etagService.matches(ifMatch, issueId))
            throw new Problem(ErrorType.PRECONDITION_FAILED, "resource changed since you read it",
                    HttpStatus.PRECONDITION_FAILED);
        service.patch(issueId, patch, actor());
        return ResponseEntity.noContent().eTag(etagService.current(issueId)).build();
    }

    /** 204 when deleted. No body, because there is nothing to describe. */
    @DeleteMapping("/{issueId}")
    ResponseEntity<Void> delete(@PathVariable String issueId) {
        service.delete(issueId, actor());
        return ResponseEntity.noContent().build();
    }

    /** State change modelled as a subresource: the transition history is itself retrievable. */
    @PostMapping("/{issueId}/transitions")
    ResponseEntity<URI> transition(@PathVariable String issueId, @RequestBody TransitionRequest t) {
        if (t.to() == IssueState.CLOSED && !actor().canTransition(issueId, t.to()))
            throw new Problem(ErrorType.INVALID_TRANSITION, "illegal transition " + t.from() + " -> " + t.to(),
                    HttpStatus.UNPROCESSABLE_ENTITY);   // 422: syntactically valid, semantically wrong
        var transition = service.transition(issueId, t);
        return ResponseEntity.created(URI.create("/api/v1/issues/" + issueId + "/transitions/" + transition.id())).build();
    }
}
```

Cursor pagination that stays correct when rows are inserted mid-scan — the keyset approach:

```java
@Service
class IssueQueryService {
    /**
     * Offset pagination breaks under concurrent writes: an insert before your offset shifts
     * rows and you see duplicates; a delete shifts them and you skip rows. Keyset pagination
     * is stable because the cursor encodes a sort position, not a count.
     */
    Page<IssueSummary> list(String projectId, IssueState state, String cursor, int limit) {
        var decoded = cursorCodec.decode(cursor);       // {createdAt, id} - never trust client input
        var spec = issueRepo.findByProjectId(projectId, Optional.ofNullable(state));
        if (decoded != null)
            spec = spec.where(issue.createdAt().isBefore(decoded.createdAt())
                    .or(issue.createdAt().isEqualTo(decoded.createdAt()).and(issue.id().lt(decoded.id())));

        // The id tiebreaker makes the sort total, so no row is skipped or duplicated when
        // createdAt values collide. Non-deterministic ordering is the classic pagination bug.
        var page = spec.orderBy(desc(issue.createdAt()), desc(issue.id()))
                      .limit(limit + 1)                 // fetch one extra to detect "has more"
                      .toList();
        boolean hasMore = page.size() > limit;
        var items = hasMore ? page.subList(0, limit) : page;
        String next = hasMore ? cursorCodec.encode(items.getLast()) : null;
        return new Page<>(items, next);
    }
}
```

One error shape for the entire API, handled generically by clients:

```java
@RestControllerAdvice
class GlobalProblemHandler extends ResponseEntityExceptionHandler {
    @ExceptionHandler(BusinessRuleViolation.class)
    ProblemDetail handle(BusinessRuleViolation ex) {
        // RFC 9457 problem+json: type, title, status, detail, instance, plus extensions.
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage());
        pd.setType(URI.create("https://api.taskforge.example/problems/" + ex.type().slug()));
        pd.setTitle(ex.type().title());
        pd.setProperty("violations", ex.violations());          // field-level detail
        pd.setProperty("traceId", MDC.get("traceId"));
        pd.setInstance(URI.create(requestUri()));
        return pd;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)     // override the framework default
    ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        var violations = ex.getBindingResult().getFieldErrors().stream()
            .map(f -> Map.of("field", f.getField(), "message", Objects.requireNonNullElse(f.getDefaultMessage(), "invalid")))
            .toList();
        return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "request validation failed")
            .withProperty("violations", violations);
    }
}
```

### Test It

```java
@Test void createReturns201WithLocation() {
    var res = mockMvc.perform(post("/api/v1/projects/p1/issues")
            .header("Idempotency-Key", UUID.randomUUID().toString())
            .content("{\"title\":\"Fix the build\"}"))
        .andExpect(status().isCreated())
        .andExpect(header().exists("Location"));
}

@Test void idempotentRetryReturnsSameResultAndDoesNotDuplicate() {
    UUID key = UUID.randomUUID();
    var first = create(key, "{\"title\":\"A\"}");
    var second = create(key, "{\"title\":\"A\"}");
    assertThat(first.getHeader("Location")).isEqualTo(second.getHeader("Location"));
    assertThat(issueRepo.count()).isEqualTo(1);
}

@Test void reusingKeyWithDifferentBodyIs409() {
    UUID key = UUID.randomUUID();
    create(key, "{\"title\":\"A\"}");
    mockMvc.perform(post("/api/v1/projects/p1/issues").header("Idempotency-Key", key.toString())
                   .content("{\"title\":\"B\"}"))
           .andExpect(status().isConflict()).andExpect(jsonPath("$.type").value(containsString("idempotency")));
}

@Test void staleIfMatchIs412() {
    String etag = etagFor("i1");
    service.patch("i1", new PatchIssueRequest("Changed by someone else", null));
    mockMvc.perform(patch("/api/v1/issues/i1").header("If-Match", etag).content("{\"title\":\"Mine\"}"))
           .andExpect(status().isPreconditionFailed());
}

@Test void cursorPaginationIsStableUnderConcurrentInserts() {
    var page1 = list(cursor: null, limit: 10);
    insertNewIssues(25);                                   // writes land before our cursor position
    var page2 = list(page1.nextCursor(), limit: 10);
    assertThat(concat(page1, page2).map(Issue::id)).doesNotHaveDuplicates();
}

@Test void everyErrorUsesProblemJson() {
    mockMvc.perform(get("/api/v1/issues/does-not-exist"))
           .andExpect(status().isNotFound())
           .andExpect(content().contentTypeCompatibleWith("application/problem+json"))
           .andExpect(jsonPath("$.title").exists()).andExpect(jsonPath("$.traceId").exists());
}
```

## Deliverables

- [ ] Resource design doc with URIs, methods, and status codes per operation
- [ ] Correct status codes: 200, 201+Location, 204, 304, 400, 401, 403, 404, 409, 412, 422
- [ ] Keyset cursor pagination with a total-order sort and a stability test
- [ ] `Idempotency-Key` handling including 409 on key reuse with a different body
- [ ] `ETag` + `If-Match` optimistic concurrency with a 412 test
- [ ] RFC 9457 problem+json for every error, including framework validation errors
- [ ] Filtering and sorting parameters validated and bounded
- [ ] OpenAPI spec plus a deprecation header example and a migration note
