# Generative Adversarial Networks — Quiz

Answers follow each item; they are the accepted standard statements.

**Q1. Write the original GAN minimax objective.**
A: `min_G max_D E_{x~p_data}[log D(x)] + E_{z~p_z}[log(1 - D(G(z)))]`.

**Q2. What is the optimal discriminator for a fixed generator?**
A: `D*(x) = p_data(x) / (p_data(x) + p_model(x))` — the ratio turn of the two densities.

**Q3. Which divergence does the game equal under the optimal discriminator?**
A: Twice the Jensen-Shannon divergence between `p_data` and `p_model` (up to log 2
constants).

**Q4. Why is the non-saturating generator loss preferred?**
A: The saturating form `-log(1 - D(G(z)))` loses gradient when `D` confidently rejects
fakes; ascending `log D(G(z))` avoids that early dead zone.

**Q5. What is mode dropping?**
A: A generator that matches only some of the true distribution's modes, producing samples
with real-looking local quality but poor coverage.

**Q6. Why do we call GANs an "implicit" model?**
A: They define the distribution only through sampling; no tractable density is exposed,
so likelihood-based scores do not directly exist.

**Q7. In our scalar toy, why did the generator drift past the data point?**
A: Its surrogate is a monotone function of the discriminator's logit; nothing in the local
objective penalizes overshoot, so with positive `w` the point keeps sliding.

**Q8. Name one evaluation practice for GANs and its limitation.**
A: Sample-quality heuristics or a trained classifier's behavior on fakes; both are proxies
tied to the classifier's own biases and never a likelihood.

**Q9. What should the discriminator output at the theoretical equilibrium?**
A: One half for every input, since the two densities coincide — the classic parity
argument leaves no signal to exploit.

**Q10. Why is no GAN score directly comparable across papers?**
A: Sample-side proxies inherit the architecture, augmentation stack, and classifier
choices; without a shared density there is no common denominator.

**Q11. Why does deep GAN training lean on schedule and rate tuning?**
A: Alternating updates chase a saddle rather than a plain minimum; our stability run
showed three rates landing in three visibly different places.
