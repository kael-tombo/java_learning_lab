# Visual Guide: Logic and Proofs

## Truth Table for P → Q

```
 P | Q | P → Q
---+---+------
 T | T |   T
 T | F |   F
 F | T |   T
 F | F |   T
```

The implication is false only in row 2 (P true, Q false).

## Logic Gate Diagrams

```
 NOT P:          P ──[NOT]── ¬P

 P AND Q:        P ──┐
                      [AND]── P ∧ Q
                 Q ──┘

 P OR Q:         P ──┐
                      [OR]─── P ∨ Q
                 Q ──┘

 P → Q:          P ──┐
                      [IMPLY]─ P → Q
                 Q ──┘
```

## Proof Tree (Natural Deduction)

```
                    P → Q    P
                    ───────────── →-elim
                           Q
                    ───────────── →-intro (discharge P)
                        P → Q
```

## Venn Diagram for Logical Equivalence

```
 P → Q  ≡  ¬P ∨ Q

   P          Q
  ┌───┐    ┌───┐
  │   │    │   │
  │ ┌─┼────┼─┐ │
  │ │ │    │ │ │
  └─┼─┘    └─┼─┘
    │        │
    └────────┘
  P → Q is true everywhere
  except where P is true
  and Q is false.
```

## Induction as Dominoes

```
Base case:  [1] falls
            ↓
Inductive:  [k] falls → [k+1] falls
            ↓
Result:     [1] [2] [3] [4] ... all fall
```

## Quantifier Scope Diagram

```
∀x ∃y R(x,y):

  x₁ ──→ y₁
  x₂ ──→ y₂    (each x gets its own y)
  x₃ ──→ y₃

∃y ∀x R(x,y):

  x₁ ──┐
  x₂ ──┼──→ y*   (one y works for all x)
  x₃ ──┘
```
