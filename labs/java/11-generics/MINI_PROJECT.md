# MINI PROJECT — Generics: Type-Safe Repository

## Goal (2 weeks, ~8–10h)
Build `Repository<T,ID>` + `Box<T>`/`Pair<K,V>` that make illegal usage uncompilable — PECS-correct, erasure-aware, warning-free.

## Requirements
### Functional
1. `Repository<T,ID>`: `save/findById/findAll/delete`; `InMemoryRepository<T,ID>` backed by `Map<ID,T>` with `Function<T,ID>` id extractor.
2. Generic utils: `copy(List<? extends T>, List<? super T>)`, `max(Collection<? extends T & Comparable>)`, `firstOrEmpty` returning `Optional<T>`.
3. Erasure-proof: no `new T[]`/`instanceof T`; use `Class<T>` token + `List<T>`; document one erasure trap + workaround.
4. Bounded domain: `Entity<ID>`, `AuditedEntity extends Entity` with `<T extends AuditedEntity>` audit method.
### Non-functional
- Zero raw types / unchecked warnings (`-Xlint:all` clean); `@SuppressWarnings` only with comment (max 1).
- 18+ tests: PECS copy both directions, merge, token-cast, bounds rejection (compile-fail note).
- README: PECS diagram + erasure table.

## Phases
### Week 1 — Repo + Box (4–5h)
- Entity/Repo/InMemory + Box/Pair + 10 tests.
- Deliverable: CRUD demo across 2 entity types.
### Week 2 — Variance (4–5h)
- PECS utils, tokens, bounds; lint-clean pass.
- Deliverable: variance cheat-sheet + trap doc.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Repo design | ID-extractor, clean | Works | Raw/Object casts |
| PECS | Correct both ways + tests | One way right | Invariant misuse |
| Erasure | Trap + token fix | Avoided | `new T[]` attempt |
| Lint | -Xlint clean | 1 justified suppress | Warnings |
| Tests | 18+ | 12+ | <8 |

Pass ≥ 70. Stretch: `Repository` with `Comparator` paging; `TypeRef`-style capture demo.
