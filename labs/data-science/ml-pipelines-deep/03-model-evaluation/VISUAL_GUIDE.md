# Model Evaluation — Visual Guide

## Confusion matrix (demo)
```
                pred 1    pred 0
label 1           4         1      recall = 4/5 = 0.8
label 0           1         4
               precision  TN
               = 4/5=0.8
```

## F1 as harmonic mean
```
P=0.8 R=0.8: F1 = 2*0.8*0.8/1.6 = 0.8
P=1.0 R=0.2: F1 = 2*1*0.2/1.2 = 0.33 (punishes the weak side)
```

## Proper scores vs baseline (demo)
```
confident: logloss 1.06569   brier 0.24608
modest:    logloss 0.42397   brier 0.12200
const 0.5: logloss 0.69314   brier 0.25
lower wins; baseline is the "did we learn anything" line
```

## Stratified 2-fold (demo, 6 neg + 4 pos)
```
fold0 test: [0,2,4,6,8]  n=5 pos=2
fold1 test: [1,3,5,7,9]  n=5 pos=2
overall pos rate 0.4 preserved in both folds
```

## Split discipline
```
train: fit preprocessing + fit model
val:   select threshold/hparams (reusable)
test:  score once (locked; preprocessing applied, never fit)
leak:  fitting preprocessing on all data first contaminates val/test
```
