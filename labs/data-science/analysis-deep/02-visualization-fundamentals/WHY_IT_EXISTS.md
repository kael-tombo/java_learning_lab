# Visualization Fundamentals - Why It Exists

## Tables do not show shape

A column of numbers and its mean (3.6 here) cannot report a gap, a tail, or
an outlier. Human vision detects peaks, gaps, clusters, and strays in
milliseconds; visualization exists to route data through that channel before
modelling choices harden. Anscombe's quartet is the permanent exhibit: four
datasets, one summary table, four different realities.

## Binning makes the continuous countable

Continuous values have no natural frequencies until binned. The histogram is
the device that turns "a spread of numbers" into countable, comparable
buckets - and the bin width is the resolution knob. This lab computes bins by
hand so the knob's power (width 2 shows the 9 as a stray; width 10 would not)
is felt, not just stated.

## Scales are rhetoric

Every axis choice persuades: truncation dramatizes, dual axes fabricate
relationships, hidden bin edges gerrymander. Scale literacy exists because
the same numbers can tell opposite stories depending on framing, and readers
- including future you - need defenses.

## Overplotting is a big-data certainty

Past a few thousand points, every scatter plot saturates. Alpha, jitter, and
binning exist because "just plot it" stops working at scale; the binned-mean
trend (3.0 to 8.0 across four cells) is the scalable survivor of the scatter
plot idea.

## The alternative is table-gazing

Analysts handed raw columns routinely report the mean (3.6) and move on -
missing the gap, the stray 9, and the skew the mean/median gap (3.6 vs 3.0)
already hinted at. Visualization exists because tables answer "how much"
while only shapes answer "what kind": cluster, trend, gap, or contamination.
No downstream method recovers a shape question the analyst never asked.

Skip the plot and the model chooses blindly; draw first and the data gets a vote.
