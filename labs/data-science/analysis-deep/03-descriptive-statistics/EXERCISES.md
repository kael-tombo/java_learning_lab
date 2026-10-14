# Descriptive Statistics - Exercises

Verify each answer by running your code; expected values come from
verified reference runs.

## 1. Reproduce center

Rewrite mean/median/mode for `{3, 7, 7, 9, 12, 15, 21}` from scratch.
Expect sum 74.0, mean 10.571428571428571, median 9.0, mode 7.0 count 2.

## 2. Reproduce spread

Recompute ss and both normalizations. Expect ss 215.71428571428572,
popVar 30.816326530612248, sampVar 35.952380952380956, sds 5.551245493635842
and 5.99603043290984.

## 3. Shape drill

Implement moment skew and excess kurtosis on the same seven values. Expect
skew 0.5802988304934447, excess kurtosis -0.6180158764966452, quartiles
Q1 7.0 / median 9.0 / Q3 13.5, IQR 6.5.

## 4. Correlation from scratch

Recompute the xs 1..5 / ys {2,4,5,8,10} triple sums. Expect s_xy 20.0,
s_xx 10.0, s_yy 40.8, covSample 5.0, r 0.9901475429766744.

## 5. Outlier sensitivity

Replace 21 with 210 and recompute mean, median, sd, skew. Expect mean to
jump near 37.6 while median stays 9.0; skew explodes past 2. State which two
numbers a report should lead with now.

## 6. Constant-input guard

Feed `{5, 5, 5, 5}` to your correlation. Expect s_xx = s_yy = 0 and a
0/0 division: implement the zero-spread branch returning NaN with a clear
message instead of a number.

## 7. Rank correlation

Implement Spearman on `{1,2,3,4,5}` vs `{2,1,4,3,5}` by ranking then
Pearson on ranks. Expect r_s = 0.8. Compare with Pearson on raw values and
explain any gap in one sentence.

## 8. Standard error

From sample sd 5.99603043290984 and n = 7, compute se = s/sqrt(n) = 2.2666...
and the interval mean +/- 2 x se. State exactly what that interval does and
does not promise.
