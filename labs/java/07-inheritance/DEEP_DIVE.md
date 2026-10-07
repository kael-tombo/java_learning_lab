# Inheritance — Ultra Deep Dive

## 1. The Diamond Problem and Java's Solution

### The Classic Diamond Problem

```
    A (void m())
   / \
  B   C  (both override m())
   \ /
    D
```

If `D` calls `m()`, which implementation runs — `B.m()` or `C.m()`?

### Multiple Inheritance of Type Only

Java allows multiple inheritance of *type* (interfaces) but not *state* (classes). Since Java 8, interfaces can have `default` methods, which reintroduced the diamond problem in a limited form:

```java
interface A {
    default void m() { System.out.println("A"); }
}
interface B extends A {
    default void m() { System.out.println("B"); }
}
interface C extends A {
    default void m() { System.out.println("C"); }
}
class D implements B, C {
    // MUST override m() — ambiguous
    @Override
    public void m() { B.super.m(); }  // Choose B's version
}
```

### Linearization Rules

Java resolves the diamond of default methods using these precedence rules:

1. **Most specific implementation wins**: If one class/interface is a subtype of another, the more specific wins
2. **Class wins over interface**: A concrete class's implementation beats any default method
3. **Ambiguity requires explicit override**: If two unrelated interfaces provide conflicting defaults, the implementing class must override

```java
interface A { default void m() { } }
interface B { default void m() { } }
class Base { public void m() { } }
class Child extends Base implements A, B {
    // Base.m() wins — class implementation beats default methods
    // No override needed!
}
```

## 2. `super()` and Constructor Chaining

### Bytecode of Constructor Call

```java
class Parent {
    Parent(String s) {}
}
class Child extends Parent {
    Child() {
        super("hello");  // Must be first statement
    }
}
```

```
Child() bytecode:
  aload_0           // Load 'this'
  ldc "hello"       // Push "hello" string
  invokespecial Parent.<init>(String)  // Call parent constructor
  return
```

### The Implicit `super()` Call

If no super() call is specified, the compiler inserts `super()`:

```java
class Parent {
    Parent() {}  // No-arg constructor
}
class Child extends Parent {
    Child() {}  // Implicit: super();
}
```

If Parent has NO no-arg constructor, Child MUST call super explicitly with arguments. This is enforced at compile time — the parser/Attr phase checks.

### Initialization Order

1. Static initializers of Object
2. Static initializers of Parent class
3. Static initializers of Child class
4. Instance init of Object
5. Instance init of Parent (super class fields + constructor body)
6. Instance init of Child (fields + constructor body)

Example demonstrating order:
```java
class Parent {
    static { System.out.print("1 "); }
    { System.out.print("3 "); }
    Parent() { System.out.print("4 "); }
}
class Child extends Parent {
    static { System.out.print("2 "); }
    { System.out.print("5 "); }
    Child() { System.out.print("6 "); }
}
new Child();  // Output: 1 2 3 4 5 6
```

### Constructor Chaining Bytecode

Each constructor starts with either:
1. `invokespecial <init>` — calls another constructor in the same class (this())
2. `invokespecial Parent.<init>` — calls superclass constructor
3. Both — if the class is a record, a canonical constructor first calls `java.lang.Record.<init>`

## 3. Abstract Classes vs Interfaces: JVM Perspective

### Abstract Class Instance

Abstract classes cannot be instantiated, but they have full object layout:
```java
abstract class Shape {
    int x, y;
    abstract double area();
}
// Shape.class is a valid class file with ACC_ABSTRACT flag
// Shape has a complete vtable (slots for x, y accessors + area)
```

### Interface as Class File

Interfaces also compile to .class files:
```java
interface Drawable {
    void draw();
    default void render() { draw(); }  // Default method
}
```

The class file has `ACC_INTERFACE` and `ACC_ABSTRACT` flags. Default methods have a Code attribute with actual bytecode.

## 4. Final Classes and Methods

### Final Class

```java
final class Immutable { }
// Cannot be subclassed — checked at compile time
// JIT optimization: all methods can be inlined with no guard
```

### Final Method

```java
class Parent {
    final void templateMethod() { step1(); step2(); }
}
// Subclasses can inherit but NOT override
// JIT: can inline with single-implementation assumption
```

### Final Method Bytecode

The `ACC_FINAL` flag is set in the method's `access_flags`. The verifier ensures no subclass overrides a final method.

## 5. The `protected` Access Modifier

```java
package p1;
public class Parent {
    protected void m() { }
}

package p2;
public class Child extends Parent {
    void test() {
        m();  // OK — inherited
        Parent p = new Parent();
        p.m();  // COMPILE ERROR! Can only access through subclass reference
    }
}
```

The second case fails because `protected` access is only allowed:
1. From the same package, OR
2. Through a reference of the subclass type (or its subclasses)

This is enforced during compilation — the Attr phase checks the access context.

## 6. Class Literals and Inheritance

```java
class Parent { }
class Child extends Parent { }

Class<?> c1 = Child.class;
Class<?> c2 = Class.forName("Child");
// Both return the same Class object for Child

// instanceof works with inheritance:
boolean b = child instanceof Parent;  // true
// getClass() does NOT work with inheritance:
boolean b = child.getClass() == Parent.class;  // false (returns Child class)
```

## 7. Inheritance and Inner Classes

```java
class Outer {
    class Inner {
        void access() {
            Outer.this.method();  // Uses synthetic this$0
        }
    }
}
class SubClass extends Outer.Inner {
    SubClass(Outer o) {
        o.super();  // Must provide enclosing instance
    }
}
```

The `o.super()` syntax is required to link the enclosing instance when extending an inner class. The compiler generates a synthetic constructor with the enclosing reference.

## 8. The `@Override` Annotation

The `@Override` annotation (since Java 5) marks a method that intends to override a superclass/interface method:

```java
interface Drawable { void draw(); }
class Circle implements Drawable {
    @Override
    public void draw() { }  // Correct override
}
```

**What the compiler checks**:
- The annotated method must actually override a method in a superclass/superinterface
- Parameter types must match exactly (no subtype in override — covariant params are NOT allowed)
- Return type can be covariant (subtype, allowed since Java 5)

Without `@Override`, if the interface changes, you might accidentally have an overload instead of an override. The annotation prevents this.

## 9. Inheritance and Methods of Object

Every class inherits from `Object`. Key methods that can be overridden:
- `toString()` — String representation
- `equals(Object)` — Value equality
- `hashCode()` — Hash for hash-based collections
- `clone()` — Object copying (protected)
- `finalize()` — Deprecated cleanup method (protected)
- `getClass()` — FINAL: returns runtime class

Methods you CANNOT override (final methods of Object):
- `getClass()` — prevents spoofing the class identity
- `wait()`, `notify()`, `notifyAll()` — final (native implementations tied to monitors)
- `registerNatives()` — private

## 10. Sealed Classes and Inheritance

Sealed classes (JEP 409, Java 17; previews JEP 360 in 15 and JEP 397 in 16) restrict which classes can extend them:

```java
sealed class Shape permits Circle, Square, Triangle { }
final class Circle extends Shape { }
final class Square extends Shape { }
final class Triangle extends Shape { }
```

The permits clause lists ALL allowed subclasses. The compiler checks:
1. All permitted subclasses are in the same module (or same package if unnamed module)
2. Each permitted subclass must directly extend the sealed class
3. No other class can extend the sealed class

### Bytecode of Sealed Classes

The sealed class has a `PermittedSubclasses` attribute in the class file:
```
PermittedSubclasses:
  Circle
  Square
  Triangle
```

The JVM enforces this at class-loading time — if a non-permitted class attempts to extend a sealed class, the verifier throws `IncompatibleClassChangeError`.

### Sealed Interfaces and Records

```java
sealed interface Expr permits Const, Add, Mul {}
record Const(int val) implements Expr {}
record Add(Expr left, Expr right) implements Expr {}
record Mul(Expr left, Expr right) implements Expr {}
```

This enables total type coverage for switch expressions:
```java
int eval(Expr e) {
    return switch (e) {
        case Const c -> c.val();
        case Add a -> eval(a.left()) + eval(a.right());
        case Mul m -> eval(m.left()) * eval(m.right());
        // No default needed — all subtypes covered!
    };
}
```

## 11. The `super` Keyword: Multiple Levels

```java
class Grandparent { 
    void m() { print("G"); } 
}
class Parent extends Grandparent { 
    void m() { print("P"); super.m(); } 
}
class Child extends Parent { 
    void m() { print("C"); super.m(); } 
}
// new Child().m() → "CPG"
```

Each `super.m()` invokes the parent's version via `invokespecial`. The chain is hardcoded at compile time — there's no dynamic dispatch for `super` calls.

## 12. Inheritance and `this` in Constructors

If a method called from a constructor is overridden, the subclass version runs:

```java
class Parent {
    Parent() { init(); }
    void init() { print("P"); }
}
class Child extends Parent {
    int x = 42;
    @Override void init() { print("C:" + x); }
}
new Child();  // Prints "C:42" — Child.init() called before Child constructor body
// x is 42 because field initializers run before the subclass constructor body
```

## 10. Enum Inheritance

All enums implicitly extend `java.lang.Enum`:

```java
enum Color { RED, GREEN, BLUE }
// Compiles to:
// final class Color extends java.lang.Enum<Color> {
//     public static final Color RED = new Color("RED", 0);
//     public static final Color GREEN = new Color("GREEN", 1);
//     public static final Color BLUE = new Color("BLUE", 2);
// }
```

Enums cannot extend other classes — the compiler enforces this. But enums CAN implement interfaces:

```java
interface Describable { String describe(); }
enum Color implements Describable {
    RED { public String describe() { return "warm"; } },
    GREEN { public String describe() { return "nature"; } };
}
```

Each enum constant can have its own anonymous class body with overridden methods.
