# Neural Networks Basics - MINI PROJECT

## Project: Build a Neural Network from Scratch

Build a fully connected neural network with backpropagation.

### Implementation

```java
public class NeuralNetwork {
    private List<Layer> layers;
    private double learningRate;
    
    public NeuralNetwork(double learningRate) {
        this.learningRate = learningRate;
        this.layers = new ArrayList<>();
    }
    
    public void addLayer(int inputSize, int outputSize, String activation) {
        layers.add(new Layer(inputSize, outputSize, activation));
    }
    
    public double[] forward(double[] input) {
        double[] output = input;
        for (Layer layer : layers) {
            output = layer.forward(output);
        }
        return output;
    }
    
    public void backward(double[] target) {
        // Output layer error
        Layer outputLayer = layers.get(layers.size() - 1);
        double[] errors = new double[target.length];
        for (int i = 0; i < target.length; i++) {
            errors[i] = target[i] - outputLayer.getOutput()[i];
        }
        
        // Backpropagate through layers
        for (int i = layers.size() - 1; i >= 0; i--) {
            errors = layers.get(i).backward(errors, learningRate);
        }
    }
    
    public void train(double[][] X, double[][] y, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (int i = 0; i < X.length; i++) {
                double[] output = forward(X[i]);
                totalLoss += mse(output, y[i]);
                backward(y[i]);
            }
            if (epoch % 100 == 0) {
                System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / X.length);
            }
        }
    }
}
```

### Test It

```java
@Test
public void testNeuralNetwork() {
    NeuralNetwork nn = new NeuralNetwork(0.1);
    nn.addLayer(2, 4, "sigmoid");
    nn.addLayer(4, 1, "sigmoid");
    
    double[][] X = {{0,0}, {0,1}, {1,0}, {1,1}};
    double[][] y = {{0}, {1}, {1}, {0}};
    nn.train(X, y, 10000);
    
    assertTrue(nn.forward(new double[]{0,0})[0] < 0.5);
    assertTrue(nn.forward(new double[]{1,1})[0] < 0.5);
}
```

## Deliverables

- [ ] Layer abstraction with forward/backward
- [ ] Activation functions (sigmoid, ReLU, tanh)
- [ ] Backpropagation implementation
- [ ] Training loop with loss tracking
- [ ] XOR problem solution
