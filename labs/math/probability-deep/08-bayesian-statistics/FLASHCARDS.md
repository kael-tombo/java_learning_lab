# Bayesian Statistics — Flashcards (Verified Numbers)

Cards whose numbers come from the captured runs in CODE_DEEP_DIVE.md;
everything else is a standard definition stated exactly.

### Card 1
**Front**: Name the triple any Bayesian computation bookkeeps.
**Back**: Prior (what you knew), likelihood (what the data endorse),
posterior (what remains), with posterior proportional to likelihood
times prior; the proportionality constant is the evidence, the
probability of the data under the prior-marginalized model.

### Card 2
**Front**: State Beta-Binomial conjugacy exactly.
**Back**: If p is Beta(a, b) and you observe s successes and f failures,
the posterior is exactly Beta(a + s, b + f). Adding counts is the whole
update; no likelihood ever gets integrated.

### Card 3
**Front**: Posterior mean and posterior mode of Beta(A, B)?
**Back**: Mean = A/(A + B); mode (the MAP) = (A - 1)/(A + B - 2), valid
when A, B > 1. On the lab's run: Beta(9, 5) has mean 9/14 (0.642857)
and mode 8/12 = 2/3.

### Card 4
**Front**: Why is Beta(9, 5)'s normalization 1/6435?
**Back**: B(9, 5) = Gamma(9)Gamma(5)/Gamma(14) = 8!4!/13! on integer
parameters — factorial arithmetic the run printed as 1/6435, checking
the density integrates to one without any numeric integration.

### Card 5
**Front**: Does feeding data one-at-a-time differ from absorbing a batch?
**Back**: No — for conjugate updating the posterior is Beta(9, 5) both
ways, machine-equality identical. Successes and failures add in either
order: sufficiency of the counts at work.

### Card 6
**Front**: Posterior predictive for the next flip vs the plug-in rate?
**Back**: Predictive = (a + s)/(a + b + n), which adds prior mass to the
denominator; plug-in = s/n. Lab numbers: 9/14 vs 7/10, an exact gap of
2/35. For Bernoulli the predictive IS the posterior mean.

### Card 7
**Front**: Priors TTT and HHHT — same data heard differently?
**Back**: Flat Beta(1, 1) plus T, T, T gives Beta(1, 4), mean 1/5.
Jeffreys Beta(1/2, 1/2) plus H,H,H,T gives Beta(7/2, 3/2), mean 7/10.
The prior's fingerprint survives the data.

### Card 8
**Front**: Normal-Normal conjugacy in one line.
**Back**: With known variance, posterior precision = 1/tau^2 + n/sigma^2
(precisions ADD) and the posterior mean is the precision-weighted blend
of prior mean and sample mean.

### Card 9
**Front**: MAP vs posterior mean vs credible interval?
**Back**: MAP maximizes the posterior density, the posterior mean
integrates it, and a credible interval is a step that carries a direct
probability claim under the posterior law — no long-run replication
semantics, unlike a frequentist confidence interval.

### Card 10
**Front**: What does the conjugate engine never do?
**Back**: It never integrates a likelihood, needs no sampler, and stays
in exact rationals until the final decimal display (9/14 printed as
0.642857 only for readability).
