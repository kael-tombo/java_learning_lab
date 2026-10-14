# Visualization Fundamentals - Reflection

## Prompts

1. The width-2 histogram shows the 9 as a stray; width-5 absorbs it. Which
   width is "true", and what experiment decides?
2. Series c (-2,6,6,6,14) has mean 6.0 and the largest sd (5.66). A colleague
   reports "highest variance group". What two sentences correct the record?
3. Your binned means rise 3.0 to 8.0 but end cells have n = 2. How do you
   present this without overstating?
4. A dashboard request demands dual axes "to save space". Draft the refusal
   with the alternative you will build instead.

## Self-check sketches

1. Neither width is true; width is resolution. Persisting features across
   widths (the [2,4) peak) are real; width-dependent ones (stray vs member)
   get flagged for domain review, not decided by the chart.
2. "The sd is large because of one low and one high point, not broad spread;
   the plot shows four 6s plus an outlier pair, so variance here means
   contamination, not diversity."
3. Show n beside each mean, widen end-cell uncertainty (s/sqrt(2) is large),
   and say "suggestive rise, ends uncertain" rather than claiming monotone.
4. "Dual axes let crossings move with rescaling, so the chart can show
   anything; I will build two aligned zero-based panels (or an indexed
   comparison) in the same space."

## Habits worth keeping

- Fix and print edges, baselines, and n before reading any shape.
- Try a second bin width whenever a finding depends on the first.
- Keep one Anscombe-style example (the mean-6.0 trio) ready for any debate
  about "just give me the average".

## One more prompt

5. A colleague compresses series c to "mean 6.0, sd 5.66" in a slide with no
plot. Rewrite the slide's two lines so a reader grasps flat-plus-outliers
without seeing the graph. (Sketch: "four of five values equal 6; one low
(-2) and one high (14) drive all the spread - see strip plot.")
