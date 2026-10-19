# Code Deep Dive: 07-dim-reduction-pca
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml07A - 2x2 eigendecomposition
C=[[4,2],[2,3]]: trace/det, quadratic formula, variance share.
```java
public class Cml07A {
    public static void main(String[] args) {
        double[][] C={{4,2},{2,3}};
        double tr=C[0][0]+C[1][1], det=C[0][0]*C[1][1]-C[0][1]*C[1][0];
        double disc=Math.sqrt(tr*tr-4*det);
        double l1=(tr+disc)/2, l2=(tr-disc)/2;
        System.out.printf("trace=%.1f det=%.1f%n", tr, det);
        System.out.printf("lambda1=%.4f lambda2=%.4f%n", l1, l2);
        System.out.printf("check_sum=%.4f check_prod=%.4f%n", l1+l2, l1*l2);
        System.out.printf("var_explained_PC1=%.4f%n", l1/(l1+l2));
    }
}
```
Observed output:
```
trace=7.0 det=8.0
lambda1=5.5616 lambda2=1.4384
check_sum=7.0000 check_prod=8.0000
var_explained_PC1=0.7945
```
## Snippet 2: Cml07B - projection onto PC1
4 symmetric points projected on [1,0]; variance ratio check.
```java
public class Cml07B {
    public static void main(String[] args) {
        double[][] X={{2,0},{0,1},{-2,0},{0,-1}};
        double[] pc={1,0};
        double tot=0;
        for(double[] p:X){double proj=p[0]*pc[0]+p[1]*pc[1];tot+=proj*proj;System.out.printf("proj=%.1f%n",proj);}
        System.out.printf("var_PC1=%.1f total_var=%.1f ratio=%.4f%n", tot/4, (4+1+4+1)/4.0, (tot/4)/((4+1+4+1)/4.0));
    }
}
```
Observed output:
```
proj=2.0
proj=0.0
proj=-2.0
proj=0.0
var_PC1=2.0 total_var=2.5 ratio=0.8000
```
## Checks
- lambda1=5.5616, lambda2=1.4384; sum=7 (trace), product=8 (det) verify the solve.
- PC1 explains 0.7945 of variance; projection demo ratio 0.8 on its toy set.

