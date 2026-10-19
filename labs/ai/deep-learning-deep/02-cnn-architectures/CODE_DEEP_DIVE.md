# Code Deep Dive: 02-cnn-architectures
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl02A - LeNet-5 param budget
conv1 156, conv2 2416, fc 48120/10164/850: total 61706 ~= 60k.
```java
public class Dl02A {
    public static void main(String[] args) {
        int c1=6*1*25+6, c2=16*6*25+16, f1=120*400+120, f2=84*120+84, f3=10*84+10;
        int tot=c1+c2+f1+f2+f3;
        System.out.printf("lenet: conv1=%d conv2=%d fc=%d,%d,%d total=%d%n", c1, c2, f1, f2, f3, tot);
        int toy=8*3*9+8+16*8*9+16;
        System.out.printf("toy2layer_params=%d%n", toy);
    }
}
```
Observed output:
```
lenet: conv1=156 conv2=2416 fc=48120,10164,850 total=61706
toy2layer_params=1392
```
## Snippet 2: Dl02B - receptive-field stacking
3x3, 3x3, 2x2-s2 stack: rf 3 -> 5 -> 6.
```java
public class Dl02B {
    public static void main(String[] args) {
        int rf=1, stride=1;
        int[][] layers={{3,1},{3,1},{2,2}};
        for(int[] l:layers){rf+=(l[0]-1)*stride;stride*=l[1];System.out.printf("k=%d s=%d rf=%d cumstride=%d%n",l[0],l[1],rf,stride);}
    }
}
```
Observed output:
```
k=3 s=1 rf=3 cumstride=1
k=3 s=1 rf=5 cumstride=1
k=2 s=2 rf=6 cumstride=2
```
## Checks
- 6*25+6=156; 16*6*25+16=2416; 120*400+120=48120: each term hand-multiplied.
- Total 61,706 grounds the widely cited ~=60k figure in stated layer shapes.

