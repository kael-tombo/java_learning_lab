# Lab 03 - Descriptive Statistics

Summarizing columns honestly: center, spread, shape, and association -
every number hand-verifiable on one seven-element dataset.

## What you will learn

- Compute mean, median, and mode, and say which the skew recommends.
- Distinguish population variance (divide by n) from sample variance
  (divide by n - 1, Bessel's correction) and defend the choice.
- Read moment skew and excess kurtosis as shape diagnostics.
- Report quartiles and IQR alongside the sd for skewed data.
- Compute sample covariance and Pearson's r from the defining sums.

## Working data

One seven-point column `{3, 7, 7, 9, 12, 15, 21}` used throughout:
sum 74, mean 10.571428571428571, median 9.0, mode 7.0 (twice). Population sd
5.551245493635842, sample sd 5.99603043290984. Skew 0.5802988304934447,
excess kurtosis -0.6180158764966452, IQR 6.5. Association demo: xs 1..5 vs
ys {2,4,5,8,10} gives r = 0.9901475429766744.

## Build and run (plain JDK only)

```text
javac --release 21 -encoding UTF-8 DescCentral.java
java DescCentral
```

Only `java.util` (`Arrays`, `Map`) and `java.lang.Math` are used. No
statistics libraries: every formula is written out so nothing hides.

## Suggested path

THEORY.md for definitions and the n vs n-1 rule, MATH_FOUNDATION.md for the
derivations (including Bessel), CODE_DEEP_DIVE.md for the three verified
programs, STEP_BY_STEP.md to check each number by hand, then EXERCISES.md.

## Pocket dataset

Memorize the seven values and their headlines (mean 10.57, median 9.0, sd
~6.0, IQR 6.5, r-demo 0.99). Any new summary routine you write gets tested
against these first: if it cannot reproduce them, it is wrong, not novel.
