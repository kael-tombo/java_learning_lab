# AI Safety & Alignment — Mathematical Foundation

## The RLHF recipe at conceptual granularity

The standard skeleton (statements kept loose intentionally; details vary by team):

```
1. SFT        a model imitates curated demonstrations (supervised fine-tuning)
2. RM         a reward model learns preferences over ranked outputs
3. RL/PPO-ish the tuned-policy is optimized against the RM reward
```

with two standard objectives written compactly in the literature:

```
reward model:  L_RM = - E_{(x, y-win, y-lose) ~ human prefs} [ log sigmoid( r(x, y-win) - r(x, y-lose) ) ]
policy stage:  J(pi) = E_{x,y~pi} [ r(x, y) - beta * KL( pi(.|x) || pi_ref(.|x) ) ]
```

The KL anchor term is the part worth memorizing: it keeps the optimized policy from
drifting impossibly far from its reference, and its strength `beta` is a dial between
reward-chasing and staying-honest-ish. What the formula does NOT settle: sampling quality,
eval validity, miscalibration of the reward model, and every robustness concern below —
all treated as open.

## Selective prediction, the coverage/accuracy trade

Each prediction carries a confidence score `s(x)`; a threshold `t` decides whether to
answer or abstain.

```
coverage(t)  = P[ s(x) >= t ]
accuracy(t)  = P[ correct | s(x) >= t ]
```

Raising `t` shrinks coverage toward 0 while answered-set accuracy usually rises — the
monotone coupling the snippet prints. The engineering question is not "the best t" but
which operating point the deployment can justify: a desk with humans answering the
abstentions can afford low coverage; a fully automated path cannot.

## Proxy-gap logic, argmax version

If a deployed preference signal `s(x)` imperfectly ranks the truth labels `y`, the
selection rule `argmax s` inherits `s`'s blind spots:

```
honestPlayer accuracy = P[ correct under truth-best pick ]
rmPlayer accuracy     = P[ correct under s-best pick ]
gap = honest - rm      (zero only if s ranks truth perfectly)
```

The hand-typed table in the snippet makes the mechanism visible rather than statistical:
with `s_c, c = (0.3, 0.9)` and truth `(1, 0)`, the argmax moves to the flattering-but-wrong
candidate in all three rows. This is a simulation; the well-known name attached to the
pattern is reward hacking, and the lesson generalizes only in spirit.

## Quantities worth being able to retell

- Coverage ladder from the snippet: `0.20, 0.40, 0.60, 0.80, 1.00` versus answered-set
  accuracy `1.0000, 1.0000, 0.6667, 0.7500, 0.6000` — NOT monotone (the 0.6667 row), so a
  threshold sweep is data, not a law; read the actual rows before quoting.
- Accuracy integrated over both players: `2/3` vs `0/3` for the rm selection in the toy
  table.
