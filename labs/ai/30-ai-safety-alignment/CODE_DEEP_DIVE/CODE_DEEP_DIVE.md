# AI Safety & Alignment — Code Deep Dive

Two deterministic snippets for the two mechanisms this folder teaches: the
coverage/accuracy trade in selective prediction, and a hand-typed proxy-gap table.
Compile with `javac --release 21 -encoding UTF-8`; run on JDK 23; outputs quoted as
observed.

## Snippet 1 — selective-prediction coverage/accuracy sweep

Five examples carry a confidence score and a correctness bit; the sweep walks thresholds
and prints, per row, coverage and accuracy-of-answered.

```java
public class SelectivePrediction {
    public static void main(String[] args) {
        double[] score = {0.95, 0.85, 0.75, 0.65, 0.35};
        int[] correct = {1, 1, 0, 1, 0}; // 3 of 5 are answered correctly if every answer goes out
        for (double t : new double[]{0.9, 0.8, 0.7, 0.6, 0.0}) {
            int cov = 0, hit = 0;
            for (int i = 0; i < score.length; i++)
                if (score[i] >= t) { cov++; hit += correct[i]; }
            double accuracy = cov > 0 ? (double) hit / cov : 0.0;
            System.out.printf("threshold>=%.2f  coverage=%d/5 (%.2f)  accuracy on answered=%.4f%n",
                t, cov, (double) cov / 5, accuracy);
        }
        System.out.println("trade: raising thresholds removed answers and changed accuracy, non-monotonically");
    }
}
```

Observed output:

```
threshold>=0.90  coverage=1/5 (0.20)  accuracy on answered=1.0000
threshold>=0.80  coverage=2/5 (0.40)  accuracy on answered=1.0000
threshold>=0.70  coverage=3/5 (0.60)  accuracy on answered=0.6667
threshold>=0.60  coverage=4/5 (0.80)  accuracy on answered=0.7500
threshold>=0.00  coverage=5/5 (1.00)  accuracy on answered=0.6000
```

The teaching rows: including the 0.75-scored wrong answer at `t = 0.7` drops answered
accuracy to `0.6667` — lower than the previous row `1.0000`. Accuracy is NOT monotone in
coverage here: moving `0.40 -> 0.60` makes things worse. Any statement
"higher threshold = better" is falsified by this table; the correct summary is "coverage
strictly falls, answered accuracy depends on which examples sit between thresholds".

## Snippet 2 — the proxy-gap argmax table (synthetic, hand-typed)

Facts and scores are constants in the source; nothing is learned or sampled. Three
user-risk cases: a truthfulness-optimal policy always picks candidate A (factual first);
a reward-model policy takes the argmax of the recorded "flattery-leaning" score.

```java
public class RewardHackArgmax {
    public static void main(String[] args) {
        // rows: A score, A correct, B score, B correct
        double[][] cs = {
            {0.3, 1, 0.9, 0},
            {0.3, 1, 0.9, 0},
            {0.3, 0, 0.9, 0}
        };
        int truthHits = 0, rmHits = 0;
        for (double[] row : cs) {
            int rmChoice = row[2] > row[0] ? 1 : 0;   // RM argmax picks higher score
            if (row[1] == 1) truthHits++;
            if (row[rmChoice * 2 + 1] == 1) rmHits++;
            System.out.println("case: oracle picked A, rm picked " + (rmChoice == 1 ? "B" : "A"));
        }
        System.out.printf("oracle accuracy = %d/3, reward-model-argmax accuracy = %d/3%n", truthHits, rmHits);
        System.out.println("proxy score up -> selection moved; factual accuracy fell: classic proxy-gap");
    }
}
```

Observed output:

```
case: oracle picked A, rm picked B
case: oracle picked A, rm picked B
case: oracle picked A, rm picked B
oracle accuracy = 2/3, reward-model-argmax accuracy = 0/3
proxy score up -> selection moved; factual accuracy fell: classic proxy-gap
```

Scope of the claim, plainly: the flattery-leaning score is ASSUMED (typed in), and the
conclusion is about selection logic, not about any particular deployed system. The two
take-aways for write-ups: (1) a proxy that is better along its own axis can still produce
strictly worse truthful outcomes; (2) case 3 shows even a wrong-honest candidate keeps
its spot when policy is truth-first, so the two policies differ in cases the accuracy
column cannot express — map that onto the preference trade you would need to examine in
real settings.
