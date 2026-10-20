# Graph Neural Networks — Mathematical Foundation

## Propagation rule formula (GCN, propagation form)

Given adjacency `A` with `A_ii = 0`, feature matrix `H`, layer weights `W`:

```
H_next = sigma( D_hat^{-1/2} * A_hat * D_hat^{-1/2} * H * W ),   A_hat = A + I
```

`D_hat` stores the self-inclusive degree of each node; `sigma` is elementwise. Row-by-row
for node `i` (using W = I for readability):

```
h_i_next = sigma( sum_{j in {i} u N(i)} A_ij * h_j / sqrt( d_i * d_j ) )
```

where `d_i` counts `{i} u N(i)`. On a cycle every `d_i = 3`, so the rule degenerates
gracefully: `h_i_next = (h_i + h_left + h_right) / 3` — exactly what the Java code does.

## Why the symmetric form beats naive row-normalization

Row normalization `D_hat^{-1} A_hat H` rescales each node's gathered message by its own
degree alone. Two problems: asymmetric (a hub influences a leaf strongly, but the reverse
dampens differently) and scale-sensitive (hub features inflate). The symmetric form's
entries `A_ij / sqrt(d_i d_j)` are symmetric by construction; the formal statement behind
it is that this preserves the spectral scaling property of the normalized Laplacian
(`D^{-1/2} A D^{-1/2}`-type operators underlie spectral graph filtering arguments).

## Message passing as set function learning

For invariance under node relabeling, aggregation must be a permutation-invariant set
operator (sum, mean, max all qualify). Message-passing nets generalize GCN as:

```
m_i = AGG({ h_j : j in N(i) }),   h_i_next = UPDATE(h_i, m_i)
```

Formal result often cited: sum-style families are, under counting assumptions, the most
expressive of the mean/max/max-set variants (up to injective-set reasoning); mean and max
lose multiplicity information — worth knowing before choosing an aggregate.

## Over-smoothing (the deep-stack failure)

Repeated averaging makes node vectors converge to each other; formally each layer acts
like a low-pass operator shrunk toward the dominant eigenvector of the normalized
adjacency. Practical consequence: 2-3 layers with residual/skip tricks is the usual
recipe rather than 10 plain layers.

## Quantities to be able to derive quickly

- Degrees with self-loops for a cycle (3 per node) and a 4-leaf star (hub 4, leaves 2).
- The two normalization modes' hand results for one round (verified numbers live in
  CODE_DEEP_DIVE).
- Two rounds on the cycle: `h1 = [4/3, 1, 5/3, 2]` and `h2 = [13/9, 4/3, 14/9, 5/3]`.
