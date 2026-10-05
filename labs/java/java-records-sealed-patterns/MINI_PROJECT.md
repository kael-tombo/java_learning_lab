# Mini Project — Expression Evaluator

## Goal
Parse + eval `2*(3+4)` via sealed AST + exhaustive switch.

## Model
```java
sealed interface Expr permits Lit, Add, Mul { }
record Lit(double v) implements Expr {}
record Add(Expr l, Expr r) implements Expr {}
record Mul(Expr l, Expr r) implements Expr {}
double eval(Expr e) {
  return switch (e) {
    case Lit(double v) -> v;
    case Add(Expr l, Expr r) -> eval(l) + eval(r);
    case Mul(Expr l, Expr r) -> eval(l) * eval(r);
  };
}
```

## Steps
1. Hand parser (recursive descent) → Expr.
2. eval + pretty-printer switches (both exhaustive, no default).
3. Null-safe entry (`case null -> throw`).
4. Tests: precedence, parens, 20 cases.

## Acceptance
- All tests pass; mutation (new variant) breaks compile until handled.
- No instanceof chains; V ≤ 5 per switch.

## Stretch
- Variables + `when` guards (div-by-zero).
- Bytecode-ish IR + constant folding.

## Demo (2 min)
Eval 3 exprs, show pretty print + result.
