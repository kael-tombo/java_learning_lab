# Model Evaluation — Why It Matters

Promotion, rollback, and launch decisions all rest on evaluation
numbers, so the numbers must mean what they claim. A team that leads
with accuracy on 1%-positive data will ship a majority classifier and
call it 99% accurate. A team that tunes on test will ship optimism and
meet reality in production. A team that ignores calibration will feed
good rankings into bad expected-value decisions.

The demo numbers show the mechanics at small scale: 0.8s that are only
interpretable beside the TP=4/FP=1/FN=1/TN=4 counts they came from, and
a proper-score gap of 0.642 in log-loss between modest and confident
forecasters on the same five labels. At production scale the same mechanics decide revenue,
risk, and trust — which is why the discipline is non-negotiable, not
academic. No metric in this lab is quoted without the counts behind it;
that habit is the whole transferable skill. Teams that internalize it
catch their own errors in review instead of production: the matrix
gets pasted next to every F1, the prevalence next to every accuracy,
the threshold next to every deployed decision rule. Reviewers learn
to ask for the missing denominator the way code reviewers ask for
the missing test — not as hostility, as hygiene. The alternative is
the accuracy-led team from the first paragraph, shipping majority
classifiers at 99% and learning about it from users. Between those
two futures, the only difference is whether anyone insisted on the
denominator before launch. This lab is that insistence, rehearsed
until it is reflex. The demo's scale is deliberately toy — five
labels, one table — so the mechanics stay visible; production adds
zeros to every count and changes nothing about which questions to ask.
Keep this file's habit: every metric you quote, quote with its counts,
its split, and its threshold — the three coordinates that make a number
a measurement instead of a rumor.
