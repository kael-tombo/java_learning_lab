# Reinforcement Learning — Theory

Reinforcement learning (RL) is the setting where an agent interacts with an environment
over time, observing states and receiving scalar rewards, with the goal of choosing
actions that maximize long-term return rather than immediate reward. The standard formal
model is the Markov Decision Process (MDP), a five-tuple `(S, A, P, R, gamma)`.

## Core definitions

- **State / action**: `s in S` describes the situation the agent perceives; `a in A` is a
  choice available to the agent.
- **Transition model**: `P(s'|s,a)` gives the probability of landing in `s'` after taking
  action `a` in state `s`. We call an MDP deterministic if every probability is 0 or 1.
- **Reward function**: `r` assigns a real number to each step, rewarding or penalizing the
  transition itself.
- **Discount factor**: `gamma in [0,1)` scales future rewards; a discounted return is the
  sum of rewards multiplied by `gamma` raised to their time offset.

## Value functions and policies

A policy `pi` maps states to actions (or distributions over actions). The value of a state
under a policy is the expected return when starting there and following `pi` forever; the
action-value function `Q^pi(s,a)` adds the condition that the first action is `a`.

The central result — the Bellman equations — says that these expectations satisfy
recursions: the value of a state is the (gamma-discounted, expectation-weighted) value of
its successors plus the immediate reward. If a recursion is used with the *best* successor
value, it becomes the Bellman optimality equation, whose fixed point `V*` is the value of
the best possible policy.

## Dynamic programming methods

When `P` and `r` are known, two classic algorithms solve the MDP:

- **Policy iteration** alternates between evaluating the current policy (fixing it, solving
  the linear Bellman equations) and improving it greedily against that evaluation.
- **Value iteration** instead repeatedly applies the optimality Bellman operator until
  values stabilize. Because the Bellman operator is a contraction when `gamma < 1`, the
  process converges to a unique fixed point — this is a standard analysis result, not a
  heuristic.

## Learning without a model

When transitions are unknown, `Q-learning` bootstrap-updates action values from observed
transitions and stays off-policy because its target uses `max_a Q(s', a)`, not the action
actually taken. Convergence of tabular Q-learning requires sufficient exploration of every
state-action pair and a learning rate satisfying the usual Robbins-Monro conditions.

## Exploration

Two canonical recipes: epsilon-greedy (mostly greedy, occasionally random) and optimism
under uncertainty (initialize values above what reality can deliver, so untried actions
look attractive). Our exercises quantify both on small, seeded problems.

## What this lab covers

Files in this folder implement a tiny grid world solved by sweeps of the Bellman
optimality operator, an epsilon-greedy bandit, and treat policy-gradient math at
conceptual level only.
