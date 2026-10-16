# Model Monitoring - Visual Guide

## Loop
```text
serve -> [log events] -> [rollups] -> [compare vs reference] -> [alert?] -> runbook
              |                                                        |
              +---- ground truth joins later --> mature metrics -------+
```

## Drift sketch
```text
reference:  #######-------
current:    ####-----------
                     ^ gap region (KS finds max CDF gap; PSI sums binned shifts)
```

## Alert tradeoff
```text
threshold loose:  recall high, pages noisy   (many false alarms)
threshold tight:  pages rare, misses grow    (silent regressions)
```

## Maturity
```text
fresh window:  predictions full, labels sparse  (provisional)
mature window: predictions full, labels joined  (official)
```

## Slice vs aggregate
```text
aggregate: ###### stable ######        (hides the break)
slice A:   ###### stable ######
slice B:   ### collapsing ###          (page here, with owner)
```

## Reference pinning
```text
ref v7 (pinned) <---- compare ---- current window
   |                         (refresh only by review + reason)
   +-- old v6 kept for back-comparison
```

## Silent monitor
```text
values:   ---- flat, looks healthy ----
volume:   ████ ..................       (telemetry stopped; page on absence)
```

## Postmortem loop
```text
incident -> pinned case -> rule retune -> reference review -> drill -> close
```
