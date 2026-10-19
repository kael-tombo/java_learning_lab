# Code Deep Dive: 03-rnn-lstm-gru
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl03A - RNN recurrence unrolled
h = tanh(0.8x + 0.5h + 0), three steps on [1,0.5,-0.5].
```java
public class Dl03A {
    public static void main(String[] args) {
        double Wxh=0.8, Whh=0.5, b=0.0, h=0.0;
        double[] xs={1.0,0.5,-0.5};
        for(double x:xs){h=Math.tanh(Wxh*x+Whh*h+b);System.out.printf("x=%.1f h=%.4f%n",x,h);}
    }
}
```
Observed output:
```
x=1.0 h=0.6640
x=0.5 h=0.6243
x=-0.5 h=-0.0876
```
## Snippet 2: Dl03B - LSTM vs GRU param inventory
d=4,h=8: 4*(32+64+8)=416 vs 3*(..)=312.
```java
public class Dl03B {
    public static void main(String[] args) {
        int d=4, h=8;
        int lstm=4*(h*d+h*h+h), gru=3*(h*d+h*h+h);
        System.out.printf("lstm_params=%d (4 gates) gru_params=%d (3 gates)%n", lstm, gru);
        System.out.printf("gates: LSTM=i,f,g,o GRU=z,r,n%n");
    }
}
```
Observed output:
```
lstm_params=416 (4 gates) gru_params=312 (3 gates)
gates: LSTM=i,f,g,o GRU=z,r,n
```
## Checks
- h: 0.6640 -> 0.6243 -> -0.0876: tanh(0.8)=0.6640 hand-checks step one.
- 4 gates (i,f,g,o) vs 3 (z,r,n): GRU is exactly 3/4 the count.

