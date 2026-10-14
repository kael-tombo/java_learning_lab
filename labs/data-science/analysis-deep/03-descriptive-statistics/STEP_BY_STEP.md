# Descriptive Statistics - Worked Example

## Data: {3, 7, 7, 9, 12, 15, 21}

## Step 1 - Mean

Sum: 3+7+7+9+12+15+21 = 74. n = 7. Mean = 74/7 = 10.571428571428571
(verify: 7 x 10.571428571428571 = 74.0).

## Step 2 - Median and mode

Sorted: [3, 7, 7, 9, 12, 15, 21]. Middle (4th of 7): 9.0. Tally: 7 appears
twice, all others once: mode 7.0, count 2. Mean (10.57) > median (9.0):
right-skew signal number one.

## Step 3 - Sum of squares

Deviations from 10.571428571428571: -7.571, -3.571, -3.571, -1.571, 1.429,
4.429, 10.429 (rounded). Squares sum to ss = 215.71428571428572.
Population variance 215.714/7 = 30.816326530612248, sd 5.551245493635842.
Sample variance 215.714/6 = 35.952380952380956, sd 5.99603043290984.

## Step 4 - Quartiles

Type-7 positions on n = 7: Q1 at h = 2.5 (average of 2nd and 3rd values:
(7+7)/2 = 7.0); median at h = 4 (9.0); Q3 at h = 5.5 (average of 5th and
6th: (12+15)/2 = 13.5). IQR = 6.5.

## Step 5 - Skew, kurtosis

Third central moment / sd^3 = 0.5802988304934447 (right tail). Fourth-moment
ratio minus 3 = -0.6180158764966452 (mild tails). Consistent with steps 2
and 4: everything points modestly right.

## Step 6 - Correlation demo

xs 1..5, ys {2,4,5,8,10}: s_xy = 7.6+1.8+0+2.2+8.4 = 20.0, cov = 5.0,
r = 20/sqrt(10 x 40.8) = 0.9901475429766744.

## Cross-checks that must hold

- Mean x n reconstructs the sum: 10.571428571428571 x 7 = 74.0.
- popVar x 7 = sampVar x 6 = ss = 215.71428571428572.
- r^2 = 0.9804: about 98% of y's sample variance lies along the linear fit.
- Median 9.0 sits inside [Q1, Q3] = [7.0, 13.5]; a median outside its own
  quartiles would prove a quartile bug.
