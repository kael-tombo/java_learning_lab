# Visualization Fundamentals - Common Mistakes

## 1. Truncating the y-axis on bars

Starting at 5.5 makes 5.8 vs 6.1 look like a landslide. Bars encode by
length from zero; cropped bars lie while staying "accurate".

## 2. Letting the library pick bins silently

Default bins merge the lone 9 into the bulk or shatter the peak into noise.
Always set and state min, width, and count - then try a second width.

## 3. Dropping empty bins from output

Omitting [6,8): 0 hides the gap between cluster and stray. Render zeros;
absence of observations is information.

## 4. Comparing percents with different denominators

"37.5% books" from n = 8 vs n = 8,000 are different evidence. Print 3/8
beside every proportion.

## 5. Dual-axis storytelling

Two independent scales let any pair of series "cross" on demand. Split into
panels or index to a common baseline instead.

## 6. Reading causation off a binned trend

Cell means 3.0 to 8.0 trace association of y with x, not proof x drives y.
A lurking third variable survives binning untouched.

## 7. Jitter overdose

Amplitudes larger than the measurement grain fabricate spread. Cap jitter
below the smallest meaningful difference and disclose it.

## 8. Pie slices for close contests

A 3-point share gap vanishes in angles but survives in aligned bar lengths.
Reserve pies for 2-3 part wholes nobody must compare precisely.

## 9. Forgetting edge rules

Values exactly on edges (2.0, 4.0) need a stated convention; silent
floor-vs-round choices move points between bins irreproducibly.

## 10. Summarizing without plotting

Reporting mean 6.0 for series c (-2,6,6,6,14) as "central tendency around 6"
without noting the outlier pair is the exact failure Anscombe exhibited.
