# Code Deep Dive: 09-gradient-descent-variants
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt09A - SGD vs momentum vs Adam, one step
w=2, g=0.8: sgd/momentum 1.92, Adam 1.90 (adaptive denom sqrt(0.64)=0.8).
```java
public class Mt09A {
    public static void main(String[] args) {
        double w=2.0,g=0.8,lr=0.1,mu=0.9,m=0,mm=0,vv=0;
        double sg=w-lr*g; System.out.printf("sgd=%.4f%n", sg);
        m=mu*m+g; System.out.printf("momentum_v=%.4f w=%.4f%n", m, w-lr*m);
        mm=0.9*mm+0.1*g; vv=0.999*vv+0.001*g*g;
        double mh=mm/0.1, vh=vv/0.001;
        System.out.printf("adam_mhat=%.4f vhat=%.4f w=%.4f%n", mh, vh, w-lr*mh/(Math.sqrt(vh)+1e-8));
    }
}
```
Observed output:
```
sgd=1.9200
momentum_v=0.8000 w=1.9200
adam_mhat=0.8000 vhat=0.6400 w=1.9000
```
## Snippet 2: Mt09B - RMSprop cache
grads 0.8 then -0.4: cache 0.064 -> 0.0736, w 1.6838 -> 1.8312.
```java
public class Mt09B {
    public static void main(String[] args) {
        double w=2.0, v=0, b=0.9, lr=0.1, e=1e-8;
        for(double g:new double[]{0.8,-0.4}){
            v=b*v+(1-b)*g*g; w-=lr*g/(Math.sqrt(v)+e);
            System.out.printf("g=%.1f cache=%.4f w=%.4f%n", g, v, w);
        }
    }
}
```
Observed output:
```
g=0.8 cache=0.0640 w=1.6838
g=-0.4 cache=0.0736 w=1.8312
```
## Checks
- Momentum v=0.8 first step equals SGD (no history yet); Adam divides by 0.8 adaptive term.
- RMSprop second step is larger relative to grad: cache grew only slightly while |g| halved.

