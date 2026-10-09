# Visual Guide: Multivariate Statistics

## Scatter cloud with regression line and correlation
```
   y
   5 │           •  •           r = 0.775
     │        •                 ŷ = 2.2 + 0.6x
   4 │     •     • •            R² = 0.60
     │  •                       passes through (x̄, ȳ) = (3, 4)
   3 │
     │
   2 │•
     └──────────────────── x
      1  2  3  4  5
```

## Correlation as ellipse orientation (bivariate normal)
```
   ρ = 0            ρ = 0.6          ρ ≈ 0.95
     ╭───╮           ╱ ╲              ╱
     │   │         ╱     ╲          ╱
     ╰───╯       ╱         ╲      ╱      thin diagonal cigar
                ╱           ╲   ╱
   axis-aligned             nearly degenerate line
   contours = independent   contour major axis ≈ direction (1,1)
```

## PCA: rotate the cloud to its principal axes
```
   before rotation          after rotation (PC1, PC2)
   y │      •••••            PC2 │  • •
     │    ••••••••               │ • • •        total variance = trace(Σ)
     │  ••••••••                 │  • •          = λ1 + λ2 = 3 + 1 = 4
     └──────────── x          ───┴────── PC1
        diagonal cloud           PC1 carries 75% of the variance
```

## Mahalanobis vs Euclidean (ρ = 0.6)
```
        (1.5, 1.5)  Euclidean 2.12 → Mahalanobis 1.68   along the correlation: unsurprising
        (2, −2)     Euclidean 2.83 → Mahalanobis 4.47   against it: jointly extreme
        formula: d² = (x−μ)ᵀ Σ⁻¹ (x−μ),  Σ = [[1, .6], [.6, 1]]
```

## Confounding: marginal vs partial correlation
```
   temperature ──▶ ice cream sales
        │                    ▲
        └──────▶ drowning ◀──┘

   r(sales, drowning) ≈ strong   ← both track temperature
   r(sales, drowning | temp) ≈ 0 ← condition it out (Yule 1897, Simpson 1951)
```
