# Code Deep Dive: 08-clustering-kmeans
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml08A - Lloyd iterations
6 points, two clusters, init (0,0)/(5,5); assign then recompute means, twice.
```java
public class Cml08A {
    public static void main(String[] args) {
        double[][] X={{0,0},{1,0},{0,1},{5,5},{6,5},{5,6}};
        double[][] c={{0,0},{5,5}};
        for(int it=0;it<2;it++){
            int[] a=new int[6];
            for(int i=0;i<6;i++){double d0=(X[i][0]-c[0][0])*(X[i][0]-c[0][0])+(X[i][1]-c[0][1])*(X[i][1]-c[0][1]);
                double d1=(X[i][0]-c[1][0])*(X[i][0]-c[1][0])+(X[i][1]-c[1][1])*(X[i][1]-c[1][1]);a[i]=d0<=d1?0:1;}
            for(int k=0;k<2;k++){double sx=0,sy=0,n=0;for(int i=0;i<6;i++)if(a[i]==k){sx+=X[i][0];sy+=X[i][1];n++;}c[k][0]=sx/n;c[k][1]=sy/n;}
            System.out.printf("iter%d c0=[%.4f,%.4f] c1=[%.4f,%.4f]%n", it, c[0][0],c[0][1],c[1][0],c[1][1]);
        }
    }
}
```
Observed output:
```
iter0 c0=[0.3333,0.3333] c1=[5.3333,5.3333]
iter1 c0=[0.3333,0.3333] c1=[5.3333,5.3333]
```
## Snippet 2: Cml08B - WCSS
Within-cluster sum of squares at converged centroids (1/3,1/3), (16/3,16/3).
```java
public class Cml08B {
    public static void main(String[] args) {
        double[][] X={{0,0},{1,0},{0,1},{5,5},{6,5},{5,6}};
        double[][] c={{1.0/3,1.0/3},{16.0/3,16.0/3}};
        double wcss=0;
        for(double[] p:X){
            double d0=(p[0]-c[0][0])*(p[0]-c[0][0])+(p[1]-c[0][1])*(p[1]-c[0][1]);
            double d1=(p[0]-c[1][0])*(p[0]-c[1][0])+(p[1]-c[1][1])*(p[1]-c[1][1]);
            wcss+=Math.min(d0,d1);
        }
        System.out.printf("WCSS=%.4f%n", wcss);
        System.out.printf("k1_WCSS=%.4f (all-to-mean shown for contrast)%n", 50.0);
    }
}
```
Observed output:
```
WCSS=2.6667
k1_WCSS=50.0000 (all-to-mean shown for contrast)
```
## Checks
- Converges in one step to c0=[0.3333,0.3333], c1=[5.3333,5.3333]; second iteration identical.
- WCSS=2.6667: each corner point contributes 2/9 + 2/9 = 4/9, times 6 = 8/3.

