# Quiz: Final Field Semantics

## Q1: An object with final fields is published through a plain (racy)
## static with no synchronization. What does a reader observe?
**A:** The fully initialized finals. JLS 17.5 orders the freeze before
any post-construction final read through the mc/dc chain, even across a
data race on the reference. The lab shows 3000/3000 exact rounds.

## Q2: The constructor assigns `published = this` before storing final
## `x`, with a 300 ms sleep before the store. A reader spins on
## `published` and reads `x` immediately. What value, and why?
**A:** Default 0. The publication precedes the freeze, so the chain
`w ->hb f ->hb a` cannot form — no freeze stands between the write and
the early read. After construction completes, `x` reads 42.

## Q3: A record `Config(String host, int port, List<String> tags)` is
## published through the same racy static. Which parts are safe?
**A:** The components (`host`, `port`, `tags` reference) are safe —
they are finals. Whether the tags *contents* are safe depends on the
list: `List.of` contents are safe (immutable, transitive rule); a
mutable `ArrayList`'s contents still race.

## Q4: The mutable twin (plain fields, same harness) passes 3000 rounds
## on x86. Does it carry the same guarantee? Explain.
**A:** No. It passes by TSO store ordering and coherence accident on
this hardware, with no specification behind it. Verdict remains data
race; a weaker CPU or reordering JIT may show stale values.

## Q5: A `final ArrayList` field is safely published. A second thread
## calls `get(0)` while the first calls `add`. Safe?
**A:** No. The reference publication is safe; the contents mutate under
ordinary race rules. Finals cover initialization only, never later
mutation.

## Q6: Post-construction reflective writes to a final field: covered?
**A:** No. They sit outside the memory model; behavior is unspecified
and version-dependent (JIT constant folding may keep returning the old
value). Never rely on any observed outcome.

## Q7: Why does unsynchronized String sharing work?
**A:** `String` stores state in `final byte[] value` + `final byte
coder`. Every handoff uses the 17.5 freeze, including array contents via
transitivity. No read-path locks exist because the seal makes them
unnecessary.
