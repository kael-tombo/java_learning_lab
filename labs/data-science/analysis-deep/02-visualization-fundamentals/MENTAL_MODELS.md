# Visualization Fundamentals - Mental Models

## 1. The chart is an argument

Every chart claims something ("sales are flat", "the tail is long"). Ask
what claim each choice serves: the bin width, the axis start, the aspect.
Honest charts make the claim checkable by printing counts and scales.

## 2. Bins are buckets, width is opinion

Narrow bins show noise; wide bins hide shape. There is no neutral width -
the lab's width-2 histogram shows a peak plus an outlier, while width-5
would merge the 9 into the bulk. Report the width and try a second one.

## 3. Summaries are lossy compression

Mean 6.0 compresses five numbers into one and deletes shape - flat, slope,
and outlier trio all compress identically. Plot first, summarize second,
and never let the compressed form travel without the picture.

## 4. Empty space is data

The zero-count [6,8) bin and the whitespace around the lone 9 carry the
finding (a gap, then a stray). Charts that auto-zoom to the bulk delete the
most newsworthy region. Draw the emptiness.

## 5. Overplotting hides in plain sight

A solid blob can be 1,000 or 1,000,000 points. Assume density is lying until
alpha, jitter, or binning proves otherwise; the binned means (3.0 to 8.0
across four cells) are the honest version of a blob with a trend.

## 6. Proportions need denominators

"3/8 books" is a finding; "37.5%" alone is a rumor. Always carry n beside
any percent, because the same percent from n = 8 and n = 8,000 means
completely different things.

## 7. The lens model

A histogram is a lens, not a photograph: width sets magnification, edges set
framing. Like microscope objectives, no single magnification shows
everything; the honest microscopist reports the objective (width 2) and
checks the finding under a second one (width 5).
