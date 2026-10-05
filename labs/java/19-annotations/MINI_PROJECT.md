# MINI PROJECT — Annotations: Validation Mini-Framework

## Goal (2 weeks, ~8–10h)
Design `@NotBlank/@Min/@Max/@Valid` + a processor/validator that fails fast at compile time where possible and validates graphs at runtime.

## Requirements
### Functional
1. Annotations: `@NotBlank`, `@Min(long)`, `@Max(long)`, `@Valid` (cascade), `@Route(method,path)` for a tiny router; correct `@Retention/@Target` each.
2. Runtime validator: `Validator.validate(Object)` returns `List<Violation(field,msg)>`; cascades `@Valid` nested objects/collections; null-safe.
3. Compile-time processor: `@Route` duplicate-path detector emitting `error()` at the element (build fails with file:line); `getSupportedSourceVersion` current.
4. Router: scan `@Route` methods, dispatch `Map<method+path, Method>`; injected validated DTOs (400 on violations).
5. Repeatable demo: `@Tag` + `@Tags` on one endpoint; documented with `@Documented`, inherited where intended via `@Inherited` note.
### Non-functional
- No `RUNTIME` where `SOURCE/CLASS` suffices (document each choice); processor incremental-safe (no state leaks between rounds).
- 16+ tests: each constraint, cascade depth 3, duplicate-route compile failure (compile-testing or manual fixture), tag repeat, null graph.
- README: retention/target table + error-message gallery (good vs bad).
- Perf: validate 10k DTOs, report µs/object (reflection cache vs uncached).

## Phases
### Week 1 — Runtime (4–5h)
- Annotations + validator + cascade + router dispatch.
- Deliverable: validated DTO demo + 8 tests.
### Week 2 — Compile-Time (4–5h)
- Processor, duplicate detection, repeatable/meta, perf note.
- Deliverable: failing-build fixture + benchmark line.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Annotation design | Retention/target exact + justified | Correct | All RUNTIME |
| Validator | Cascade+null-safe, clean violations | Works flat | Throws on null |
| Processor | Element-pinned errors, tested | Works | System.out only |
| Router | Validated dispatch, 400 path | Dispatches | Unvalidated |
| Tests + perf | 16+ tests, cached timing | 10+ tests | Happy-path only |

Pass ≥ 70. Stretch: code generator (`@Builder` for one DTO via JavaPoet/manual Filer); `@Inherited` semantics demo with superclass test.
