# Code Deep Dive: 04-rag-evaluation
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg04A - faithfulness + answer relevance
4/5 supported = 0.80; relevance mean of [0.9,0.7,0.8] = 0.8.
```java
public class Lg04A {
    public static void main(String[] args) {
        int supported=4, total=5;
        System.out.printf("faithfulness=%d/%d=%.2f%n", supported, total, (double)supported/total);
        double[] rel={0.9,0.7,0.8};
        System.out.printf("answer_relevance=%.4f%n", (rel[0]+rel[1]+rel[2])/3);
    }
}
```
Observed output:
```
faithfulness=4/5=0.80
answer_relevance=0.8000
```
## Snippet 2: Lg04B - context precision/recall
Flags [1,0,1,1,0]: P@3=2/3=0.6667; recall 1.0.
```java
public class Lg04B {
    public static void main(String[] args) {
        int[] rel={1,0,1,1,0};
        int k=3, hit=0; for(int i=0;i<k;i++) hit+=rel[i];
        System.out.printf("context_precision@3=%d/%d=%.4f%n", hit, k, (double)hit/k);
        System.out.printf("context_recall=3/3=1.0000 (all gold covered)%n");
    }
}
```
Observed output:
```
context_precision@3=2/3=0.6667
context_recall=3/3=1.0000 (all gold covered)
```
## Checks
- Faithfulness = supported claims / total claims against retrieved context.
- One irrelevant chunk in top-3 drops precision to 0.6667 while recall stays perfect.

