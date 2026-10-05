# MINI_PROJECT — Information Theory: Entropy & Coding Lab
> Implement + encode + measure. ~3 hours.

## Goal
Build a CLI computing Shannon entropy of a text dataset, building Huffman codes,
comparing compressed sizes to entropy bound, and computing mutual information between two columns.

## Build Steps
1. `Entropy.java`: H(X) over a symbol alphabet; report bits/symbol.
2. `Huffman.java`: build code tree, emit code lengths; verify Kraft inequality Σ 2^(-len) ≤ 1.
3. `Bound.java`: compare average code length to H(X); ratio → "redundancy".
4. `MI.java`: I(X;Y) from a joint frequency table (two CSV columns).
5. Driver: run on alice.txt (or any text); print H, Huffman length, redundancy, MI pairs.

## Sample Output
```
H(X)=4.19 bits/symbol (26 letters + space)
Huffman avg length=4.29 → redundancy 0.10
I(day; weather)=0.62 bits
Kraft: Σ 2^-len = 0.9998 ✓
```

## Benchmark Table (fill)
| corpus | bytes | H(X) bits/sym | Huffman avg len | redundancy |
|--------|-------|---------------|-----------------|------------|
| small  | | | | |
| medium | | | | |
| large  | | | | |

## Acceptance
- [ ] Huffman never exceeds H(X)+1 average length (theorem sanity check).
- [ ] Kraft inequality holds for every code produced.
- [ ] MI(X;X) == H(X) verified.

## Extensions
- Arithmetic coding approximation demo.
- Cross-entropy of a uniform model vs true distribution.
