# Meta-Learning — Quiz

Keys after each item, standard statements only.

**Q1. What are the inner and outer loops in the model-based meta family?**
A: Inner = adapting parameters on a task's support set; outer = updating the shared
initialization using query-set performance after adaptation.

**Q2. What does the first-order approximation drop?**
A: The second-order chain through the inner gradient step; the outer gradient is read
directly at the adapted parameters (pseudo-gradient form).

**Q3. Write the inner update rule.**
A: `theta1 = theta0 - alpha * dL_support(theta0)/d theta0`.

**Q4. Reptile's update in one line?**
A: `theta_next = theta + epsilon * ( mean of inner solutions - theta )`.

**Q5. Why did task B's outer gradient flip sign in our run?**
A: A single large-curvature inner step overshot the query optimum
(`theta1 = -1.6`, fixed point `-0.5`), so the query loss pulled the opposite way.

**Q6. What does a good meta-initialization achieve, informally?**
A: Starting points from which each task from the distribution is a SHORT downhill walk,
i.e., low post-adaptation loss across tasks.

**Q7. Name the standard evaluation for meta-learners.**
A: Adaptation-time comparison on held-out tasks: few inner steps at test time versus the
from-scratch baseline on the same support size.

**Q8. What is the stability bound for a scalar inner step?**
A: For quadratic curvature `c`, convergence needs `lr < 2/c`; with task B at `c = 32`,
`lr = 0.1` violates the bound and diverges, while `lr = 0.05` sits inside it.
