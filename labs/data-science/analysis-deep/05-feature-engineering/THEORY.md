# Feature Engineering - Theory

## 1. Categorical encodings

- **One-hot:** one binary column per level (red -> [1,0,0]). Claims no order
  and no distance between levels. Cost: one column per level; rare levels
  get near-constant columns.
- **Ordinal:** integers 0,1,2,... Valid only for truly ordered levels
  (small < medium < large); applied to nominal colors it invents an order
  the model will exploit.
- **Target encoding:** replace each level by its mean target (smoothed
  toward the global mean). Powerful and dangerous: fitted on labels, it
  leaks the answer into the question unless computed inside train folds
  only, never on full data.
- **Hashing trick:** hash level names into a fixed-width vector. Bounded
  memory for open vocabularies (URLs, tokens); collisions merge levels at
  random, so it suits linear models with many weak features, not exact
  identity needs.

## 2. Scaling

- **Min-max:** (x - min)/(max - min) into [0,1]. Needs known bounds; one new
  extreme breaks the range. Demo: {10..50} maps to quarters exactly.
- **z-score:** (x - mean)/sd, zero center, unit spread. Assumes roughly
  symmetric data; outliers inflate sd and compress everything else.
- **Robust:** (x - median)/IQR. Immune to tails; the demo gives clean
  [-1.0, -0.5, 0, 0.5, 1.0]. Default for skewed money-like columns.
- Scale for the consumer: regularized linear models and gradient methods
  need comparable magnitudes; trees do not care.

## 3. Transforms and interactions

- **Log:** compresses right skew (areas 50/80/120 become 3.91/4.38/4.79);
  requires positive values (shift or filter first). Box-Cox generalizes the
  power choice with a fitted exponent.
- **Interactions:** products like area x rooms (100/240/480) let linear
  models price combinations, not just parts. Create sparingly: each product
  spends degrees of freedom and multiplies multicollinearity.

## 4. The leakage rule

Fit (means, sds, medians, target means, vocabularies) on train only; apply
the frozen transform to validation, test, and each CV fold's held-out part.
Fitting on all data (leaky mean 37.5 vs train mean 25.0) lets test
information shape training features - optimism masquerading as accuracy.
