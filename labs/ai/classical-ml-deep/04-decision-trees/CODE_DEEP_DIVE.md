# Code Deep Dive: 04-decision-trees
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml04A - Gini vs entropy values
Gini = 1 - sum p^2; entropy = -sum p log2 p on [2,1], [1,1], [3,0].
```java
public class Cml04A {
    static double gini(int[] c){int n=0;for(int v:c)n+=v;double s=0;for(int v:c){double p=(double)v/n;s+=p*p;}return 1-s;}
    static double entropy(int[] c){int n=0;for(int v:c)n+=v;double s=0;for(int v:c){if(v==0)continue;double p=(double)v/n;s-=p*Math.log(p)/Math.log(2);}return s;}
    public static void main(String[] args) {
        System.out.printf("gini[2,1]=%.4f entropy[2,1]=%.4f%n", gini(new int[]{2,1}), entropy(new int[]{2,1}));
        System.out.printf("gini[1,1]=%.4f entropy[1,1]=%.4f%n", gini(new int[]{1,1}), entropy(new int[]{1,1}));
        System.out.printf("gini[3,0]=%.4f entropy[3,0]=%.4f%n", gini(new int[]{3,0}), entropy(new int[]{3,0}));
    }
}
```
Observed output:
```
gini[2,1]=0.4444 entropy[2,1]=0.9183
gini[1,1]=0.5000 entropy[1,1]=1.0000
gini[3,0]=0.0000 entropy[3,0]=0.0000
```
## Snippet 2: Cml04B - best 1D split search
x=[1..5], y=[0,0,1,1,1]; weighted Gini at midpoints 1.5/2.5/3.5/4.5.
```java
public class Cml04B {
    static double gini(int a,int b){int n=a+b;if(n==0)return 0;double pa=(double)a/n,pb=(double)b/n;return 1-pa*pa-pb*pb;}
    public static void main(String[] args) {
        double[] x={1,2,3,4,5}; int[] y={0,0,1,1,1};
        double best=1e9, bt=0;
        for(double t:new double[]{1.5,2.5,3.5,4.5}){
            int l0=0,l1=0,r0=0,r1=0;
            for(int i=0;i<5;i++){if(x[i]<=t){if(y[i]==0)l0++;else l1++;}else{if(y[i]==0)r0++;else r1++;}}
            int ln=l0+l1, rn=r0+r1;
            double w=(double)ln/5*gini(l0,l1)+(double)rn/5*gini(r0,r1);
            System.out.printf("t=%.1f giniL=%.4f giniR=%.4f weighted=%.4f%n", t, gini(l0,l1), gini(r0,r1), w);
            if(w<best){best=w;bt=t;}
        }
        System.out.printf("best_t=%.1f best=%.4f%n", bt, best);
    }
}
```
Observed output:
```
t=1.5 giniL=0.0000 giniR=0.3750 weighted=0.3000
t=2.5 giniL=0.0000 giniR=0.0000 weighted=0.0000
t=3.5 giniL=0.4444 giniR=0.0000 weighted=0.2667
t=4.5 giniL=0.5000 giniR=0.0000 weighted=0.4000
best_t=2.5 best=0.0000
```
## Checks
- Gini[2,1]=0.4444 vs entropy 0.9183; pure node scores 0 under both.
- Split at 2.5 gives weighted Gini 0.0 (perfect split); 1.5 gives 0.3.

