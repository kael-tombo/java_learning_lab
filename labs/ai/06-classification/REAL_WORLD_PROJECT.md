# Classification - REAL WORLD PROJECT

## Project: Customer Churn Prediction

Build a classification system to predict customer churn.

### Architecture

```
Customer Data → Feature Engineering → Model Training → Evaluation → Deployment
```

### Implementation

```java
public class ChurnPredictor {
    private LogisticRegression model;
    private FeatureEngineer engineer;
    
    public void train(List<Customer> customers) {
        double[][] X = engineer.transform(customers);
        int[] y = customers.stream().mapToInt(Customer::getChurned).toArray();
        
        // Handle class imbalance
        double[] classWeights = computeClassWeights(y);
        
        // Train with weighted loss
        model = new LogisticRegression();
        model.fitWeighted(X, y, classWeights, 0.01, 1000);
    }
    
    public ChurnPrediction predict(Customer customer) {
        double[] features = engineer.transformSingle(customer);
        double probability = model.predictProba(features);
        return new ChurnPrediction(probability, probability > 0.5);
    }
    
    public EvaluationResult evaluate(List<Customer> testCustomers) {
        // Compute precision, recall, F1, AUC
        return new EvaluationResult(precision, recall, f1, auc);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Class imbalance is a common challenge in churn prediction; techniques like SMOTE and class weights help.
- Reference: https://machinelearningmastery.com/tactics-to-combat-imbalanced-classes-in-your-machine-learning-dataset/
- Reference: https://scikit-learn.org/stable/modules/generated/sklearn.utils.class_weight.compute_class_weight.html

## Deliverables

- [x] Data preprocessing pipeline
- [x] Feature engineering for categorical and numerical data
- [x] Model training with class imbalance handling
- [x] Evaluation with precision, recall, F1, AUC
- [x] Prediction API with probability scores
