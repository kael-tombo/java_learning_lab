# VISION — Enums

## Vision Statement
**Enums are typesafe state machines, not int constants** — model lifecycles,
strategies, and lookup tables as enum types so illegal states are
unrepresentable and `switch` is exhaustive and refactor-safe.

---

## Mental Models
### 1. Enum = Final Class + Fixed Instances
Each constant is a singleton; constructors private, fields final. Identity
`==` is correct here. `ordinal()` is an implementation detail — never persist
it; persist `name()` or an explicit code.
### 2. Behavior Lives Inside
Constants override abstract methods (`FEE.calculate()`) — replaces
`switch`-walls with polymorphism. Add `fromCode()` factories returning
`Optional` instead of throwing on unknown input.
### 3. Enum Collections Are Bitsets
`EnumSet` is a bit vector, `EnumMap` an array — fastest `Set/Map` in the JDK.
Reach for them for flags, transitions, and per-state config.
### 4. Switch Must Be Exhaustive
`switch` expressions force exhaustiveness (with sealed/enum); add a default
only when forward-compat demands it. Unknown-wire-values map to `UNKNOWN`,
never crash the parser.

---

## Decision Framework
| Question | Rule |
|----------|------|
| int/String status? | Enum with explicit `code` field |
| Per-constant logic? | Abstract method override, not switch |
| Lookup by code? | Static `Map<code,Enum>` + `Optional` return |
| Persist? | Store `name()`/code, never `ordinal()` |
| Flags set? | `EnumSet`, not booleans or bit ints |

---

## Career Trajectory
- **L1:** Constants, `valueOf`, switch, `EnumSet/EnumMap` basics.
- **L2:** Strategy enums, `fromCode`, JSON mapping (`@JsonValue/@JsonCreator`).
- **L3:** State-machine design, transition tables, event sourcing with enums.
- **L4:** Domain vocabulary governance (API enums, compat policy).

---

## 4-Week Path
```
W1: Basics, valueOf pitfalls, switch expressions, EnumSet/EnumMap.
W2: Strategy enums, fromCode factories, persistence mapping.
W3: Order-state-machine kata (transitions table + tests).
W4: Payment-status service capstone + Jackson compat review.
```
## Success Metrics
- [ ] No ordinal persisted; unknown codes map to UNKNOWN/Optional
- [ ] Switch exhaustive; per-constant behavior tested per constant
- [ ] State transitions reject illegal moves with tests
