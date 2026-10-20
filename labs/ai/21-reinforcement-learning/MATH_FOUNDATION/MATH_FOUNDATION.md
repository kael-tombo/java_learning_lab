# Reinforcement Learning — Mathematical Foundation

Everything below is the standard result set for tabular RL. We use ASCII math with
`gamma` for the discount and `E` for expectation.

## Definitions

An MDP is `(S, A, P, R, gamma)`; a trajectory is a sequence of states, actions, rewards.
The **discounted return** from time `t`:

```
G_t = sum_{k >= 0} gamma^k * r_{t+k+1},   with gamma in [0,1)
```

Because `gamma < 1` and rewards are bounded, `|G_t| <= r_max / (1 - gamma)`, so returns are
always finite — a fact used everywhere in the proofs.

## Bellman equations (exact statements)

For a fixed policy `pi`, the state-value and action-value functions obey:

```
V^pi(s) = sum_a pi(a|s) * sum_{s'} P(s'|s,a) * [ r + gamma * V^pi(s') ]
Q^pi(s,a) = sum_{s'} P(s'|s,a) * [ r + gamma * sum_{a'} pi(a'|s') * Q^pi(s',a') ]
```

For the optimal policy, the expectation over actions is replaced by a maximum:

```
V*(s) = max_a sum_{s'} P(s'|s,a) * [ r + gamma * V*(s') ]
Q*(s,a) = sum_{s'} P(s'|s,a) * [ r + gamma * max_{a'} Q*(s',a') ]
```

The optimality operator is a **contraction mapping** in the sup norm with modulus `gamma`;
with `gamma < 1` it has exactly one fixed point, and repeated application of the operator
converges to `V*` geometrically (error shrinks by at least gamma per sweep).

## Tabular TD and Q-learning

The temporal-difference error for state values is `delta = r + gamma * V(s') - V(s)`.
The off-policy Q-learning update after observing `(s, a, r, s')`:

```
Q(s,a) <- Q(s,a) + alpha * [ r + gamma * max_{a'} Q(s',a') - Q(s,a) ]
```

Its target mixes the bellman optimality form; if every `(s,a)` is visited infinitely often
and `alpha` decays per the Robbins-Monro sequence, `Q` converges to `Q*`.

## Bandit special case

Arms have fixed means `mu_i`; epsilon-greedy selects the argmax of current estimates with
probability `1 - epsilon` and a uniformly random arm otherwise. Our snippet uses a
fixed-step exponential-averaging update (alpha = 0.5), which is a common bookkeeping choice
rather than the exact sample mean.

## Quantities used in the exercises

- `V*` of the tiny grid world: one-step states get exactly the entry reward 1.0; the
  two-step-away start cell gets `gamma * 1.0 = 0.9`.
- Greedy-policy tie-break: choose the action that appears first in the action list.
