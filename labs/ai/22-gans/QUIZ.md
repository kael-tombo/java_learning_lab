# Quiz: Generative Adversarial Networks

## Instructions
30 questions covering Generative Adversarial Networks concepts. Passing score: 70%.

## Section 1: Multiple Choice (Questions 1-10)

**1. What is the primary goal of **
A) Replace human decision-making
B) Learn patterns from data without explicit programming
C) Store large datasets efficiently
D) Execute faster than traditional programs
Answer: B

**2. What does overfitting mean?**
A) Model is too simple to capture patterns
B) Model memorizes training data and fails on new data
C) Training takes too long
D) Model uses too much memory
Answer: B

**3. What is the role of the learning rate in gradient descent?**
A) Determines model architecture
B) Controls step size of parameter updates
C) Sets the number of training epochs
D) Defines the loss function
Answer: B

**4. Which technique helps prevent overfitting?**
A) Increasing model size
B) Adding L2 regularization
C) Removing validation data
D) Increasing learning rate
Answer: B

**5. What does the gradient of loss with respect to parameters indicate?**
A) The current loss value
B) The direction of steepest increase in loss
C) The optimal parameter values
D) The number of training steps needed
Answer: B

**6. What is the purpose of a validation set?**
A) To train the model
B) To tune hyperparameters without bias
C) To augment the training data
D) To replace the test set
Answer: B

**7. What is backpropagation used for?**
A) Forward propagation of inputs
B) Computing gradients efficiently in neural networks
C) Updating hyperparameters
D) Preprocessing data
Answer: B

**8. What is the bias-variance tradeoff?**
A) Model complexity vs training time
B) Error due to simplifying assumptions vs sensitivity to training data
C) Number of parameters vs dataset size
D) Training loss vs validation loss
Answer: B

**9. What type of learning uses labeled data?**
A) Unsupervised learning
B) Supervised learning
C) Reinforcement learning
D) Self-supervised learning
Answer: B

**10. What does cross-validation help estimate?**
A) Training time
B) Model generalization performance
C) Memory requirements
D) Number of parameters
Answer: B

## Section 2: True/False (Questions 11-20)

**11. More data always improves model performance.**
Answer: False. Data quality matters more than quantity.

**12. A deeper network always performs better.**
Answer: False. Deeper networks can suffer from vanishing gradients and overfitting.

**13. Cross-validation reduces overfitting.**
Answer: True. It provides more robust performance estimates.

**14. Learning rate should be constant throughout training.**
Answer: False. Learning rate schedules often improve convergence.

**15. Feature scaling is important for gradient-based optimization.**
Answer: True. It ensures all features contribute proportionally.

**16. Regularization always improves model performance.**
Answer: False. Too much regularization causes underfitting.

**17. Transfer learning is only useful for image tasks.**
Answer: False. It works across many domains.

**18. Ensemble methods combine multiple models for better predictions.**
Answer: True.

**19. Gradient descent guarantees finding the global optimum.**
Answer: False. It finds a local optimum for non-convex functions.

**20. Data augmentation increases effective dataset size.**
Answer: True. It creates modified versions of existing data.

## Section 3: Short Answer (Questions 21-30)

**21. Explain gradient descent in one paragraph.**
Expected: Iterative optimization algorithm. Computes gradient of loss, updates parameters in opposite direction. Step size controlled by learning rate. Converges to minimum under suitable conditions.

**22. What is the difference between parameters and hyperparameters?**
Expected: Parameters learned from data during training (weights, biases). Hyperparameters set before training (learning rate, batch size, architecture).

**23. Describe three overfitting prevention techniques.**
Expected: Regularization (penalty on weights), dropout (randomly drop units), early stopping (stop when validation loss increases), data augmentation.

**24. Why is non-linearity important in neural networks?**
Expected: Without non-linear activation functions, multiple layers collapse into a single linear transformation, limiting representational power.

**25. What is transfer learning and when is it useful?**
Expected: Using a pre-trained model as starting point for a new task. Useful when limited labeled data is available for the target task.

**26. What is the chain rule and its role in backpropagation?**
Expected: Chain rule computes derivative of composite functions. Backpropagation applies it to propagate error gradients from output to input.

**27. Compare L1 and L2 regularization.**
Expected: L1 adds absolute value penalty, promotes sparsity. L2 adds squared penalty, promotes small weights. L1 can zero out features; L2 cannot.

**28. What is the role of activation functions?**
Expected: Introduce non-linearity, enable learning complex patterns. Common choices: ReLU (fast, sparse), sigmoid (bounded, smooth), tanh (zero-centered).

**29. How do you choose between different algorithms?**
Expected: Consider data size and quality, problem complexity, interpretability needs, computational constraints, and performance requirements.

**30. What is model evaluation and why is it important?**
Expected: Process of assessing model performance on unseen data. Essential for understanding generalization, comparing approaches, and detecting issues like overfitting.
