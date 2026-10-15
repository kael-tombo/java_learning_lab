# Model Evaluation — References

All entries are real publications. Verify editions locally.

1. Hastie, T., Tibshirani, R., Friedman, J. "The Elements of
   Statistical Learning." Confusion-based metrics, deviance
   (log-loss), cross-validation methodology.
2. Breck, E. et al. "The ML Test Score: A Rubric for ML Production
   Readiness." Held-out evaluation and validation checks in production.
3. Sculley, D. et al. "Hidden Technical Debt in Complex Machine
   Learning Systems" (NIPS 2015). Why evaluation discipline erodes
   without defaults like locked test sets.
4. Kohavi, R. Study of cross-validation and bootstrap for accuracy
   estimation and model selection (commonly cited empirical basis for
   fold methodology; check venue/year in library catalogs).
5. Zinkevich, M. "Rules of Machine Learning" (Google, living guide).
   Metric choice matched to product goals and launch thresholds.
6. Fawcett, T. "An introduction to ROC analysis" (Pattern Recognition
   Letters, 2006). The standard ROC/AUC reference: construction,
   interpretation, and averaging over folds.
7. Saito, T. and Rehmsmeier, M. "The Precision-Recall Plot Is More
   Informative than the ROC Plot When Evaluating Binary Classifiers on
   Imbalanced Datasets" (PLoS ONE, 2015). Why PR curves replace ROC
   under class imbalance.
8. Gneiting, T. and Raftery, A. "Strictly Proper Scoring Rules,
   Prediction, and Estimation" (JASA, 2007). The decision-theoretic
   foundation log-loss and Brier rest on.
9. Niculescu-Mizil, A. and Caruana, R. "Predicting Good Probabilities
   with Supervised Learning" (ICML, 2005). Calibration via Platt
   scaling and isotonic regression; why raw scores mislead.

No vendor docs, no invented papers, no benchmark numbers.
