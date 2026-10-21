# Model Training Pipelines — Visual Guide

## The DAG
```
ingest --> validate --pass--> transform --> train --> evaluate --pass--> register
                |                                                  |
              fail                                               fail
                v                                                  v
           stop+page                                        record, no promote
```

Observed healthy run: order=ingest->validate->transform->train->
evaluate->register, gate_pass=true, stages=6.

## Validation snapshot (demo column)
```
values: 1.0 null 3.0 null 5.0 7.0 null 9.0 11.0 13.0
nulls:  ###.......  3/10 = 0.3 > 0.25 -> drift_flag=true
range:  [1.0, 13.0], non-negative -> schema_ok=true
```

## Seed determinism
```
seed 42 run1: [2, 6, 3, 1, 4, 0, 7, 5]
seed 42 run2: [2, 6, 3, 1, 4, 0, 7, 5]  equal
seed 7  run3: different order           not equal
```

## Tracking record shape
```
run: params{lr, depth} + metrics{scores} + code_hash + data_hash
     + seed + timestamps -> artifact model:vN (immutable)
config: lr=0.01|depth=6|seed=42|data=v3  hash=-1652323048
```

## Retraining loop
```
schedule/data trigger --> same DAG, new dataset version
metrics delta reflects data change (seeds pinned, code pinned)
```
