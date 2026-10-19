# Code Deep Dive: 04-seq2seq-attention
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl04A - alignment weights
Scores [1,2,0.5]: softmax [0.2312,0.6285,0.1402], sum 1.0.
```java
public class Dl04A {
    public static void main(String[] args) {
        double[] scores={1.0,2.0,0.5};
        double m=2.0,s=Math.exp(-1)+1+Math.exp(-1.5);
        for(int i=0;i<3;i++) System.out.printf("alpha%d=%.4f%n", i, Math.exp(scores[i]-m)/s);
        System.out.printf("sum=%.4f%n", (Math.exp(-1)+1+Math.exp(-1.5))/s);
    }
}
```
Observed output:
```
alpha0=0.2312
alpha1=0.6285
alpha2=0.1402
sum=1.0000
```
## Snippet 2: Dl04B - context vector
alpha=[.2,.3,.5] over 3x2 states -> [0.70,0.80].
```java
public class Dl04B {
    public static void main(String[] args) {
        double[][] H={{1,0},{0,1},{1,1}};
        double[] a={0.2,0.3,0.5};
        double c0=a[0]*H[0][0]+a[1]*H[1][0]+a[2]*H[2][0];
        double c1=a[0]*H[0][1]+a[1]*H[1][1]+a[2]*H[2][1];
        System.out.printf("context=[%.2f,%.2f]%n", c0, c1);
    }
}
```
Observed output:
```
context=[0.70,0.80]
```
## Checks
- e^-1=0.3679, e^-1.5=0.2231: weights = each/sum(2.591) verified by hand.
- Context = 0.2[1,0]+0.3[0,1]+0.5[1,1] = [0.7,0.8] exactly.

