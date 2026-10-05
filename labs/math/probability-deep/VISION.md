# Probability Vision: Visual & Intuitive Interpretations

## Probability as Area
Probability is area under a curve. For a continuous random variable, P(a ≤ X ≤ b) is the area under the PDF between a and b. The total area is 1.

**Visual:** A histogram of samples from a distribution approximates the PDF. As sample size grows, the histogram smooths into the curve. The CLT says: sample means always form a bell curve.

## Conditional Probability as Rescaling
P(A|B) restricts the world to where B happened, then asks what fraction also has A. It's like cropping a photo to region B and measuring how much of the crop is A.

**Visual:** A Venn diagram. P(A|B) is the overlap area divided by the entire B circle. When B is small, even a modest overlap gives a high conditional probability.

## Bayes' Theorem as Updating Beliefs
Start with a prior belief. Gather evidence. Update to a posterior belief. Bayes' theorem is the mathematics of learning from experience.

**Visual:** Imagine a doctor diagnosing a rare disease. The prior is low (disease is rare). A positive test is evidence. Bayes updates the probability upward — but not to certainty, because false positives exist. More evidence → more confident posteriors.

## Independence as No Influence
Independent events don't affect each other. Knowing one happened tells you nothing about the other.

**Visual:** Two dice. The outcome of one has no influence on the other. Contrast with drawing cards without replacement — the first card changes the deck, so probabilities shift. That's dependence.

## The CLT as Universal Shape
No matter the original distribution (uniform, exponential, bimodal), sample means converge to a normal distribution. The bell curve is the attractor of averaging.

**Visual:** Roll one die — uniform distribution. Roll two dice and sum — triangular. Roll five dice and sum — nearly normal. Each averaging step smooths the distribution toward the bell curve.

## Markov Chains as State Machines
A Markov chain is a machine that hops between states. The next state depends only on the current state, not the history.

**Visual:** A board game where your next move depends only on where you now, not how you got there. The transition matrix is the rulebook. The stationary distribution is where you end up spending time in the long run.

## Variance as Spread
Variance measures how spread out a distribution is. Low variance — outcomes cluster near the mean. High variance — outcomes are unpredictable.

**Visual:** Two archers. One always hits near the bullseye (low variance). One hits randomly all over the target (high variance). Both might have the same average accuracy, but their consistency differs.

## Monte Carlo as Brute Force
Estimate probabilities by simulating many trials and counting outcomes. The law of large numbers guarantees convergence.

**Visual:** Throw darts randomly at a square containing a circle. The fraction landing in the circle estimates π/4. More darts → better estimate. Monte Carlo turns probability into counting.
