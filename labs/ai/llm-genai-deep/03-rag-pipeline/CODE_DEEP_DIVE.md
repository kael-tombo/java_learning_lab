# Code Deep Dive: 03-rag-pipeline
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg03A - chunk-score-retrieve order
Query [1,0]; chunks score 1.0/0.7071/0.0; top-2 retrieved.
```java
public class Lg03A {
    static double cos(double[] a,double[] b){double d=0,na=0,nb=0;for(int i=0;i<a.length;i++){d+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i];}return d/(Math.sqrt(na)*Math.sqrt(nb));}
    public static void main(String[] args) {
        double[] q={1,0};
        double[][] ch={{1,0},{0.7,0.7},{0,1}};
        for(int i=0;i<3;i++) System.out.printf("chunk%d score=%.4f%n", i, cos(q,ch[i]));
        System.out.printf("retrieve_top2=chunk0,chunk1 -> augment -> generate%n");
    }
}
```
Observed output:
```
chunk0 score=1.0000
chunk1 score=0.7071
chunk2 score=0.0000
retrieve_top2=chunk0,chunk1 -> augment -> generate
```
## Snippet 2: Lg03B - MRR and recall@k
Ranks [1,3,2]: MRR=0.6111; recall@2=2/3=0.6667.
```java
public class Lg03B {
    public static void main(String[] args) {
        int[] ranks={1,3,2};
        double mrr=0; for(int r:ranks) mrr+=1.0/r;
        mrr/=ranks.length;
        System.out.printf("ranks=[1,3,2] MRR=%.4f%n", mrr);
        System.out.printf("recall@2=%d/3=%.4f%n", 2, 2.0/3);
    }
}
```
Observed output:
```
ranks=[1,3,2] MRR=0.6111
recall@2=2/3=0.6667
```
## Checks
- cos([1,0],[0.7,0.7]) = 0.7/1.0... = 0.7071 exact to 4 decimals.
- MRR = (1 + 1/3 + 1/2)/3 = 0.6111 hand-verified.

