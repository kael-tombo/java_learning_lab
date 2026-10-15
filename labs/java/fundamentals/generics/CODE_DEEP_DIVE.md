# Generics Code Deep Dive

This lab demonstrates the practical application of the PECS principle and the limitations of Type Erasure.

## 💻 Pure Java Implementation

```java file="labs/java/fundamentals/generics/SOLUTION/GenericsPecsDemo.java"
package fundamentals.generics;

import java.util.ArrayList;
import java.util.List;

/**
 * A demonstration of the PECS (Producer Extends, Consumer Super) principle.
 */
public class GenericsPecsDemo {

    static class Animal { String name; }
    static class Cat extends Animal { }
    static class Dog extends Animal { }

    /**
     * PRODUCER: Uses '? extends'.
     * We can READ Animals from this list, but we cannot add anything to it.
     */
    public static void printAnimalNames(List<? extends Animal> animals) {
        for (Animal a : animals) {
            System.out.println(a.getClass().getSimpleName());
        }
        // animals.add(new Cat()); // ❌ COMPILE ERROR!
    }

    /**
     * CONSUMER: Uses '? super'.
     * We can ADD Cats to this list safely.
     */
    public static void addCats(List<? super Cat> cats) {
        cats.add(new Cat());
        // Cat c = cats.get(0); // ❌ COMPILE ERROR! (Returns Object, not Cat)
    }

    public static void main(String[] args) {
        List<Cat> myCats = new ArrayList<>();
        myCats.add(new Cat());

        // 1. Cat list works for '? extends Animal' (Producer)
        printAnimalNames(myCats);

        // 2. Animal list works for '? super Cat' (Consumer)
        List<Animal> myAnimals = new ArrayList<>();
        addCats(myAnimals);
        
        System.out.println("Animals list size after adding cat: " + myAnimals.size());
        
        // 3. Proving Type Erasure
        List<String> strings = new ArrayList<>();
        List<Integer> ints = new ArrayList<>();
        
        System.out.println("\n--- Type Erasure Proof ---");
        System.out.println("List<String> class: " + strings.getClass().getName());
        System.out.println("List<Integer> class: " + ints.getClass().getName());
        System.out.println("Are they the same class? " + (strings.getClass() == ints.getClass()));
    }
}
```

## 🔍 Key Takeaways
1. **The 'extends' Trap**: Beginners often try to use `List<? extends Animal>` to add a `Cat`. This fails because the list could actually be a `List<Dog>`. The compiler forbids adding anything (except `null`) to an `extends` wildcard to maintain safety.
2. **The 'super' Benefit**: `List<? super Cat>` allows you to pass a `List<Animal>` or even a `List<Object>`. You can safely add a `Cat` because a `Cat` *is* an `Animal` and an `Object`.
3. **Erasure in Practice**: The final check in `main` proves that at runtime, the generic type information is gone. Both lists report being of class `java.util.ArrayList`.