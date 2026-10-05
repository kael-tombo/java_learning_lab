# Flashcards — Records / Sealed / Patterns

| Q | A |
|---|---|
| record decl? | record P(int x, int y) {} |
| Accessor? | p.x(), not getX() |
| Compact ctor? | P { validation } |
| Canonical ctor? | Full param list |
| Static member? | Allowed in record |
| Extend? | Cannot extend; can impl |
| equals? | Component-wise |
| toString? | P[x=.., y=..] |
| Mutable array? | Copy in/out |
| Generic record? | record Box<T>(T v) {} |
| Record + annot? | On component/field |
| sealed? | permits fixed subtypes |
| permits list? | Same package/module |
| non-sealed? | Open branch |
| final variant? | Closed leaf |
| Exhaustive? | All cases covered |
| default? | Fallback, avoid if exhaustive |
| case null? | Explicit null arm |
| Guard? | case C c when cond |
| Dominance? | Unreachable later case |
| instanceof pat? | instanceof C c |
| Scope? | After true-check |
| && with pat? | Allowed flow scope |
| \|\| with pat? | c not in scope |
| Switch expr? | switch(){case..->..} |
| Arrow vs colon? | Arrow no fallthrough |
| Yield? | yield v in block case |
| Record pattern? | User(String n, int a) |
| Nested? | Order(Cust(String n),..) |
| Unnamed (_)? | JDK 22+ wildcard |
| Deconstruct null? | Fails match, no throw |
| Var name clash? | No redeclare in scope |
| Overload switch? | Return type unify |
| Total pattern? | Always matches (var) |
| Refine Object? | case String s -> |
| Number hierarchy? | Seal or default |
| Enum switch? | Exhaustive w/o default |
| Sealed + enum? | Both exhaustive |
| Visitor replace? | Switch over sealed |
| JSON record? | Canonical ctor deser |
| Jackson param? | ParameterNames module |
| Compact JSON? | Fewer fields |
| permits reflect? | getPermittedSubclasses() |
| isRecord()? | Class.isRecord() |
| getRecordComps? | getRecordComponents() |
| Canonical test? | getCanonicalConstructor |
| Pattern perf? | Same as casts |
| Megamorphic? | Switch → tableswitch |
| Null-first? | case null before total |
| Guard order? | Specific before general |
| Side-effect guard? | Avoid; pure only |
| when vs &&? | when in switch, && in if |
| Deconstruct depth? | Nest 2-3 max readability |
| Big switch? | Split by sealed subtype |
| DTO rule? | Record for immutable DTO |
| Entity rule? | Class for mutable/JPA |
| Event modeling? | Sealed interface events |
| State machine? | Sealed states + switch |
| Exhaust CI? | -Werror + no default |
| Preview flag? | --enable-preview (older) |
| JDK 21 stable? | Patterns + switch stable |
| Record patterns stable? | JDK 21/22 |
