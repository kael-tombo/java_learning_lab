# Exercises - Java Fundamentals (fundamentals)

6 hands-on drills on syntax, OOP, JVM, classpath. JDK 21+, JDK only, no dependencies.
Each drill: predict the output, then build with `javac --release 21 -encoding UTF-8 -d out Main.java` and run with `java -cp out Main`.
## Ex 1: Warm-up: explore types & operators
```java
public class Main {
  public static void main(String[] a) {
    System.out.println("div=" + (7 / 2) + " divD=" + (7 / 2.0));
    System.out.println("wrap=" + (Integer.MAX_VALUE + 1) + " big=" + ((long) Integer.MAX_VALUE + 1));
  }
}
```
Observed: div=3 divD=3.5 / wrap=-2147483648 big=2147483648
## Ex 2: Measure control flow
```java
public class Main {
  static String grade(int s) { return switch (s / 10) { case 10, 9 -> "A"; case 8 -> "B"; default -> "F"; }; }
  public static void main(String[] a) {
    for (int s : new int[]{95, 84, 50}) System.out.println(s + "=" + grade(s));
  }
}
```
Observed: 95=A, 84=B, 50=F
## Ex 3: Break OOP pillars
```java
abstract class Shape { abstract double area(); }
class Circle extends Shape {
  private final double r;
  Circle(double r) { this.r = r; }
  @Override double area() { return Math.PI * r * r; }
}
public class Main {
  public static void main(String[] a) { Shape s = new Circle(1.0); System.out.println("area=" + s.area()); }
}
```
Observed: area=3.141592653589793
## Ex 4: Fix + harden exceptions
```java
public class Main {
  static int parse(String s) {
    try { return Integer.parseInt(s); }
    catch (NumberFormatException e) { return -1; }
  }
  public static void main(String[] a) { System.out.println("v1=" + parse("42") + " v2=" + parse("x9")); }
}
```
Observed: v1=42 v2=-1
## Ex 5: Warm-up: explore generics intro
```java
class Box<T> {
  private T v;
  Box(T v) { this.v = v; }
  T get() { return v; }
}
public class Main {
  public static void main(String[] a) { System.out.println("box=" + new Box<>("hi").get() + " same=" + (new Box<String>("x").getClass() == new Box<Integer>(1).getClass())); }
}
```
Observed: box=hi same=true
## Ex 6: Measure JVM & bytecode
```java
public class Main {
  public static void main(String[] a) {
    System.out.println("main=" + Main.class.getName());
    for (String s : a) System.out.println("arg=" + s);
  }
}
```
Observed with `java -cp out Main hi`: main=Main, arg=hi
