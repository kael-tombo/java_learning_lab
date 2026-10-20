# AI Safety & Alignment — Quiz

Answers stated; contested areas flagged inside the answers.

**Q1. Name the classical three-stage RLHF skeleton.**
A: Supervised fine-tuning on demonstrations; training a reward model on human preference
comparisons; policy optimization against that reward. Descriptions vary by team; treat
stage names as process vocabulary.

**Q2. Why does the RL objective include a KL penalty against a reference policy?**
A: It keeps the optimized policy near its reference so reward chasing beyond verified
regions cannot run unchecked; `beta` sets that clamp's strength.

**Q3. What is the coverage/accuracy trade in selective prediction?**
A: Raising the decision threshold covers fewer examples but typically answers with
higher accuracy; coverage falls monotonically while the accuracy schedule depends on
the data between thresholds (our sweep printed a non-monotone stretch).

**Q4. Define specification gaming / reward hacking in one sentence.**
A: Behavior that maximizes the measured proxy while missing the intended goal — the
pattern the toy argmax table simulates.

**Q5. Why is a passing benchmark never a safety guarantee?**
A: Benchmarks sample the test distribution, not deployment distribution's; adaptation to
the test is always a risk; and single metrics hide many simultaneous failure modes.

**Q6. In the proxy-gap table, what does the wrong-but-flattering candidate being picked
regularly indicate about the scoring proxy?**
A: The proxy ranks by style-alignment signal; its correlation with truth was assumed zero
there — the observed gap between `2/3` and `0/3` accuracy is the consequence.

**Q7. Which piece of the guard-rail stack is the least confident to assert in audits?**
A: Coverage of the eval grid (how much of realistic behavior was actually tested);
testing throughput and label quality are the usual reasons the residual is unknown.

**Q8. How should an uncertain forecast about model behavior be written?**
A: With error bars and stated evidence: name conditions that would change the prediction
and give a falsifiable monitoring hook, without inventing incidents or numbers.
