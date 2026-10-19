# 07-information-theory - Information Theory
## Overview
Entropy H = -sum p log p is expected surprise; KL = sum p log(p/q) is the extra cost of using q; cross-entropy CE = H + KL is the total coding cost.
## Key formulas
- H(p) = -sum p log p; KL(p||q) = sum p log(p/q).
- CE(p,q) = H(p) + KL(p||q).
## What the snippets show
- Mt07A: H=1.5000 bits, KL=0.2500 bits.
- Mt07B: identity holds to 1e-4 in nats.
## Try it
Set q=p and confirm KL and excess CE both vanish.
## Formula reference
- H = -sum p log p; units bits (base 2) or nats (base e), ratio ln 2.
- KL >= 0, zero iff p = q; not symmetric, not a metric.
- Mutual information I = H(X) - H(X|Y) = KL(p(x,y)||p(x)p(y)).
## Worked example
- H([.5,.25,.25]) = 0.5 + 0.5 + 0.5 = 1.5 bits exactly.
- KL terms: 0.5*1 + 0.25*0 + 0.25*(-1) = 0.5 - 0.25 = 0.25 bits.
- Nats: H 0.8018 + KL 0.0268 = CE 0.8286; times log2(e) for bits.
## Pitfalls
- KL(p||q) != KL(q||p): direction matters (mode-seeking vs covering).
- Zero q where p > 0: infinite KL; smooth first.
- Log bases: state bits vs nats explicitly.
## Connections
- CE loss trains every classifier head in these labs.
- Distillation KL matches student to teacher distributions.
## Exercises
1. Set q = p; confirm KL = 0.
2. Compute H of [0.25]*4 in bits.
3. Convert the nats result using log2(e).
