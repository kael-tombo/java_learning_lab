# Visualization Fundamentals - Interview Questions

## Q1. Your scatter plot is a solid blob. What do you do?

A: Assume density is hidden: apply alpha blending, then bin into cells with
counts or binned means (as in this lab: four cells recovered a clean
3.0-to-8.0 trend). Report cell n beside each mean since sparse cells are
noisy.

## Q2. A stakeholder wants the y-axis to start at 5.5 "to show the growth".
How do you respond?

A: Show both versions: truncated dramatizes a 5% gap (5.8 vs 6.1) into a
headline. Standard is zero baseline for bars; if change matters, plot the
change (differences or indexed values) explicitly instead of cropping.

## Q3. Explain Anscombe's quartet and why it matters for modelling.

A: Four sets share mean x 9, mean y 7.5, r 0.816, yet are linear, curved,
outlier-driven, and degenerate. A regression fit without plotting describes
none of them correctly. Plot-first is not aesthetics; it selects the model.

## Q4. How do you pick histogram bin width?

A: There is no neutral width: narrow shows noise, wide hides strays (the 9
vanishes at width 10). Default to a rule (e.g. Sturges or Freedman-Diaconis
as a start), then try a second width and keep only features that persist.

## Q5. Pie chart or stacked bar for five market shares?

A: Stacked bar (or plain bars): position/length judgments beat angle/area
(Cleveland and McGill 1984), and small-share differences stay readable.

## Q6. How do you visualize a million points on the JDK without libraries?

A: Stream into a fixed grid of counters (2D histogram), then print densities
as text or scale symbols by count. O(n) time, O(cells) memory; exact points
are never stored.

## Q7. What is wrong with this chart: dual axes, no zero, 3D bars?

A: Three independent distortions: crossings are scale artifacts, bar lengths
misstate values, perspective distorts further. Redraw as two zero-based
panels with stated bins.

## Q8. How do you make a chart reproducible in code review?

A: State edges, counts, and n in the output itself (as the lab's text charts
do), fix the bin width in code, and test rendered strings byte-for-byte.
