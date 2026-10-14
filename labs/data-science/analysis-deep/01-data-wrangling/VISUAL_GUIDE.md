# Data Wrangling - Visual Guide

## Pipeline sketch

```text
[ raw CSV-ish text ] --> [ profile ] --> [ coerce ] --> [ dedup ]
      counts               reject log       key set
--> [ impute ] --> [ screen ] --> [ validate ] --> [ clean table ]
     fill value      fences          receipts
```

## Missingness patterns (rows = records, X = observed, . = missing)

```text
MCAR:  X X . X     holes scattered, no pattern by column
       X . X X
MAR:   young rows: X . X .   holes track the observed age column
       senior rows: X X X X
MNAR:  high values: X X . .  holes sit where values would be large
```

## Tukey fences on a number line

```text
values:  12 12 13 13 14 14 14 15 15                60
         |<---- bulk ---->|                        ^
   lo=10.375          hi=17.375                    flagged
Q1=13.0   median~14   Q3=14.75   IQR=1.75
```

## Dedup keying

```text
row  (c7, 2026-01-05) --key--> [c7|2026-01-05] first seen: KEEP
row  (c7, 2026-01-05) --key--> [c7|2026-01-05] seen before: DROP
row  (c7, 2026-01-06) --key--> [c7|2026-01-06] new key: KEEP
```

## Coercion outcomes

```text
"12" --> 12.0      " 45 " --> 45.0 (trimmed)   "7.5" --> 7.5
"-8" --> -8.0      "3x" --> REJECT (bad chars)  "" --> REJECT (blank)
"N/A" --> REJECT (sentinel)
parsed = 4, rejected = 3, sum of parsed = 56.5
```

## Reading rule

If any box in the pipeline picture cannot report its counts, the picture is
incomplete. Counts are the wrangling equivalent of axis labels.
