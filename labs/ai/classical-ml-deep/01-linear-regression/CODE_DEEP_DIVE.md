# Code Deep Dive: 01-linear-regression
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml01A - OLS normal equations
Solves w = (X^T X)^-1 X^T y on y=[2,3,5,4] at x=[1,2,3,4] with bias column. 2x2 inverse via determinant.
```java
public class Cml01A {
    public static void main(String[] args) {
        double[][] X = {{1,1},{1,2},{1,3},{1,4}};
        double[] y = {2,3,5,4};
        double[][] XtX = new double[2][2];
        double[] Xty = new double[2];
        for (int i = 0; i < 4; i++) {
            XtX[0][0] += X[i][0]*X[i][0]; XtX[0][1] += X[i][0]*X[i][1];
            XtX[1][0] += X[i][1]*X[i][0]; XtX[1][1] += X[i][1]*X[i][1];
            Xty[0] += X[i][0]*y[i]; Xty[1] += X[i][1]*y[i];
        }
        double det = XtX[0][0]*XtX[1][1]-XtX[0][1]*XtX[1][0];
        double w0 = (XtX[1][1]*Xty[0]-XtX[0][1]*Xty[1])/det;
        double w1 = (-XtX[1][0]*Xty[0]+XtX[0][0]*Xty[1])/det;
        System.out.printf("XtX=[[%.0f,%.0f],[%.0f,%.0f]] det=%.0f%n", XtX[0][0],XtX[0][1],XtX[1][0],XtX[1][1],det);
        System.out.printf("w0=%.4f w1=%.4f%n", w0, w1);
        double sse=0; for(int i=0;i<4;i++){double p=w0+w1*(i+1); sse+=(p-y[i])*(p-y[i]);}
        System.out.printf("SSE=%.4f%n", sse);
    }
}
```
Observed output:
```
XtX=[[4,10],[10,30]] det=20
w0=1.5000 w1=0.8000
SSE=1.8000
```
## Snippet 2: Cml01B - gradient descent + R^2
200 batch steps from zero at lr=0.05, then R^2 = 1 - SSE/SST.
```java
public class Cml01B {
    public static void main(String[] args) {
        double[] x = {1,2,3,4}; double[] y = {2,3,5,4};
        double w0=0, w1=0, lr=0.05;
        for (int e=0;e<200;e++){double g0=0,g1=0;for(int i=0;i<4;i++){double err=(w0+w1*x[i])-y[i];g0+=err;g1+=err*x[i];}w0-=lr*g0/4;w1-=lr*g1/4;}
        double mean=3.5, sst=0, sse=0;
        for(int i=0;i<4;i++){sst+=(y[i]-mean)*(y[i]-mean);double p=w0+w1*x[i];sse+=(y[i]-p)*(y[i]-p);}
        System.out.printf("gd w0=%.4f w1=%.4f%n", w0, w1);
        System.out.printf("R2=%.4f%n", 1-sse/sst);
    }
}
```
Observed output:
```
gd w0=1.2551 w1=0.8833
R2=0.6320
```
## Checks
- X^T X=[[4,10],[10,30]], det=20 matches hand count (n=4, sum=10, sumsq=30).
- Closed form w0=1.5, w1=0.8; SSE=1.8. GD lands nearby (1.2551, 0.8833); exact match needs more steps.

