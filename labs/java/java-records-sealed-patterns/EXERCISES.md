# Exercises — Records / Sealed / Patterns (10 hands-on)

## E1 — Record Basics
```java
record User(String name, int age) {
  User { if (age < 0) throw new IllegalArgumentException(); }
}
```
Tasks: compact ctor, custom accessor, static factory. Flags: none.

## E2 — Record vs Class equals/hashCode
Tasks: prove records auto-derive; break with mutable array component (defensive copy fix).

## E3 — Sealed Hierarchy
```java
sealed interface Shape permits Circle, Rect { double area(); }
record Circle(double r) implements Shape { public double area(){return Math.PI*r*r;} }
record Rect(double w,double h) implements Shape { public double area(){return w*h;} }
```
Tasks: add Triangle (permits update); try non-permitted impl → error.

## E4 — instanceof Pattern
```java
if (o instanceof Circle c) System.out.println(c.r());
```
Tasks: flow-scoping rules; `&&` guard556556.

## E5 — Switch Pattern Exhaustive
```java
double a = switch (s) {
  case Circle c -> c.area();
  case Rect r -> r.area();
};
```
Tasks: remove default, verify exhaustiveness; add null arm (`case null ->`).

## E6 — Record Patterns
```java
if (u instanceof User(String n, int age)) System.out.println(n);
```
Tasks: nested deconstruction `Order(Customer(String n), List<Item>)`.

## E7 — Guards (when)
```java
case Circle c when c.r() > 0 -> "pos";
```
Tasks: order guards; dominancelabel compile error demo.

## E8 — Generic Records + Serialization
Tasks: `record Box<T>(T v)` JSON round-trip (Jackson); compact JSON size compare.

## E9 — Sealed + Visitor Refactor
Tasks: convert visitor to switch; delete 30 lines, keep tests green.

## E10 — Capstone: AST Eval
Tasks: sealed Expr (Lit/Add/Mul) + switch eval + pretty-printer.
Flags: `-XX:+UseG1GC`. Checklist: exhaustive, no default, null-safe.
