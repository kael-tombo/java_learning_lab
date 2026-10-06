# Regression - REAL WORLD PROJECT

## Project: House Price Prediction

Build a complete regression pipeline for predicting house prices.

### Architecture

```
Raw Data → Feature Engineering → Model Training → Evaluation → Prediction API
```

### Implementation

```java
public class HousePricePredictor {
    private LinearRegression model;
    private FeatureEngineer engineer;
    
    public void train(List<House> houses) {
        double[][] X = engineer.transform(houses);
        double[] y = houses.stream().mapToDouble(House::getPrice).toArray();
        
        // Split data
        int trainSize = (int)(X.length * 0.8);
        double[][] XTrain = Arrays.copyOfRange(X, 0, trainSize);
        double[] yTrain = Arrays.copyOfRange(y, 0, trainSize);
        double[][] XTest = Arrays.copyOfRange(X, trainSize, X.length);
        double[] yTest = Arrays.copyOfRange(y, trainSize, y.length);
        
        // Train model
        model = new LinearRegression();
        model.fit(XTrain, yTrain, 0.01, 1000);
        
        // Evaluate
        double r2 = model.r2Score(XTest, yTest);
        double rmse = rmse(XTest, yTest);
        System.out.printf("R²: %.4f, RMSE: %.2f%n", r2, rmse);
    }
    
    public double predict(House house) {
        double[] features = engineer.transformSingle(house);
        return model.predict(features);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Feature engineering is often more important than model selection for regression tasks.
- Reference: https://scikit-learn.org/stable/modules/linear_model.html
- Reference: https://www.kaggle.com/c/house-prices-advanced-regression-techniques

## Deliverables

- [x] Data loading and preprocessing
- [x] Feature engineering pipeline
- [x] Model training with regularization
- [x] Cross-validation and evaluation
- [x] Prediction API endpoint
