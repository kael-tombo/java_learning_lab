# MINI_PROJECT — Arithmetic: Exact Calculator & Money Ledger
> Implement + verify + benchmark. ~3 hours.

## Goal
Build a CLI calculator that (a) evaluates integer/fraction expressions exactly via
`BigInteger` numerators/denominators, (b) formats money to cents with rounding-half-even,
and (c) reports operation counts and overflow incidents.

## Build Steps
1. `Fraction.java`: reduce on construction (gcd), add/mul/div, toString `p/q`.
2. `Parser.java`: shunting-yard for `+ - * /` with parentheses and unary minus.
3. `Money.java`: store cents as long; `format`, `split(n, mode)` distributes remainder.
4. `OverflowGuard.java`: `checkedAdd/Sub/Mul` wrapping `Math.addExact` etc.
5. Drive: parse 20 expressions, print exact results, and a ledger split demo.

## Sample Run (fill with your numbers)
```
expr: (2/3 + 5/6) * 3/4  = 3/2
ledger: $100.00 split 3 ways → 33.34, 33.33, 33.33 (remainder tracked)
int overflow at 2147483647 + 1 → caught, message logged
```

## Benchmark Table (fill)
| expr complexity | parse µs | eval µs | fractions reduced |
|-----------------|----------|---------|-------------------|
| depth 2         | | | |
| depth 5         | | | |
| depth 10        | | | |

## Acceptance
- [ ] `1/3 + 1/3 + 1/3` prints exactly `1/1`.
- [ ] Money split reconciles to the cent with the ledger.
- [ ] One overflow triggers a clear message, not wraparound.

## Extensions
- Add decimal mode with configurable precision (BigDecimal).
- Expression history + undo via immutable value objects.
