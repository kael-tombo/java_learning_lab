# Visualization Fundamentals - Visual Guide

## The lab histogram (width 2 from 0)

```text
[0.0,2.0):  1 #
[2.0,4.0):  5 #####
[4.0,6.0):  3 ###
[6.0,8.0):  0
[8.0,10.0): 1 #
peak at [2,4), gap, then the lone 9
```

## Same mean, three shapes (all mean 6.0)

```text
a: 6 6 6 6 6        flat line ............
b: 2 4 6 8 10       steady slope  /
c: -2 6 6 6 14      flat with outlier pair  *     *
sds: 0.0 vs 3.16 vs 5.66 - the sd hints, only the plot tells
```

## Truncated axis dishonesty

```text
honest (0-based):   truncated (5.5-based):
5.8 | ## 6.1 | ##   5.8 | #  6.1 | ########
5.5 | ## ...         (identical data, manufactured drama)
```

## Overplotting fixes

```text
raw blob:       alpha:          jitter:         binned means:
*********       .:##:.:         . * . *         [0,2): 3.0
*********  -->  :#####:    -->  * . * .    -->  [2,4): 4.5
*********       .:##:.:         . * . *         [4,6): 6.5
                                                        [6,8): 8.0
```

## Category bars with denominators

```text
books: 3/8 ###     games: 3/8 ###     food: 2/8 ##
```

## Dual-axis warning

```text
series A (left axis 0-10) vs series B (right axis 0-1000):
rescale either axis and the "crossover" moves - crossings are artifacts.
Plot separately or index both to a common baseline.
```
