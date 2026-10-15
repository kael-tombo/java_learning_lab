# Pass-By-Value Code Deep Dive

This lab provides pure Java examples that definitively prove Java is Pass-By-Value, demonstrating the difference between mutating an object and reassigning a reference.

## 💻 Pure Java Implementation

```java file="labs/java/fundamentals/pass-by-value/SOLUTION/PassByValueDemo.java"
package fundamentals.passbyvalue;

/**
 * A demonstration of Java's strict Pass-By-Value semantics.
 */
public class PassByValueDemo {

    // A simple mutable class
    static class Person {
        String name;
        Person(String name) { this.name = name; }
        @Override public String toString() { return name; }
    }

    public static void main(String[] args) {
        System.out.println("--- 1. Passing Primitives ---");
        int originalInt = 10;
        System.out.println("Before method: " + originalInt);
        modifyPrimitive(originalInt);
        System.out.println("After method:  " + originalInt + " (Unchanged)\n");

        System.out.println("--- 2. Passing Object References (Mutation) ---");
        Person personA = new Person("Alice");
        System.out.println("Before method: " + personA);
        mutateObject(personA);
        System.out.println("After method:  " + personA + " (Mutated!)\n");

        System.out.println("--- 3. Passing Object References (Reassignment) ---");
        Person personB = new Person("Bob");
        System.out.println("Before method: " + personB);
        reassignObject(personB);
        System.out.println("After method:  " + personB + " (Unchanged!)\n");
        
        System.out.println("--- 4. The Classic Swap Interview Question ---");
        Person p1 = new Person("One");
        Person p2 = new Person("Two");
        System.out.println("Before swap: p1=" + p1 + ", p2=" + p2);
        swap(p1, p2);
        System.out.println("After swap:  p1=" + p1 + ", p2=" + p2 + " (Swap Failed!)");
    }

    /**
     * Receives a copy of the primitive value.
     */
    private static void modifyPrimitive(int x) {
        x = 99; // Only changes the local copy
    }

    /**
     * Receives a copy of the memory address.
     * Uses the address to reach into the Heap and change the object's internal state.
     */
    private static void mutateObject(Person p) {
        p.name = "Alice_Mutated"; 
    }

    /**
     * Receives a copy of the memory address.
     * Reassigns the local variable to point to a brand new object on the Heap.
     * This does NOT affect the caller's variable.
     */
    private static void reassignObject(Person p) {
        p = new Person("Charlie"); // The caller never sees this new object
    }

    /**
     * A classic trick question. 
     * Because Java passes copies of references, swapping the copies locally 
     * does absolutely nothing to the original references in the caller method.
     */
    private static void swap(Person a, Person b) {
        Person temp = a;
        a = b;
        b = temp;
    }
}
```

## 🔍 Key Takeaways
1. **The Swap Failure**: The `swap` method is the ultimate proof that Java is Pass-By-Value. In a language with true Pass-By-Reference (like C++ with `&`), a swap method works perfectly. In Java, you are only swapping the *copies* of the memory addresses inside the local stack frame. When the method returns, those copies are destroyed, and `main`'s variables remain completely unchanged.
2. **Immutability is Safer**: Because passing an object allows the receiving method to mutate its internal state (as seen in `mutateObject`), defensive programming often relies on immutable objects (like `String` or Java 14 `record`s). If an object has no setter methods, you can safely pass it anywhere without fear of unexpected side effects.