# Feature Engineering - Why It Matters

## Encoding choices change conclusions

Ordinal-coding colors invents red < green < blue; a linear model then
charges per "color unit" - nonsense with real coefficients. One-hot costs
columns but tells no lies. Target encoding without folds tells the model
the answer in training and goes silent in production: the leaderboard (or
the audit) eventually collects, with interest.

## Scaling decides optimization fate

Unscaled areas beside raw room counts stall gradient descent or explode it;
standardized features converge where raw ones crawl. The demo numbers show
why: magnitudes 120 vs 4 differ 30x, z-units differ ~2x. Convergence,
regularization fairness (penalize comparable units), and distance metrics
(kNN, k-means) all ride on the scaling decision.

## Leakage is the top silent killer

Fitting the scaler on all data (mean 37.5) or target-encoding on full labels
manufactures optimism: validation scores describe a world where test data
already spoke. Shipped on that basis, models degrade on contact with truly
new data - the most expensive direction to discover a bug, after deployment.

## Transforms buy robustness cheaply

A log is one line that removes more outlier drama than pages of robust
loss functions: 50-to-120 becomes 3.91-to-4.79, and the fit stops
negotiating with the tail. Cheap, interpretable, reversible - the highest
return line in the preprocessing file.

## The 37.5 parable

Two means, 25.0 honest and 37.5 leaky, differ by one inclusion decision -
whether two test rows voted. That single decision moves an outlier alarm
from 6.71 to ~4.9 and inflates every validation score downstream. Whole
model programs have been funded on gaps no bigger than this one's optimism.
Small fit decisions, production-sized consequences.

## Encoding is a contract with the future

Vocabulary order, fallback behavior, scaling constants, shift values: each
is a promise apply-time keeps to fit-time. New levels, new extremes, new
ranges arrive constantly; contracts decide whether they become handled cases
or silent corruptions. Teams that version parameter stores keep promises;
teams that recompute "for convenience" keep incidents.
