# Lab 02 - Visualization Fundamentals

Choosing the right chart, scaling axes honestly, and defeating overplotting -
computed in plain Java and printed as text, no graphics libraries.

## What you will learn

- Match chart to variable type: bars for categories, histograms for
  continuous distributions, scatter for pairs, lines for time.
- Read and set histogram bins; see how bin width changes the story.
- Spot dishonest scales: truncated y-axes, dual axes, area-as-length.
- State the Anscombe lesson: identical means can hide flat, trending, and
  outlier-driven shapes.
- Tame overplotting with transparency, jitter, and binned means.

## Working data

- `{1, 2, 2, 3, 3, 3, 4, 4, 5, 9}` binned at width 2 from 0.
- Sales labels `{books x3, games x3, food x2}` for bar counts.
- Twelve `(x, y)` points binned into width-2 cells with cell means.
- Three 5-point series, each with mean exactly 6.0 but sds 0.0, 3.16, 5.66.

## Build and run (plain JDK only)

```text
javac --release 21 -encoding UTF-8 VizHistogram.java
java VizHistogram
```

Only `java.util` and `java.lang.Math` are used. Charts are text (`#` bars)
so every plot is diffable and checkable by hand.

## Suggested path

THEORY.md for chart selection and scale rules, CODE_DEEP_DIVE.md for the
three verified text-chart programs, STEP_BY_STEP.md for the hand-worked bin
counts, then EXERCISES.md. Keep COMMON_MISTAKES.md open while you work: the
truncated-axis and bin-width traps live there.

## What done looks like

You can bin any small dataset by hand, defend a bin width in one sentence,
spot a truncated axis instantly, and reproduce the Anscombe moral (shared
mean 6.0, three shapes) from memory when someone says "just average it".
