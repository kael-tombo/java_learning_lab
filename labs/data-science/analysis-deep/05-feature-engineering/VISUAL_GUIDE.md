# Feature Engineering - Visual Guide

## One-hot map

```text
vocabulary: [red, green, blue]  (order fixed at fit)
red   -> [1, 0, 0]     blue  -> [0, 0, 1]
green -> [0, 1, 0]     ???   -> [0, 0, 0] (declared unknown fallback)
```

## Scaling three lenses on {10..50}

```text
min-max:  0    0.25   0.5   0.75   1.0     (bounds 10..50)
z-score: -1.41 -0.71   0    0.71   1.41    (mean 30, sd 14.14)
robust:  -1.0  -0.5    0    0.5    1.0     (median 30, IQR 20)
```

## Train-only vs leaky fit

```text
honest: fit on {10,20,30,40} -> mean 25.0, sd 11.18
        test 100 -> z 6.71 (alarm rings)
leaky:  fit on all six -> mean 37.5 (test voted in the estimate)
        test 100 -> muted z (alarm muffled)  DO NOT DO THIS
```

## Log compression

```text
area:  50 ------ 80 ------ 120      (gaps 30, 40)
log:   3.91 -- 4.38 -- 4.79         (gaps 0.47, 0.41) compressed
```

## Interaction grid (area x rooms)

```text
        rooms 2   rooms 3   rooms 4
area 50    100       .         .
area 80     .       240        .
area 120    .        .        480
diagonal observed; off-diagonal needs data before modelling
```

## Encoding decision tree

```text
ordered levels? --yes--> ordinal (small<medium<large)
   |
   no -- labels available AND folds strict? --yes--> smoothed target encoding
   |
   no -- few levels? --yes--> one-hot
   |
   open vocabulary? --yes--> hashing trick
```
