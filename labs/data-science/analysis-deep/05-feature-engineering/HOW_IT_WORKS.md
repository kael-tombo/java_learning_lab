# Feature Engineering - How It Works

## One-hot encoding pass

Fix the vocabulary order once ([red, green, blue]); each value maps to the
unit vector at its index (blue -> [0,0,1]). Unknown levels at transform time
map to all-zeros (or an explicit unknown column) - never refit the
vocabulary on test data, which would shift every column index.

## Scaling pass

Fit phase on train: record min/max, or mean/sd, or median/IQR. Apply phase:
pure arithmetic per value with the frozen constants. The demo fits on
{10..50} and would apply the same constants to any newcomer (60 becomes
min-max 1.25 - out of range, correctly signalling extrapolation rather than
silently rescaling).

## Train-only discipline, mechanically

Split first. Compute train mean 25.0 and sd 11.180339887498949 from the four
train values only. Transform test 25 -> 0.0, test 100 -> 6.7082039324993685.
The z of 6.71 correctly screams "far from train" - a leaky fit (mean 37.5)
would mute it to ~4.9 and hide the outlier. Leakage dampens the very alarms
scaling is meant to raise.

## Interaction and log construction

Per row, emit the raw pair plus area x rooms plus log(area): (50,2) becomes
(50, 2, 100, 3.912023005428146). Log compresses the 50-to-120 range (2.4x)
into 3.91-to-4.79 (1.2x), taming leverage; the product lets a linear model
charge extra for big houses with many rooms beyond the sum of parts.

## Pipeline assembly order

Encode categoricals, transform skew, add interactions, scale numerics -
with fit/apply separation enforced at every stage. Order matters because
interactions of unscaled raw magnitudes can overflow or dominate before
scaling gets its turn.

## Failure preview

Refit the vocabulary on test and column indices shift silently. Interact
after scaling and the product's meaning changes under you. Fit target means
on full labels and validation applauds a memorization act. Each ordering and
separation rule above exists because its violation ships regularly, looks
correct locally, and fails on contact with new data.
