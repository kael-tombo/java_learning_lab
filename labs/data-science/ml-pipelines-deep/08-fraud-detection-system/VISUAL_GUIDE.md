# Fraud Detection System - Visual Guide

## Decision path
```text
tx -> [features] -> [rules]--hit--> block / step-up
                      |
                   no hit
                      v
                   [model score]--high--> block
                                --mid---> review queue --> label
                                --low---> pass
```

## Threshold tradeoff
```text
threshold low:   recall up, reviews flood
threshold high:  reviews calm, misses grow
```

## Label maturity
```text
day:    0    1    2    3    4    5    6
labeled:5%  18%  42%  70%  88%  96% 100%
```

## Adversarial cycle
```text
attack -> rule cover -> retrain -> deploy -> attackers shift -> repeat
```

## Review economics
```text
band wide:   reviews flood, misses rare     (staffing binds)
band narrow: reviews calm, misses grow      (loss binds)
price both with the fitted ratio, then check capacity
```

## Parity check
```text
training features  --join on key-->  compare  --match--> parity ok
serving features   --overlap days-->  values   --drift--> shared-path fix
```
