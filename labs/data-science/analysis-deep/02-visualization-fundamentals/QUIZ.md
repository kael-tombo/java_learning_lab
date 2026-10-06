# Visualization Fundamentals - Quiz

## Question 1
Why is the y-axis truncated at 90% misleading for a 0–100 scale metric?
A) It isn't
B) Small true differences are visually exaggerated
C) It changes the color
D) It hides the legend

**Answer**: B

## Question 2
Which encoding is best for showing magnitude of a continuous variable?
A) Color hue
B) Position along a common baseline (bar length)
C) Shape
D) Texture

**Answer**: B

## Question 3
Why do pie charts make it hard to compare category sizes?
A) Colors are hard to read
B) Humans judge angles less accurately than lengths along a baseline
C) They hide outliers
D) They require too much space

**Answer**: B

## Question 4
What does a log-transformed axis do to an exponential trend?
A) Makes it steeper
B) Turns it into roughly a straight line, revealing growth rate
C) Hides it
D) Inverts it

**Answer**: B

## Question 5
Why facet (small multiples) instead of one overloaded plot?
A) It uses more colors
B) Side-by-side aligned panels let you compare many series without occlusion
C) It is slower
D) It requires more data

**Answer**: B

## Question 6
When is a density plot preferred over a histogram?
A) Always
B) When comparing smooth distributions without bin-size artifacts
C) When you need exact counts
D) When data is categorical

**Answer**: B — note density still depends on bandwidth choice.

## Question 7
Why add confidence intervals to a bar chart of means?
A) For aesthetics
B) To communicate uncertainty rather than over-interpreting small differences
C) To speed reading
D) To fix skew

**Answer**: B

## Question 8
What does a QQ-plot test visually?
A) Linearity
B) Whether a sample's quantiles match a theoretical distribution (often normal)
C) Correlation
D) Outliers only

**Answer**: B

## Question 9
Why is a rainbow/jet colormap discouraged?
A) It wastes ink
B) It is not perceptually uniform — equal data steps map to unequal perceived steps
C) It prints poorly
D) It hides zero

**Answer**: B — prefer viridis; red-green problematic for colorblind readers.

## Question 10
Why is "dual y-axis" often criticized?
A) It is hard to read on mobile
B) Two independent scales invite spurious correlation claims
C) It requires lines
D) It doubles rendering time

**Answer**: B

## Question 11
What is a Anscombe's quartet lesson for visualization?
A) Always drop outliers
B) Same summary statistics can hide radically different shapes — always plot
C) Means are robust
D) Linear regression always fits

**Answer**: B

## Question 12
Why use a log-log scatter for power laws?
A) To zoom in
B) Power laws appear as straight lines with slope = exponent
C) To hide outliers
D) To color categories

**Answer**: B

## Question 13
When should you standardize before plotting multiple series on one axis?
A) Always
B) When series have different units/scales — plot z-scores or indexed values (base = 100)
C) Never
D) Only for time series

**Answer**: B

## Question 14
Why are zero baselines required for bar charts but not line charts?
A) Bars encode by length from the baseline; truncating distorts. Lines encode by position — truncation shifts, doesn't rescale
B) Bars need more ink
C) Lines can't show zero
D) It is just a convention

**Answer**: A

## Question 15
What is the risk of a chart that shows a single aggregate?
A) Too simple
B) Simpson's paradox / aggregation bias — the aggregate trend can reverse within subgroups
C) It is hard to read
D) It hides the axis

**Answer**: B
