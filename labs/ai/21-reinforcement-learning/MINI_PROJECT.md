# Reinforcement Learning - MINI PROJECT

## Project: Q-Learning Agent

Build a Q-learning agent for a grid world environment.

### Implementation

```java
public class QLearningAgent {
    private double[][] qTable;
    private double learningRate;
    private double discountFactor;
    private double epsilon;
    private Random rand;
    
    public QLearningAgent(int states, int actions, double lr, double gamma, double epsilon) {
        this.qTable = new double[states][actions];
        this.learningRate = lr;
        this.discountFactor = gamma;
        this.epsilon = epsilon;
        this.rand = new Random();
    }
    
    public int chooseAction(int state) {
        if (rand.nextDouble() < epsilon) {
            return rand.nextInt(qTable[state].length); // Explore
        }
        return argmax(qTable[state]); // Exploit
    }
    
    public void update(int state, int action, double reward, int nextState) {
        double currentQ = qTable[state][action];
        double maxNextQ = max(qTable[nextState]);
        double newQ = currentQ + learningRate * (reward + discountFactor * maxNextQ - currentQ);
        qTable[state][action] = newQ;
    }
    
    public void train(GridWorld env, int episodes) {
        for (int ep = 0; ep < episodes; ep++) {
            int state = env.reset();
            int steps = 0;
            while (!env.isTerminal() && steps < 100) {
                int action = chooseAction(state);
                StepResult result = env.step(action);
                update(state, action, result.getReward(), result.getNextState());
                state = result.getNextState();
                steps++;
            }
            // Decay epsilon
            epsilon *= 0.995;
        }
    }
}
```

### Test It

```java
@Test
public void testQLearning() {
    QLearningAgent agent = new QLearningAgent(16, 4, 0.1, 0.9, 0.1);
    GridWorld env = new GridWorld(4, 4);
    agent.train(env, 1000);
    assertTrue(agent.evaluate(env, 100) > 0.8);
}
```

## Deliverables

- [ ] Q-learning algorithm
- [ ] Epsilon-greedy exploration
- [ ] Q-table updates
- [ ] Grid world environment
- [ ] Visualization of learned policy
