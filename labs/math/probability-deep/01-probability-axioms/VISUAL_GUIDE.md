# Visual Guide: Probability Axioms

## Probability tree (medical test, P(D)=0.01)
```
                       Ω
          ┌────────────┴────────────┐
        D (0.01)                 ¬D (0.99)
     ┌────┴────┐              ┌─────┴─────┐
   + (0.99)  ¬+ (0.01)     + (0.05)    ¬+ (0.95)
     0.0099     0.0001        0.0495      0.9405

  P(+) = 0.0099 + 0.0495 = 0.0594
  P(D | +) = 0.0099 / 0.0594 = 0.1667
```
Multiply along branches; add across branches at the same node; divide the branch you want by the node you observed.

## Inclusion–exclusion as overlapping patches
```
   ┌────────────────────────────────────┐
   │   ┌──────────────┐                 │
   │   │  A           │   P(A)=0.5      │
   │   │      ┌───────┼──────┐          │
   │   │      │ A∩B   │0.2   │          │
   │   ├──────┼───────┘      │          │
   │   │      │          B   │ P(B)=0.4 │
   │   └──────┴──────────────┘          │
   │              P(A∪B) = 0.5+0.4−0.2  │
   │                            = 0.7   │
   └────────────────────────────────────┘
```

## Two-dice space Ω (36 equally likely cells)
```
        1      2      3      4      5      6
    ┌──────┬──────┬──────┬──────┬──────┬──────┐
  1 │ 2    │ 3    │ 4    │ 5    │ 6    │ 7    │
  2 │ 3    │ 4    │ 5    │ 6    │ 7    │ 8    │
  3 │ 4    │ 5    │ 6    │ 7    │ 8    │ 9    │
  4 │ 5    │ 6    │ 7    │ 8    │ 9    │10    │
  5 │ 6    │ 7    │ 8    │ 9    │10    │11    │
  6 │ 7    │ 8    │ 9    │10    │11    │12    │
    └──────┴──────┴──────┴──────┴──────┴──────┘
  A = "sum ≥ 9": 10 cells        → 10/36
  B = "doubles": diagonal         →  6/36
  A∩B = {(5,5),(6,6)}             →  2/36
```

## Conditioning as re-cropping
```
  before B:  |#########|                 P(A) relative to Ω
  observed B:        |######|            everything else discarded
  after:      scale so |######| = 1      P(A|B) = A∩B / B
```
