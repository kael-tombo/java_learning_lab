# Math Foundation: Open-Addressing Costs

## Load factor

α = (live entries) / capacity — or with tombstones, α_eff = (size +
tombstones) / n, which is what governs probes. All formulas below use the
effective α.

## Expected probes (linear probing, uniform hashing)

- Successful search: ≈ ½(1 + 1/(1−α)).
- Unsuccessful search / insert: ≈ ½(1 + 1/(1−α)²).

Worked values:

| α | hit | miss |
|---|---|---|
| 0.5 | ½(1+2) = 1.5 | ½(1+4) = 2.5 |
| 0.7 | ½(1+3.33) ≈ 2.2 | ½(1+11.1) ≈ 6.1 |
| 0.9 | ½(1+10) = 5.5 | ½(1+100) = 50.5 |

Miss cost squares — inserts (which always probe to EMPTY) feel the knee
first. This is the quantitative case for capping at ~0.7.

## Why the formulas blow up

At load α, the chance a random slot is occupied is α; a probe run of
length L needs L consecutive occupied slots (≈ α^L ignoring clustering —
clustering makes reality *worse*). Expected run length ~ 1/(1−α); miss
probes integrate over run lengths, hence the square.

## Amortized resize

Doubling at cap c: total rehash work Σ n_i = n + n/2 + ... < 2n across the
table's life → O(1) amortized per insert. Same series as ArrayList growth;
each unit is hash-and-place instead of `arraycopy`.

## Spread math

`h ^ (h >>> 16)` folds the top 16 bits into the bottom 16. With mask
`n−1` keeping the bottom b bits, unspread entropy in bits ≥ b is
otherwise discarded — folding recovers it with one XOR + one shift.
