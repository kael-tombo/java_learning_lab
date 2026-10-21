# Common Mistakes in Federated Learning

## 1. Data Mistakes
- Data leakage: Using future information for prediction
- Insufficient data: Model complexity exceeds data size
- Not handling missing values properly
- Wrong train/validation/test split

## 2. Model Mistakes
- Wrong architecture for the problem
- Too complex (overfitting) or too simple (underfitting)
- Poor weight initialization
- Wrong loss function selection

## 3. Training Mistakes
- Learning rate too high (divergence) or too low (slow convergence)
- Training too long without validation monitoring
- Batch size too small (noisy gradients) or too large (poor generalization)
- Not using regularization when needed

## 4. Evaluation Mistakes
- Using wrong metrics for the task
- Not accounting for class imbalance
- Over-optimistic evaluation from data leakage
- Not using confidence intervals

## 5. Deployment Mistakes
- Environment mismatch between training and production
- No monitoring for model drift
- Insufficient testing of inference pipeline
- Not handling edge cases in production data

## 6. Prevention
1. Start simple and iterate
2. Validate assumptions early
3. Use cross-validation for robust estimates
4. Monitor training and validation metrics
5. Document decisions and rationale
