# Code Deep Dive: 01-embeddings-semantic
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg01A - cosine similarity values
Query [1,0,1] vs three fixed docs: 0.9986/0.0000/0.9959.
```java
public class Lg01A {
    static double cos(double[] a,double[] b){double d=0,na=0,nb=0;for(int i=0;i<a.length;i++){d+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i];}return d/(Math.sqrt(na)*Math.sqrt(nb));}
    public static void main(String[] args) {
        double[] q={1,0,1}, d1={1,0,0.9}, d2={0,1,0}, d3={0.9,0.1,1};
        System.out.printf("cos(q,d1)=%.4f%n", cos(q,d1));
        System.out.printf("cos(q,d2)=%.4f%n", cos(q,d2));
        System.out.printf("cos(q,d3)=%.4f%n", cos(q,d3));
    }
}
```
Observed output:
```
cos(q,d1)=0.9986
cos(q,d2)=0.0000
cos(q,d3)=0.9959
```
## Snippet 2: Lg01B - nearest-neighbor ranking
Four docs scored; top1 selected programmatically.
```java
public class Lg01B {
    static double cos(double[] a,double[] b){double d=0,na=0,nb=0;for(int i=0;i<a.length;i++){d+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i];}return d/(Math.sqrt(na)*Math.sqrt(nb));}
    public static void main(String[] args) {
        double[] q={1,0,1};
        double[][] docs={{1,0,0.9},{0,1,0},{0.9,0.1,1},{0.2,0.9,0.1}};
        int best=0; double bs=-2;
        for(int i=0;i<docs.length;i++){double c=cos(q,docs[i]);System.out.printf("doc%d cos=%.4f%n",i,c);if(c>bs){bs=c;best=i;}}
        System.out.printf("top1=doc%d%n", best);
    }
}
```
Observed output:
```
doc0 cos=0.9986
doc1 cos=0.0000
doc2 cos=0.9959
doc3 cos=0.2287
top1=doc0
```
## Checks
- Orthogonal doc scores exactly 0.0000; near-duplicate 0.9986 > partial 0.9959.
- Top1 = doc0 by argmax over printed scores; doc3 0.2287 ranks last.

