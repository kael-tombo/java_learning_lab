# Code Deep Dive: 07-positional-encoding
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl07A - sinusoidal PE values
pos=1, d=4: sin/cos at divisors 1 and 100; wavelength note.
```java
public class Dl07A {
    public static void main(String[] args) {
        int pos=1, d=4;
        for(int i=0;i<2;i++){
            double div=Math.pow(10000, 2.0*i/d);
            System.out.printf("PE[%d]=[sin=%.4f,cos=%.4f] div=%.1f%n", i, Math.sin(pos/div), Math.cos(pos/div), div);
        }
        System.out.printf("PE[365] wavelength=%.1f%n", 2*Math.PI*100);
    }
}
```
Observed output:
```
PE[0]=[sin=0.8415,cos=0.5403] div=1.0
PE[1]=[sin=0.0100,cos=1.0000] div=100.0
PE[365] wavelength=628.3
```
## Snippet 2: Dl07B - ALiBi slopes + RoPE angle
Bias -0.5*dist for 1/2/4/8; rotation by 0.5 rad.
```java
public class Dl07B {
    public static void main(String[] args) {
        double[] d={1,2,4,8};
        for(double dist:d) System.out.printf("alibi_bias(dist=%.0f,slope=0.5)=%.1f%n", dist, -0.5*dist);
        double theta=0.5;
        System.out.printf("rope_rot(t=1)=[cos=%.4f,sin=%.4f]%n", Math.cos(theta), Math.sin(theta));
    }
}
```
Observed output:
```
alibi_bias(dist=1,slope=0.5)=-0.5
alibi_bias(dist=2,slope=0.5)=-1.0
alibi_bias(dist=4,slope=0.5)=-2.0
alibi_bias(dist=8,slope=0.5)=-4.0
rope_rot(t=1)=[cos=0.8776,sin=0.4794]
```
## Checks
- PE: sin(1)=0.8415, cos(1)=0.5403; high dim divisor 100 -> sin(0.01)=0.0100.
- ALiBi -0.5/-1/-2/-4 linear in distance; RoPE cos=0.8776, sin=0.4794.

