# AI Safety & Alignment - MINI PROJECT

## Project: RLHF Pipeline Implementation

Build a reinforcement learning from human feedback pipeline.

### Implementation

```java
public class RLHF {
    private NeuralNetwork policyModel;
    private NeuralNetwork rewardModel;
    private NeuralNetwork valueModel;
    
    public void trainRewardModel(List<Preference> preferences) {
        // Train reward model on human preferences
        for (Preference pref : preferences) {
            double rewardChosen = rewardModel.forward(pref.getChosen());
            double rewardRejected = rewardModel.forward(pref.getRejected());
            
            // Bradley-Terry loss
            double loss = -Math.log(sigmoid(rewardChosen - rewardRejected));
            
            // Backpropagate
            rewardModel.backward(loss);
        }
    }
    
    public void trainPolicy(List<Prompt> prompts, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (Prompt prompt : prompts) {
                // Generate response
                double[] response = policyModel.generate(prompt);
                
                // Compute reward
                double reward = rewardModel.forward(response);
                
                // Compute PPO loss
                double oldLogProb = policyModel.getLogProb(prompt, response);
                double newLogProb = policyModel.getLogProb(prompt, response);
                double ratio = Math.exp(newLogProb - oldLogProb);
                
                double advantage = reward - valueModel.forward(prompt);
                double ppoLoss = -Math.min(ratio * advantage, 
                                          clip(ratio, 0.8, 1.2) * advantage);
                
                // Backpropagate
                policyModel.backward(ppoLoss);
            }
        }
    }
    
    public double[] generate(Prompt prompt) {
        return policyModel.generate(prompt);
    }
}
```

### Test It

```java
@Test
public void testRLHF() {
    RLHF rlhf = new RLHF();
    List<Preference> prefs = loadPreferences();
    rlhf.trainRewardModel(prefs);
    
    List<Prompt> prompts = loadPrompts();
    rlhf.trainPolicy(prompts, 10);
    
    double[] response = rlhf.generate(prompts.get(0));
    assertTrue(response.length > 0);
}
```

## Deliverables

- [ ] Reward model training
- [ ] PPO policy optimization
- [ ] KL divergence penalty
- [ ] Response generation
- [ ] Evaluation with human eval metrics
