# Code Deep Dive: 04-gradient-vector-calc
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt04A - analytic vs numeric gradient
f=a^2 b^2 at (2,3): analytic [36,24] vs central differences.
```java
public class Mt04A {
    interface F2 { double apply(double a,double b); }
    public static void main(String[] args) {
        double x=2.0, y=3.0;
        double analyticX=2*x*y*y, analyticY=2*x*x*y;
        double h=1e-6;
        F2 f=(a,b)->a*a*b*b;
        double nx=(f.apply(x+h,y)-f.apply(x-h,y))/(2*h), ny=(f.apply(x,y+h)-f.apply(x,y-h))/(2*h);
        System.out.printf("analytic=[%.1f,%.1f] numeric=[%.4f,%.4f]%n", analyticX, analyticY, nx, ny);
    }
}
```
Observed output:
```
analytic=[36.0,24.0] numeric=[36.0000,24.0000]
```
## Snippet 2: Mt04B - Jacobian shape and action
f:R3->R2 toy map: 2x3 Jacobian times a step vector.
```java
public class Mt04B {
    public static void main(String[] args) {
        System.out.printf("f:R3->R2 jacobian_shape=2x3%n");
        double[] x={1,2,3};
        double[][] J={{2*x[0],0,0},{1,1,1}};
        System.out.printf("J=[[%.0f,%.0f,%.0f],[%.0f,%.0f,%.0f]]%n", J[0][0],J[0][1],J[0][2],J[1][0],J[1][1],J[1][2]);
        double[] v={0.1,0.1,0.1};
        System.out.printf("Jv=[%.2f,%.2f]%n", J[0][0]*v[0]+J[0][1]*v[1]+J[0][2]*v[2], J[1][0]*v[0]+J[1][1]*v[1]+J[1][2]*v[2]);
    }
}
```
Observed output:
```
f:R3->R2 jacobian_shape=2x3
J=[[2,0,0],[1,1,1]]
Jv=[0.20,0.30]
```
## Checks
- Numeric [36.0000,24.0000] matches analytic to 4 decimals: independent check passes.
- Jv=[0.20,0.30]: linearization predicts f(x+v) - f(x).

