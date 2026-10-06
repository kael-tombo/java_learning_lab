# Federated Learning - MINI PROJECT

## Project: Federated Averaging Implementation

Build a federated learning system with FedAvg algorithm.

### Implementation

```java
public class FederatedLearning {
    private NeuralNetwork globalModel;
    private List<Client> clients;
    
    public FederatedLearning(NeuralNetwork initialModel) {
        this.globalModel = initialModel;
        this.clients = new ArrayList<>();
    }
    
    public void addClient(Client client) {
        clients.add(client);
    }
    
    public void train(int rounds, int localEpochs) {
        for (int round = 0; round < rounds; round++) {
            // Select clients for this round
            List<Client> selectedClients = selectClients(clients, 0.5);
            
            // Train on each client
            List<NeuralNetwork> clientModels = new ArrayList<>();
            for (Client client : selectedClients) {
                NeuralNetwork clientModel = globalModel.copy();
                clientModel = client.train(clientModel, localEpochs);
                clientModels.add(clientModel);
            }
            
            // Aggregate models (FedAvg)
            globalModel = aggregateModels(clientModels);
            
            // Evaluate
            double accuracy = evaluate(globalModel);
            System.out.printf("Round %d: Accuracy = %.4f%n", round, accuracy);
        }
    }
    
    private NeuralNetwork aggregateModels(List<NeuralNetwork> clientModels) {
        // Weighted average of model parameters
        NeuralNetwork aggregated = globalModel.copy();
        
        for (int layer = 0; layer < aggregated.numLayers(); layer++) {
            double[][] weights = aggregated.getLayer(layer).getWeights();
            for (int i = 0; i < weights.length; i++) {
                for (int j = 0; j < weights[0].length; j++) {
                    double sum = 0;
                    for (NeuralNetwork clientModel : clientModels) {
                        sum += clientModel.getLayer(layer).getWeights()[i][j];
                    }
                    weights[i][j] = sum / clientModels.size();
                }
            }
        }
        
        return aggregated;
    }
}
```

### Test It

```java
@Test
public void testFederatedLearning() {
    NeuralNetwork model = createSimpleModel();
    FederatedLearning fl = new FederatedLearning(model);
    
    // Add clients with different data
    fl.addClient(new Client(generateData(100)));
    fl.addClient(new Client(generateData(100)));
    fl.addClient(new Client(generateData(100)));
    
    fl.train(10, 5);
    assertTrue(fl.evaluate(testData) > 0.7);
}
```

## Deliverables

- [ ] FedAvg algorithm
- [ ] Client selection
- [ ] Local training
- [ ] Model aggregation
- [ ] Comparison with centralized training
