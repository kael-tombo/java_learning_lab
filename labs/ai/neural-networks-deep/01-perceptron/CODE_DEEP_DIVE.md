# Code Deep Dive: 01-perceptron
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn01A - perceptron learns OR
Update w += err*x, b += err; 10 passes over OR gate truth table.
```java
public class Nn01A {
    public static void main(String[] args) {
        double[][] X={{0,0},{0,1},{1,0},{1,1}}; int[] y={0,1,1,1};
        double[] w={0,0}; double b=0;
        for(int e=0;e<10;e++) for(int i=0;i<4;i++){
            int p=(w[0]*X[i][0]+w[1]*X[i][1]+b)>=0?1:0;
            int err=y[i]-p; w[0]+=err*X[i][0]; w[1]+=err*X[i][1]; b+=err;
        }
        System.out.printf("w=[%.1f,%.1f] b=%.1f%n", w[0],w[1],b);
        for(int i=0;i<4;i++){int p=(w[0]*X[i][0]+w[1]*X[i][1]+b)>=0?1:0;System.out.printf("OR(%.0f,%.0f)=%d%n",X[i][0],X[i][1],p);}
    }
}
```
Observed output:
```
w=[1.0,1.0] b=-1.0
OR(0,0)=0
OR(0,1)=1
OR(1,0)=1
OR(1,1)=1
```
## Snippet 2: Nn01B - XOR fails
Same rule on XOR; accuracy and update count show non-convergence.
```java
public class Nn01B {
    public static void main(String[] args) {
        double[][] X={{0,0},{0,1},{1,0},{1,1}}; int[] y={0,1,1,0};
        double[] w={0,0}; double b=0; int updates=0;
        for(int e=0;e<10;e++) for(int i=0;i<4;i++){
            int p=(w[0]*X[i][0]+w[1]*X[i][1]+b)>=0?1:0;
            int err=y[i]-p; if(err!=0)updates++; w[0]+=err*X[i][0]; w[1]+=err*X[i][1]; b+=err;
        }
        int ok=0; for(int i=0;i<4;i++){int p=(w[0]*X[i][0]+w[1]*X[i][1]+b)>=0?1:0;if(p==y[i])ok++;}
        System.out.printf("XOR acc=%d/4 updates=%d (not linearly separable)%n", ok, updates);
    }
}
```
Observed output:
```
XOR acc=2/4 updates=38 (not linearly separable)
```
## Checks
- OR converges to w=[1,1], b=-1, exact truth table reproduced.
- XOR stalls at 2/4 with 38 updates: no linear separator exists, as theory states.

