# Federated Learning — Mathematical Foundation

## FedAvg, the canonical aggregation (weighted-mean steps)

With clients `C_1..C_N` holding `n_i` examples each and (optionally) local training
before aggregation, the classical round is:

```
1. server sends w_t to a subset S_t of clients
2. each client i runs local SGD on its own data, producing w_{t+1}^i
3. server sets  w_{t+1} = sum_{i in S_t} (n_i / sum_j n_j) * w_{t+1}^i
```

Weights proportional to data size are the canonical choice; uniform
`(1/|S_t|)` weighting is the naive alternative. In our toy snippets, the "local
training" step is replaced by a single fixed gradient vector per client
(no local steps), so the update rule reduces to weighted-update mathematics only — a
statement about aggregation, not about local optimization.

## One worked round, hand numbers

Clients with gradients `g_1 = [0.2, -0.1]`, `g_2 = [0.4, 0.2]`, `g_3 = [-0.3, 0.5]`
and sizes `n = (1, 2, 3)`:

```
uniform:   mean = [0.1, 0.2]              (each client weight 1/3)
weighted:  (g_1 + 2*g_2 + 3*g_3) / 6 = [ (0.2+0.8-0.9)/6, (-0.1+0.4+1.5)/6 ] = [1/60, 0.3]
```

With `lr = 0.1` from `theta_0 = [0, 0]`, three rounds move the shared model to
`[-0.03, -0.06]` under uniform averaging and to `[-0.005, -0.09]` under size-weighted
averaging — two genuinely different trajectories from identical inputs (both printed and
independently re-verified).

## Client drift statement

Let each client take `k` local steps of size `eta` on its own gradient. Its local endpoint
after `k` steps is `theta_0 - k*eta*g_i`; straight-line drift grows linearly in `k*eta`
while the server-side average only linearly in `eta` per round. Our drift snippet shows
three clients' endpoints after `k = 3` steps versus ONE server-aggregated step, and the
gap between client-average and server-step is the textbook drift argument reduced to
vectors.

## Convergence claims kept honest

Even the classical analyses state round-robin/mood assumptions: identical local rates,
participating fraction fixed, bounded gradient norms, and convexity (or restricted
nonconvex stand-in conditions). Numbers above are the arithmetic facts of this toy; any
generalized statement ("FedAvg converges") must carry its assumptions or it is rhetoric.

## Vectors to be able to reproduce fast

- Round-1 weighted step from zero: `[-0.001667, -0.03]` (observed, verified).
- After 3 rounds uniform: `[-0.03, -0.06]`; weighted: `[-0.005, -0.09]` (observed,
  verified).
- Drift endpoints per client at `theta_0 = [2, 0], lr = 0.1, 3 local steps`:
  `[1.94, 0.03]`, `[1.88, -0.06]`, `[2.09, -0.15]` (observed, verified).
