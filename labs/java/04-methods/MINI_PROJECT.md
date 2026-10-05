# MINI PROJECT — Methods: String & Math Utility Library

## Goal (2 weeks, ~8–10h)
Ship a documented `textutils`/`mathutils` library demonstrating overload hygiene, varargs, defensive copies, recursion-vs-iteration.

## Requirements
### Functional
1. `Strings`: `isBlank`, `truncate(s,max)`, `slugify`, `join(sep, parts...)`; overload `truncate(s,max,ellipsis)`.
2. `Maths`: `gcd`, `factorial(int→long, overflow-checked)`, `fibonacci` iterative + recursive (document stack limit), `average(double...)`.
3. Pass-by-value demo: `swap`-attempt vs `shuffle(int[])` showing reference-copy semantics in javadoc + test.
4. Null policy: no null returns — empty string/list or `Optional`/`IllegalArgumentException`.
### Non-functional
- Full javadoc (`@param/@return/@throws`) on public API; `mvn javadoc` clean.
- 25+ tests incl. overload-resolution edge (`average()` empty → throw) and overflow.
- No boolean-param methods; ≤3 params or parameter object.

## Phases
### Week 1 — API + Impl (4–5h)
- Signatures first (review overload set), then impl; javadoc drafts.
- Deliverable: API listing + 12 tests green.
### Week 2 — Hardening (4–5h)
- Varargs/defensive-copy tests, recursion limit doc, README with complexity notes.
- Deliverable: published checklist + demo `Main`.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Signature design | Unambiguous, ≤3 params | Usable | Ambiguous overloads |
| Varargs/copies | Correct + tested | Correct | Aliasing bugs |
| Recursion doc | Limit measured | Stated | Missing |
| Javadoc | Complete, useful | Present | Sparse |
| Tests | 25+ incl. edges | 15+ | <10 |

Pass ≥ 70. Stretch: `Stats.median/mode` with parameter object; pitest mutation check.
