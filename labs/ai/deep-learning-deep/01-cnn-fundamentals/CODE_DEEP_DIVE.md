# Code Deep Dive: 01-cnn-fundamentals
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl01A - output-size arithmetic
out = (W-K+2P)/S+1 on four (W,K,P,S) cases.
```java
public class Dl01A {
    static int out(int W,int K,int P,int S){return (W-K+2*P)/S+1;}
    public static void main(String[] args) {
        System.out.printf("28,5,0,1 -> %d%n", out(28,5,0,1));
        System.out.printf("32,3,1,1 -> %d%n", out(32,3,1,1));
        System.out.printf("32,3,0,2 -> %d%n", out(32,3,0,2));
        System.out.printf("7,3,0,2 -> %d%n", out(7,3,0,2));
    }
}
```
Observed output:
```
28,5,0,1 -> 24
32,3,1,1 -> 32
32,3,0,2 -> 15
7,3,0,2 -> 3
```
## Snippet 2: Dl01B - param count + toy convolution
8x(3x5x5)+8 = 608; 2x2 kernel [[1,0],[0,-1]] on 3x3 input.
```java
public class Dl01B {
    public static void main(String[] args) {
        int Cin=3, Cout=8, K=5;
        System.out.printf("conv_params=%d (8*3*25 + 8 bias)%n", Cout*Cin*K*K+Cout);
        double[][] x={{1,2,3},{4,5,6},{7,8,9}};
        double[][] k={{1,0},{0,-1}};
        for(int i=0;i<2;i++)for(int j=0;j<2;j++){
            double s=0;for(int a=0;a<2;a++)for(int b=0;b<2;b++)s+=x[i+a][j+b]*k[a][b];
            System.out.printf("y[%d][%d]=%.0f%n", i, j, s);
        }
    }
}
```
Observed output:
```
conv_params=608 (8*3*25 + 8 bias)
y[0][0]=-4
y[0][1]=-4
y[1][0]=-4
y[1][1]=-4
```
## Checks
- 28/5/0/1 -> 24; 32/3/1/1 -> 32 (same); 32/3/0/2 -> 15; 7/3/0/2 -> 3.
- All four valid outputs are -4: each window is (top-left minus bottom-right) = -4 by hand.

