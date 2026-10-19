# Code Deep Dive: 03-activation-functions
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn03A - function values
sigmoid/tanh/ReLU at -2..2.
```java
public class Nn03A {
    public static void main(String[] args) {
        double[] xs={-2,-1,0,1,2};
        for(double v:xs){
            double s=1/(1+Math.exp(-v)), th=Math.tanh(v), r=Math.max(0,v);
            System.out.printf("x=%.0f sig=%.4f tanh=%.4f relu=%.1f%n", v, s, th, r);
        }
    }
}
```
Observed output:
```
x=-2 sig=0.1192 tanh=-0.9640 relu=0.0
x=-1 sig=0.2689 tanh=-0.7616 relu=0.0
x=0 sig=0.5000 tanh=0.0000 relu=0.0
x=1 sig=0.7311 tanh=0.7616 relu=1.0
x=2 sig=0.8808 tanh=0.9640 relu=2.0
```
## Snippet 2: Nn03B - derivatives
sigmoid p(1-p), tanh 1-t^2, ReLU step at -1/0/1.
```java
public class Nn03B {
    public static void main(String[] args) {
        double[] xs={-1,0,1};
        for(double v:xs){
            double s=1/(1+Math.exp(-v));
            double ds=s*(1-s), dt=1-Math.tanh(v)*Math.tanh(v);
            double dr=v>0?1:(v==0?0:0);
            System.out.printf("x=%.0f sig'=%.4f tanh'=%.4f relu'=%.0f%n", v, ds, dt, dr);
        }
    }
}
```
Observed output:
```
x=-1 sig'=0.1966 tanh'=0.4200 relu'=0
x=0 sig'=0.2500 tanh'=1.0000 relu'=0
x=1 sig'=0.1966 tanh'=0.4200 relu'=1
```
## Checks
- sigmoid(1)=0.7311, tanh(1)=0.7616, relu(-2)=0: standard table values.
- Max sigmoid slope 0.25 at 0; tanh slope 1.0 at 0; ReLU 0/1 split.

