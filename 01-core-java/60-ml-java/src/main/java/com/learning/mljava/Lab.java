package com.learning.mljava;

import java.util.*;
import java.util.function.*;
import java.util.stream.*;

public class Lab {

    static class Matrix {
        final double[][] data;
        final int rows, cols;

        Matrix(double[][] data) { this.data = data; this.rows = data.length; this.cols = data[0].length; }

        Matrix multiply(Matrix other) {
            var result = new double[rows][other.cols];
            for (int i = 0; i < rows; i++)
                for (int j = 0; j < other.cols; j++)
                    for (int k = 0; k < cols; k++)
                        result[i][j] += data[i][k] * other.data[k][j];
            return new Matrix(result);
        }

        double[] flatten() {
            return Arrays.stream(data).flatMapToDouble(Arrays::stream).toArray();
        }
    }

    static class LinearRegression {
        private double w = 0, b = 0;
        private final double learningRate;
        private final int epochs;

        LinearRegression(double lr, int epochs) { this.learningRate = lr; this.epochs = epochs; }

        void fit(double[] x, double[] y) {
            int n = x.length;
            for (int ep = 0; ep < epochs; ep++) {
                double dw = 0, db = 0;
                for (int i = 0; i < n; i++) {
                    double pred = w * x[i] + b;
                    dw += (pred - y[i]) * x[i];
                    db += (pred - y[i]);
                }
                w -= learningRate * dw / n;
                b -= learningRate * db / n;
            }
        }

        double predict(double x) { return w * x + b; }
        double getW() { return w; }
        double getB() { return b; }
    }

    static class KNN {
        private List<double[]> X_train;
        private List<Integer> y_train;
        private final int k;

        KNN(int k) { this.k = k; }

        void fit(List<double[]> X, List<Integer> y) { X_train = X; y_train = y; }

        int predict(double[] point) {
            return X_train.stream()
                .map(x -> new AbstractMap.SimpleEntry<>(distance(x, point), y_train.get(X_train.indexOf(x))))
                .sorted(Comparator.comparingDouble(Map.Entry::getKey))
                .limit(k)
                .collect(Collectors.groupingBy(Map.Entry::getValue, Collectors.counting()))
                .entrySet().stream().max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey).orElse(-1);
        }

        private double distance(double[] a, double[] b) {
            double sum = 0;
            for (int i = 0; i < a.length; i++) sum += Math.pow(a[i] - b[i], 2);
            return Math.sqrt(sum);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Machine Learning in Java Lab ===\n");

        linearRegression();
        knnClassifier();
        matrixOperations();
        dataPreprocessing();
        javaMlLibs();
    }

    static void linearRegression() {
        System.out.println("--- Linear Regression ---");
        var x = new double[]{1, 2, 3, 4, 5, 6, 7, 8};
        var y = new double[]{2, 4, 6, 8, 10, 12, 14, 16};

        var model = new LinearRegression(0.01, 1000);
        model.fit(x, y);

        System.out.printf("  y = %.2f * x + %.2f%n", model.getW(), model.getB());
        System.out.printf("  predict(9) = %.2f (expected ~18)%n", model.predict(9));
        System.out.printf("  predict(10) = %.2f (expected ~20)%n", model.predict(10));
    }

    static void knnClassifier() {
        System.out.println("\n--- KNN Classifier ---");
        var X = List.of(
            new double[]{1.0, 1.0}, new double[]{1.5, 2.0}, new double[]{3.0, 4.0},
            new double[]{5.0, 7.0}, new double[]{3.5, 5.0}, new double[]{4.5, 5.0}
        );
        var y = List.of(0, 0, 0, 1, 1, 1);

        var knn = new KNN(3);
        knn.fit(X, y);

        System.out.println("  predict([2,3]) = " + knn.predict(new double[]{2, 3}) + " (class 0)");
        System.out.println("  predict([5,5]) = " + knn.predict(new double[]{5, 5}) + " (class 1)");
        System.out.println("  predict([1,1]) = " + knn.predict(new double[]{1, 1}) + " (class 0)");
    }

    static void matrixOperations() {
        System.out.println("\n--- Matrix Operations ---");
        var a = new Matrix(new double[][]{{1, 2}, {3, 4}});
        var b = new Matrix(new double[][]{{5, 6}, {7, 8}});
        var c = a.multiply(b);

        System.out.println("  A * B =");
        for (var row : c.data)
            System.out.println("    " + Arrays.toString(row));
        System.out.println("  Flattened: " + Arrays.toString(c.flatten()));

        System.out.println("""
  Neural networks = sequences of matrix multiplications + activations
  Forward pass: y = activation(W * x + b)
  Backpropagation: chain rule for gradient computation
    """);
    }

    static void dataPreprocessing() {
        System.out.println("\n--- Data Preprocessing ---");
        var raw = new ArrayList<Map<String, Object>>();
        var row1 = new HashMap<String, Object>();
        row1.put("age", 25);
        row1.put("income", 50000.0);
        row1.put("city", "NYC");
        var row2 = new HashMap<String, Object>();
        row2.put("age", null);
        row2.put("income", 60000.0);
        row2.put("city", "SF");
        var row3 = new HashMap<String, Object>();
        row3.put("age", 35);
        row3.put("income", null);
        row3.put("city", "NYC");
        raw.add(row1);
        raw.add(row2);
        raw.add(row3);

        System.out.println("  Raw data: " + raw);

        var ages = raw.stream().map(m -> (Integer) m.get("age")).filter(Objects::nonNull)
            .mapToInt(Integer::intValue).average().orElse(0);
        var incomes = raw.stream().map(m -> (Double) m.get("income")).filter(Objects::nonNull)
            .mapToDouble(Double::doubleValue).average().orElse(0);

        var cleaned = raw.stream().map(m -> {
            var copy = new HashMap<>(m);
            if (copy.get("age") == null) copy.put("age", (int) ages);
            if (copy.get("income") == null) copy.put("income", incomes);
            return copy;
        }).toList();

        System.out.println("  After imputation: " + cleaned);

        System.out.println("""
  Preprocessing steps:
  - Handle missing values (mean/median/mode imputation)
  - Normalize/standardize features
  - One-hot encode categorical variables
  - Train/test split
    """);
    }

    static void javaMlLibs() {
        System.out.println("\n--- Java ML Libraries ---");
        System.out.println("""
  Deep Learning:
  - DeepLearning4J (DL4J): neural networks on JVM
    ND4J for tensor operations, training on GPU
  - DJL (Deep Java Library): MXNet, PyTorch, TensorFlow
    Model Zoo for pretrained models

  ML/Statistics:
  - Smile: comprehensive ML (SVM, RF, GBM, NLP)
  - Apache Mahout: scalable ML on Spark
  - Tribuo: Oracle's ML library
  - Java-ML: collection of ML algorithms

  Integration:
  - ONNX Runtime: load ONNX models in Java
  - PMML: export models as Portable Model Markup Language
  - gRPC client to Python inference servers (TF Serving)
    """);
    }
}
