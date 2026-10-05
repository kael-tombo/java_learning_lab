# Quiz — Records / Sealed / Patterns (20 Q)

1. Record components are?
> Final fields + accessor + equals/hashCode/toString.
2. Compact constructor?
> No param list; validates/normalizes.
3. Can record extend class?
> No; implicitly extends Record.
4. Mutable component fix?
> Defensive copy in ctor/accessor.
5. sealed permits?
> Closed subtype list.
6. non-sealed?
> Reopens a branch for extension.
7. Exhaustive switch?
> Covers all permitted + null if needed.
8. Dominance error?
> Earlier case subsumes later — reorder.
9. Guard keyword?
> `when` clause on case.
10. Record pattern?
> `Point(int x, int y)` deconstructs.
11. Nested pattern?
> Pattern inside pattern.
12. null in switch?
> `case null ->` explicit; else NPE.
13. Pattern var scope?
> Flow-scoped after match true.
14. instanceof + &&?
> `instanceof C c && c.x()>0` allowed.
15. Switch expression value?
> Every arm yields value or throws.
16. default needed?
> Only if non-exhaustive.
17. Permits across modules?
> Same module/package constraint.
18. Record serialization?
> Canonical ctor used; add serialVersionUID not needed.
19. When to use sealed?
> Fixed known variants (AST, events).
20. Anti-pattern?
> Stringly-typed codes instead of sealed variants.
