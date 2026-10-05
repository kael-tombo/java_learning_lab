# THEORY — Fundamentals

## Overview

This module covers the absolute fundamentals of Java programming — the building blocks that every Java developer must master before advancing to more complex topics.

---

## 1. Java Program Structure

### Basic Structure

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

**Key components:**
- **Class declaration**: Every Java file contains at least one class
- **main method**: Entry point - `public static void main(String[] args)`
- **Statements**: End with semicolon `;`
- **Blocks**: Curly braces `{ }` define scope

---

## 2. Primitive Data Types

Java has 8 primitive types (not objects):

| Type | Size | Range | Default |
|--------|------|-------|---------|
| `byte` | 8-bit | -128 to 127 | 0 |
| `short` | 16-bit | -32,768 to 32,767 | 0 |
| `int` | 32-bit | -2³¹ to 2³¹-1 | 0 |
| `long` | 64-bit | -2⁶³ to 2⁶³-1 | 0L |
| `float` | 32-bit | ~±3.4×10³⁸ | 0.0f |
| `double` | 64-bit | ~±1.7×10³⁰⁸ | 0.0d |
| `boolean` | 1-bit | true/false | false |
| `char` | 16-bit | Unicode 0 to 65,535 | '\u0000' |

### Literals

```java
int i = 42;
long l = 42L;           // L suffix required
float f = 3.14f;        // f suffix required
double d = 3.14;        // default double
char c = 'A';           // single quotes
boolean b = true;
String s = "hello";     // String is not primitive!
```

---

## 2. Variables & Scope

### Declaration & Initialization

```java
// Declaration
int x;
int x = 42;              // declaration + initialization
var x = 42;              // type inference (Java 10+)

// Multiple declarations
int a = 1, b = 2, c = 3;

// Constants (compile-time constants)
final int MAX_SIZE = 100;
final String APP_NAME = "MyApp";
```

### Scope Rules

```java
public class ScopeExample {
    int instanceVar = 1;        // Instance scope
    static int classVar = 2;    // Class scope
    
    void method() {
        int localVar = 3;       // Method scope
        if (true) {
            int blockVar = 4;   // Block scope
        }
        // blockVar not accessible here
    }
}
```

---

## 3. Operators

### Arithmetic
```java
int a = 10, b = 3;
int sum = a + b;        // 13
int diff = a - b;       // 7
int prod = a * b;       // 30
int quot = a / b;       // 3 (integer division!)
int rem = a % b;        // 1
```

### Comparison & Logical
```java
boolean eq = (a == b);
boolean neq = (a != b);
boolean gt = (a > b);
boolean and = (a > 0) && (b > 0);
boolean or = (a > 0) || (b > 0);
boolean not = !(a > 0);
```

### Bitwise
```java
int a = 6;  // 0110
int b = 3;  // 0011
int and = a & b;    // 2 (0010)
int or = a | b;     // 7 (0111)
int xor = a ^ b;    // 5 (0101)
int not = ~a;       // -7 (complement)
int left = a << 1;  // 12 (1100)
int right = a >> 1; // 3 (0011)
```

---

## 4. Control Flow

### if-else
```java
if (score >= 90) {
    grade = 'A';
} else if (score >= 80) {
    grade = 'B';
} else {
    grade = 'C';
}
```

### switch (Java 14+)
```java
String day = switch (dayNum) {
    case 1 -> "Monday";
    case 2 -> "Tuesday";
    case 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
    default -> "Invalid";
};
```

### Loops
```java
// for
for (int i = 0; i < 10; i++) { }

// for-each
for (String s : list) { }

// while
while (condition) { }

// do-while
do { } while (condition);
```

---

## 5. Methods

### Signature
```java
// access modifier + return type + name + parameters
public int add(int a, int b) {
    return a + b;
}

// Varargs
public int sum(int... numbers) {
    int sum = 0;
    for (int n : numbers) sum += n;
    return sum;
}

// Method overloading
public int add(int a, int b) { return a + b; }
public double add(double a, double b) { return a + b; }
```

### Pass-by-Value
```java
// Primitives: value copied
void modify(int x) { x = 10; }  // original unchanged

// Objects: reference copied
void modify(List<String> list) {
    list.add("new");  // modifies original!
}
```

---

## 6. Arrays

```java
// Declaration & initialization
int[] arr = new int[5];
int[] arr = {1, 2, 3, 4, 5};
int[][] matrix = new int[3][3];

// Access
int x = arr[0];
arr[0] = 10;

// Length
int len = arr.length;

// Iteration
for (int i = 0; i < arr.length; i++) { }
for (int x : arr) { }  // for-each
```

---

## 6. Strings

```java
String s1 = "hello";
String s2 = new String("hello");

// Immutable!
String s = "hello";
s.toUpperCase();  // returns NEW string, original unchanged

// Comparison
s1.equals(s2);           // content equality
s1 == s2;                // reference equality (avoid!)
s1.equalsIgnoreCase(s2); // case-insensitive

// Common operations
s.length();
s.charAt(0);
s.substring(0, 5);
s.toUpperCase();
s.trim();
s.split(",");
String.join(",", list);
```

---

## 8. Basic OOP Concepts

### Class Definition
```java
public class Person {
    // Fields
    private String name;
    private int age;
    
    // Constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Methods
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public void greet() {
        System.out.println("Hi, I'm " + name);
    }
}
```

### Access Modifiers
| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| `public` | ✓ | ✓ | ✓ | ✓ |
| `protected` | ✓ | ✓ | ✓ | ✗ |
| (default) | ✓ | ✓ | ✗ | ✗ |
| `private` | ✓ | ✗ | ✗ | ✗ |

---

## 9. Basic Exception Handling

```java
try {
    riskyOperation();
} catch (IOException e) {
    logger.error("IO failed", e);
} catch (Exception e) {
    logger.error("Error", e);
} finally {
    cleanup();
}

// Try-with-resources (auto-close)
try (FileReader fr = new FileReader("file.txt")) {
    // auto-closes
}
```

---

## 10. Packages & Imports

```java
package com.example.app;

import java.util.List;
import java.util.ArrayList;
import static java.util.Collections.*;

// Package naming: reverse domain
package com.company.project.module;
```

---

## 10. Essential APIs Quick Reference

| Task | Class/Method |
|------|-------------|
| Current time | `LocalDateTime.now()` |
| Format date | `DateTimeFormatter.ofPattern("yyyy-MM-dd").format(now)` |
| Read file | `Files.readString(Path.of("file.txt"))` |
| Write file | `Files.writeString(path, content)` |
| Parse int | `Integer.parseInt("42")` |
| Random int | `new Random().nextInt(100)` |
| Current thread | `Thread.currentThread().getName()` |
| Sleep | `Thread.sleep(1000)` |
| System props | `System.getProperty("user.home")` |

---

## 10. Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `==` for String comparison | Use `.equals()` |
| `==` for Integer > 127 | Use `.equals()` or `Objects.equals()` |
| Modifying collection during iteration | Use iterator or stream |
| `==` for enum | Safe (singletons) |
| `==` for String literals | Works due to interning, but use `.equals()` |
| Empty catch block | Always log or handle |
| `String +=` in loop | Use `StringBuilder` |