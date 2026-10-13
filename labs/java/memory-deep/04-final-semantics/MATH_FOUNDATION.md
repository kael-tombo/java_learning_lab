# Math Foundation: Final Field Semantics

## The freeze chain as an ordering formula

Name the events: `w` (final write), `f` (constructor-end freeze), `a`
(publication action), `r1` (reference read), `r2` (final read). The rule:

```
w ->hb f ->hb a ->mc r1 ->dc r2  ==>  value(r2) in {w} U later-writes
```

`->hb` is happens-before; `->mc` (memory chain) and `->dc` (dereference
chain) extend ordering through the reference. The consequent says the
reader observes the frozen write or a strictly later one — never the
pre-construction default.

## Reading the chain as a proof obligation

To claim "reader R sees initialized final x," discharge each link:

1. `w ->hb f`: the store precedes constructor end in program order.
   Holds iff the store is inside the constructor before it returns.
2. `f ->hb a`: the freeze precedes publication. Fails exactly when
   `this` escapes during construction (publication before the freeze).
3. `a ->mc r1`: the reader's reference load is memory-chained after the
   publication. Holds for any path by which the bits travelled.
4. `r1 ->dc r2`: the final read goes through the loaded reference.
   Holds iff the reader dereferences the obtained reference (not a
   stale or speculative unrelated read).

If link 2 fails (escape), no conclusion follows: default values are
legal observations. If link 1 fails (post-construction reflective
write), the write is outside the model and the formula does not apply.

## Transitivity as chain composition

For a final array element reached through a final reference, compose two
chains: element-store to array-freeze, then array-reference-freeze to
reader. The composition is valid only when every allocation and fill
happened inside the constructing thread before the outer freeze. Aliased
caller-owned storage breaks link 1 of the inner chain.

## Why defaults are the only alternative

A final field has exactly two candidate sources at read time: the
pre-construction default (zero/null) and the frozen write. The rule
eliminates the default whenever the chain holds. There is no third
"value from thin air": out-of-thin-air reads are prohibited, so the
reader's observation set is precisely {default (chain broken), frozen
value (chain holds)}.

## No probabilities, no statistics

The guarantee is universal, not statistical: 3000 exact rounds are
evidence of the rule, not the rule itself. The mutable twin's 3000
passing rounds license no formula at all — without the chain, the
observation set legally includes stale values on every round.
