# Math Foundation: Policies as Decision Functions

## Subtask state machine

Each handle occupies exactly one of three states, with two terminal
transitions and no other edges:

```
UNAVAILABLE ── callable returns ──→ SUCCESS
UNAVAILABLE ── callable throws ───→ FAILED
```

No transition leaves `SUCCESS` or `FAILED`; no transition exists between
them. `state()` is the observation function, `get()` is defined only on
`SUCCESS`, `exception()` is non-null only on `FAILED`.

## Policy decision table: ShutdownOnFailure

| Completion event | Scope action | Terminal outcome |
|---|---|---|
| subtask → SUCCESS, others pending | record value, keep waiting | — |
| all subtasks → SUCCESS | join returns | `throwIfFailed()` no-op, all `get()` valid |
| any subtask → FAILED | `shutdown()`, interrupt siblings | `throwIfFailed()` rethrows first failure |
| `joinUntil` deadline passes first | `TimeoutException` to owner | `close()` still reaps leftovers |

Conjunction semantics: the scope value is the tuple of all subtask
values; a single `FAILED` poisons the tuple.

## Policy decision table: ShutdownOnSuccess<T>

| Completion event | Scope action | Terminal outcome |
|---|---|---|
| subtask → FAILED, others pending | record failure, keep waiting | — |
| any subtask → SUCCESS | `shutdown()`, cancel siblings | `result()` returns first success |
| all → FAILED, none succeeded | join returns | `result()` throws `ExecutionException` |
| empty scope (nothing forked) | join returns at once | `result()` throws `IllegalStateException` |

Disjunction semantics: the scope value is the first success; failures
matter only when no success exists to preempt them.

## First-wins as argmin over completion time

Let c(i) be subtask i's completion instant. Under `ShutdownOnFailure`
the outcome is determined by argmin over failing completions versus the
max over all completions (all-must-finish); under `ShutdownOnSuccess`
by argmin over succeeding completions. Siblings with c(j) beyond the
decision instant are cancelled — their values are never observed.

## Custom policies: threshold predicates

`handleComplete` implements a predicate P over the multiset of observed
completions; when P turns true the override calls `shutdown()`. Quorum
(k-of-n successes),partial-result (first m arrivals regardless of
status), and deadline-plus-best-so-far are all threshold predicates on
counts, distinguished only by which completions they count.
## joinUntil as a bounded quantifier

`join()` waits for ∀ subtasks: completed(i). `joinUntil(T)` waits for
(∀i completed(i)) ∨ (now ≥ T), raising `TimeoutException` on the second
disjunct. The deadline weakens the universal claim without weakening
containment: `close()` still enforces ∀i reaped(i) on block exit.

## Ownership as an access matrix

| Operation | Owner thread | Other thread | Subtask thread (nested scope) |
|---|---|---|---|
| `join()` / `close()` / `result()` | allowed | `WrongThreadException` | allowed on its own scope |
| `fork()` before close, same bindings | allowed | n/a (not owner path) | allowed into its own scope |
| `fork()` after close | `IllegalStateException` | `IllegalStateException`* | `IllegalStateException` |
| `fork()` under changed bindings | `StructureViolationException` | — | `StructureViolationException` |

*Any thread forking a closed scope fails; ownership is moot after close.
