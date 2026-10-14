# Feature Engineering - Architecture

## Transform pipeline

```text
raw columns --> ENCODE (one-hot/ordinal/target, fitted vocab)
   --> TRANSFORM (log/Box-Cox on skew) --> INTERACT (products)
   --> SCALE (frozen train constants) --> model-ready matrix
fit path: TRAIN ONLY --> parameter store --> apply path reuses it
```

## Component responsibilities

- **Encoder:** owns vocabulary (level -> index) fitted on train; maps
  unknowns to a fixed fallback. One-hot emits sparse-friendly vectors.
- **Transformer:** owns shift/log decisions for skew; records the shift so
  apply repeats it exactly (log(x + c) with train's c).
- **Interactor:** owns the product list (area x rooms); pure per-row
  arithmetic, no fitted state, but runs before scaling by design.
- **Scaler:** owns frozen (min/max, mean/sd, median/IQR); apply is
  division by construction, never refit.
- **Parameter store:** the single record of every fitted constant with the
  train slice identity (rows, hash). Validation/test paths read, never
  write.

## JDK mapping

- Vocabularies: `List` index lookup (`indexOf`) at lab scale; `HashMap`
  level-to-index beyond dozens of levels.
- One-hot rows: `int[]` unit vectors printed via `Arrays.toString`.
- Scaling: primitive double arithmetic; `Math.log` for transforms.
- Parameter passing: small holder objects/records carrying (mean, sd) from
  fit to apply - never recomputed downstream.

## Invariants

1. No component reads test data during fit; the split precedes all fitting.
2. Apply uses byte-identical constants to fit (same object, not recompute).
3. Unknown levels and out-of-range values map to declared fallbacks, loudly.
4. Column order and widths are fixed at fit; apply cannot add columns.
