# Visual Guide - Time Series

## 1. The line plot + rolling stats

Draw y_t with rolling mean (window ~ m) overlaid. Trend shows as a
sloping rolling mean; changing spread shows as a fanning band. This one
plot decides whether to difference or transform.

## 2. ACF/PACF stem plots

Stems at lags 1..2m with dashed bands at +/-1.96/sqrt(T). Cutoff =
stems die after one lag; tail-off = slow decay. Label which panel is
which - mixing them up is the classic misread.

## 3. Decomposition panels

Stack four aligned panels: observed, trend, seasonal, residual. The
residual panel should look patternless; any wave there belongs in the
seasonal panel.

## 4. Rolling-origin sketch

```
train [====] test [-]
train [=====] test [-]
train [======] test [-]
```

Each row extends training by one origin; errors average down the rows.
Never draw arrows from test back into train.

## 5. Forecast with widening fan

Point line plus shaded bands that visibly widen with horizon. If your
charting code draws parallel bands, the variance math is wrong.

## 6. ASCII sanity plot

Print levels as ASCII bars before fancy charts - a 10-line histogram of
differences often reveals the outlier that a smoothed chart hides.

## 7. ASCII ACF check

Print stems as text bars (`lag 2: #### 0.47`) before plotting libraries.
Text stems expose sign flips and cutoffs without axis-truncation tricks,
and they paste into logs where PNGs cannot go.
