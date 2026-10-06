# Flashcards — Combinatorial Algorithms

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Pascal rule | C(n,k) = C(n-1,k-1) + C(n-1,k) |
| 2 | C(n,k) definition | k-subsets of an n-set |
| 3 | Catalan closed form | C_n = (1/(n+1))·C(2n,n) |
| 4 | Catalan recurrence | C_{n+1} = Σ_{i=0}^{n} C_i C_{n-i} |
| 5 | C_0 seed | C_0 = 1 |
| 6 | C_4 value | 14 |
| 7 | Recognising Catalan | balanced structures, non-crossing, binary trees |
| 8 | Inclusion–exclusion | |∩Aᵢᶜ| = Σ (-1)^|S| |∩_{i∈S} Aᵢ| |
| 9 | Derangements D_n | n! Σ_{k=0}^{n} (-1)^k/k! |
| 10 | D_n limit density | 1/e |
| 11 | Stirling second kind S(n,k) | partitions of an n-set into k non-empty blocks |
| 12 | S(n,k) recurrence | S(n,k) = k·S(n-1,k) + S(n-1,k-1) |
| 13 | Onto maps to k boxes | k!·S(n,k) |
| 14 | Stirling first kind c(n,k) | permutations of n with k cycles |
| 15 | c(n,k) recurrence | c(n,k) = (n-1)c(n-1,k) + c(n-1,k-1) |
| 16 | Meet in the middle | enumerate halves Θ(2^{n/2}), combine by sort/search |
| 17 | Meet-in-the-middle memory | Θ(2^{n/2}) |
| 18 | Submask loop | for (s=M; ; s=(s-1)&M) |
| 19 | Total submask work over all masks | Θ(3^k) |
| 20 | C(8,3) | 56 |
| 21 | Overflow of C(60,30) | ≈ 1.18·10¹⁷ — needs long/BigInteger |
| 22 | Factorial ratio formula | n!/(k!(n-k)!) |
| 23 | Why not divide factorials directly | intermediate overflow and division-order integrality |
| 24 | Pascal space optimisation | keep one row, update right-to-left |
| 25 | Catalan objects | parens, binary trees, non-crossing matchings |
| 26 | Non-crossing matching count | C_n for 2n points on a circle |
| 27 | Inclusion–exclusion practicality | k ≤ ~20, terms simplify |
| 28 | Derangement of 4 | 9 |
| 29 | Onto maps 5→3 | 150 |
| 30 | S(5,3) | 25 |
| 31 | S(n,1) | 1 |
| 32 | S(n,n) | 1 |
| 33 | S(n,2) | 2^(n-1) - 1 |
| 34 | c(n,1) | (n-1)! |
| 35 | c(n,n) | 1 |
| 36 | Binomial symmetry | C(n,k) = C(n,n-k) |
| 37 | Sum of row n | Σ C(n,k) = 2^n |
| 38 | Vandermonde | Σ C(r,k)C(s,n-k) = C(r+s,n) |
| 39 | Hockey-stick | Σ_{i=r}^{n} C(i,r) = C(n+1,r+1) |
| 40 | Pascal row n time | Θ(n²) |
| 41 | Meet-in-middle for subset sum | n≈40 splits into two 20-halves |
| 42 | Combine step of MITM | sort one half, binary-search each of the other |
| 43 | Submask enumeration count for mask with j bits | 2^j |
| 44 | Mask 0b1011 submask count | 8 |
| 45 | Why Θ(3^k) submask total | each bit is in, out-but-in-mask, or not-in-mask |
| 46 | k≈20 subset DP limit | 2^20 ≈ 10⁶ states |
| 47 | Inclusion–exclusion terms | 2^k subsets of properties |
| 48 | Negative terms in IE | odd-sized subsets subtracted, even added |
| 49 | Binomial coefficient parity | C(2^r, k) is even for 0<k<2^r |
| 50 | Lucas theorem | C(n,k) mod p via base-p digits, no overflow |
| 51 | Ballot count | (1/(n+1))C(2n,n) |
| 52 | Catalan generating function | C(x) = (1 - sqrt(1-4x)) / (2x) |
| 53 | Binary trees with n internals | C_n |
| 54 | Valid parens of 2n chars | C_n |
