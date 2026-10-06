# Reinforcement Learning - REAL WORLD PROJECT

## Project: Train an Agent to Play CartPole

Build a deep Q-network to solve the CartPole environment.

### Architecture

```
State (4-dim) → Dense(24) → ReLU → Dense(24) → ReLU → Dense(2) → Q-Values
```

### Implementation

```java
public class CartPoleAgent {
    private NeuralNetwork qNetwork;
    private NeuralNetwork targetNetwork;
    private ReplayBuffer replayBuffer;
    
    public void train(int episodes) {
        for (int ep = 0; ep < episodes; ep++) {
            double[] state = env.reset();
            double totalReward = 0;
            
            for (int step = 0; step < 500; step++) {
                int action = chooseAction(state);
                StepResult result = env.step(action);
                
                // Store transition
                replayBuffer.add(state, action, result.getReward(), 
                                result.getNextState(), result.isDone());
                
                // Train on batch
                if (replayBuffer.size() > 32) {
                    trainBatch(32);
                }
                
                state = result.getNextState();
                totalReward += result.getReward();
                
                if (result.isDone()) break;
            }
            
            // Update target network periodically
            if (ep % 10 == 0) {
                targetNetwork.copyWeightsFrom(qNetwork);
            }
            
            System.out.printf("Episode %d: Reward = %.0f%n", ep, totalReward);
        }
    }
    
    private void trainBatch(int batchSize) {
        List<Transition> batch = replayBuffer.sample(batchSize);
        for (Transition t : batch) {
            double[] target = qNetwork.forward(t.getState());
            if (t.isDone()) {
                target[t.getAction()] = t.getReward();
            } else {
                double[] nextQ = targetNetwork.forward(t.getNextState());
                target[t.getAction()] = t.getReward() + 0.99 * max(nextQ);
            }
            qNetwork.backward(target);
        }
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Deep Q-Networks (DQN) combine Q-learning with deep neural networks for complex environments.
- Reference: https://arxiv.org/abs/1312.5602
- Reference: https://www.gymlibrary.dev/environments/classic_control/cart_pole/

## Deliverables

- [x] Deep Q-Network implementation
- [x] Experience replay buffer
- [x] Target network for stability
- [x] Epsilon-greedy exploration
- [x] Training visualization and evaluation
