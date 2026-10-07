# Code Deep Dive — Java Generics Mastery (generics)

Six runnable snippets that follow generics from the declaration (bounds, wildcards) down to what the compiler leaves in the class file (erasure, bridge methods) and up again to the workarounds for erased information (type tokens).

How to use this file: each snippet is a complete single-file program. Save it as `<ClassName>.java`, compile with `javac --release 21 -proc:none <ClassName>.java`, then run the command shown under it. Every snippet targets Java 21 without preview features and uses only the JDK. The "Observed output" blocks were produced by compiling and running the snippets on JDK 23.0.1 (Windows), with `--release 21`.

## Snippet 1: type parameters & bounds

A bound such as `T extends Comparable<? super T>` restricts which types may be substituted for `T` and lets the method body call the bound's methods (`compareTo`) without casts. The `? super T` part matters: a `Dog` inherits `Comparable<Animal>` from `Animal`, which is not `Comparable<Dog>`, so only the `? super` form accepts a list of `Dog`. An intersection bound (`Number & Comparable<T>`) lists a class first and then interfaces, and after erasure `T` becomes the leftmost bound.

```java
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Set;

public class TypeBounds {
    static class Animal implements Comparable<Animal> {
        final String name;
        final int weightKg;

        Animal(String name, int weightKg) {
            this.name = name;
            this.weightKg = weightKg;
        }

        @Override public int compareTo(Animal other) { return Integer.compare(weightKg, other.weightKg); }
        @Override public String toString() { return getClass().getSimpleName() + "(" + name + "," + weightKg + ")"; }
    }

    static class Dog extends Animal {
        Dog(String name, int weightKg) { super(name, weightKg); }
    }

    // Accepts any collection whose elements can be compared with T or a supertype of T.
    static <T extends Comparable<? super T>> T max(Collection<? extends T> items) {
        Iterator<? extends T> it = items.iterator();
        T best = it.next();                  // throws NoSuchElementException when empty
        while (it.hasNext()) {
            T candidate = it.next();
            if (candidate.compareTo(best) > 0) {
                best = candidate;
            }
        }
        return best;
    }

    // Too strict: T itself must implement Comparable<T>, so Dog is rejected (Animal implements Comparable<Animal>).
    static <T extends Comparable<T>> T maxStrict(Collection<T> items) {
        return max(items);
    }

    // Intersection bound: a class (Number) first, then interfaces.
    static <T extends Number & Comparable<T>> T clamp(T value, T lo, T hi) {
        if (value.compareTo(lo) < 0) return lo;
        if (value.compareTo(hi) > 0) return hi;
        return value;
    }

    public static void main(String[] args) {
        System.out.println("max(3,8,5)       = " + max(List.of(3, 8, 5)));
        System.out.println("max(kiwi)        = " + max(Set.of("kiwi")));

        List<Dog> dogs = List.of(new Dog("rex", 30), new Dog("fido", 12), new Dog("max", 41));
        Dog heaviest = max(dogs);            // T = Dog, bound is Comparable<Animal>, Animal is a supertype of Dog
        System.out.println("max(dogs)        = " + heaviest);

        List<Animal> animals = List.of(new Animal("cat", 4), new Animal("cow", 600));
        System.out.println("maxStrict(animals) = " + maxStrict(animals));

        System.out.println("clamp(15, 0, 10)  = " + clamp(15, 0, 10));
        System.out.println("clamp(2.5, 3.0, 4.0) = " + clamp(2.5, 3.0, 4.0));

        try {
            max(new ArrayList<Integer>());
        } catch (NoSuchElementException e) {
            System.out.println("max(empty list)  -> NoSuchElementException");
        }
    }
}
```

Run: `java TypeBounds`

Observed output:
```text
max(3,8,5)       = 8
max(kiwi)        = kiwi
max(dogs)        = Dog(max,41)
maxStrict(animals) = Animal(cow,600)
clamp(15, 0, 10)  = 10
clamp(2.5, 3.0, 4.0) = 3.0
max(empty list)  -> NoSuchElementException
```

**Pitfall:** the natural-looking signature `<T extends Comparable<T>>` (as in `maxStrict`) works for `List<Animal>` but rejects `List<Dog>`, even though every `Dog` is comparable to every other `Dog`. Calling `maxStrict(dogs)` from the snippet above fails to compile with:
```text
TypeBounds.java:62: error: method maxStrict in class TypeBounds cannot be applied to given types;
        maxStrict(dogs);
        ^
  required: Collection<T>
  found:    List<Dog>
  reason: inference variable T has incompatible equality constraints Animal,Dog
  where T is a type-variable:
    T extends Comparable<T> declared in method <T>maxStrict(Collection<T>)
1 error
```
(Produced by adding that one call to a scratch copy of the snippet.) Declare comparison bounds as `Comparable<? super T>`, which is what `Collections.max` does.

## Snippet 2: wildcards PECS

PECS (Producer Extends, Consumer Super) is the rule for choosing a wildcard: a collection you only read from is `? extends T`, one you only write to is `? super T`. `List<? extends Number>` can be a `List<Integer>` or a `List<Double>`, so reading yields a `Number` but the compiler forbids `add` because it cannot know the real element type. `List<? super Integer>` can be a `List<Number>` or `List<Object>`, so adding an `Integer` is always safe but reading yields only `Object`. A method taking `List<?>` can call a private generic helper to give the captured wildcard a name.

```java
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class WildcardsPecs {
    // src produces T values, dst consumes them.
    static <T> void copy(List<? super T> dst, List<? extends T> src) {
        for (T item : src) {
            dst.add(item);
        }
    }

    static double sum(Collection<? extends Number> numbers) {
        double total = 0;
        for (Number n : numbers) {
            total += n.doubleValue();
        }
        return total;
    }

    static void fillWithInts(List<? super Integer> sink, int count) {
        for (int i = 0; i < count; i++) {
            sink.add(i);
        }
    }

    // List<?> hides the element type; the helper captures it as T so elements can be swapped.
    static void reverseAny(List<?> list) {
        reverse(list);
    }

    private static <T> void reverse(List<T> list) {
        for (int i = 0, j = list.size() - 1; i < j; i++, j--) {
            T tmp = list.get(i);
            list.set(i, list.get(j));
            list.set(j, tmp);
        }
    }

    public static void main(String[] args) {
        List<Integer> ints = List.of(1, 2, 3);
        List<Double> doubles = List.of(0.5, 1.5);
        System.out.println("sum(ints)    = " + sum(ints));
        System.out.println("sum(doubles) = " + sum(doubles));

        List<Number> numbers = new ArrayList<>();
        copy(numbers, ints);
        copy(numbers, doubles);
        System.out.println("numbers      = " + numbers);

        List<Object> objects = new ArrayList<>();
        fillWithInts(objects, 3);
        List<? super Integer> sink = objects;
        Object first = sink.get(0);          // the only static type available when reading
        System.out.println("objects      = " + objects + ", first read as Object = " + first);

        List<String> words = new ArrayList<>(List.of("a", "b", "c", "d"));
        reverseAny(words);
        System.out.println("reversed     = " + words);

        List<? extends Number> readOnlyView = new ArrayList<>(ints);
        Number head = readOnlyView.get(0);
        System.out.println("head         = " + head + " (static type Number, runtime " + head.getClass().getSimpleName() + ")");
    }
}
```

Run: `java WildcardsPecs`

Observed output:
```text
sum(ints)    = 6.0
sum(doubles) = 2.0
numbers      = [1, 2, 3, 0.5, 1.5]
objects      = [0, 1, 2], first read as Object = 0
reversed     = [d, c, b, a]
head         = 1 (static type Number, runtime Integer)
```

**Pitfall:** the restriction is enforced at compile time and is easy to misread as a bug. Adding `readOnlyView.add(4)` to the snippet above is rejected:
```text
WildcardsPecs.java:62: error: incompatible types: int cannot be converted to CAP#1
        readOnlyView.add(4);
                         ^
  where CAP#1 is a fresh type-variable:
    CAP#1 extends Number from capture of ? extends Number
Note: Some messages have been simplified; recompile with -Xdiags:verbose to get full output
1 error
```
(Produced by adding that line to a scratch copy.) The usual wrong fix is to change the parameter to `List<Number>`, which then refuses `List<Integer>` arguments; the right fix is to decide whether the method produces or consumes, and apply `extends` or `super` accordingly.

## Snippet 3: erasure & bridge methods

After type checking, javac erases type parameters to their bounds and inserts casts where erased values are used. When a subclass overrides a generic method with a concrete signature (`compareTo(Name)` for `Comparable<Name>.compareTo(T)`), the erased signatures differ, so javac generates a synthetic bridge method `compareTo(Object)` that casts its argument and calls the real one. The declarations still carry generic information in the class file's `Signature` attribute, which is why reflection can print `Comparable<ErasureBridge$Name>` even though the instances themselves know nothing about their type arguments.

```java
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class ErasureBridge {
    static class Name implements Comparable<Name> {
        final String value;

        Name(String value) { this.value = value; }

        @Override public int compareTo(Name other) { return value.compareTo(other.value); }
        @Override public String toString() { return "Name(" + value + ")"; }
    }

    static abstract class Handler<T> {
        abstract String handle(T input);
    }

    static class StringHandler extends Handler<String> {
        @Override String handle(String input) { return input.toUpperCase(); }
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    static int rawCompare(Comparable a, Object b) {
        return a.compareTo(b);
    }

    static void printMethods(Class<?> type) {
        Method[] methods = type.getDeclaredMethods();
        Arrays.sort(methods, Comparator.comparing(m -> m.getName() + Arrays.toString(m.getParameterTypes())));
        System.out.println(type.getSimpleName() + " declares:");
        for (Method m : methods) {
            System.out.println("  " + m.getReturnType().getSimpleName() + " " + m.getName()
                    + Arrays.stream(m.getParameterTypes()).map(Class::getSimpleName).toList()
                    + "  bridge=" + m.isBridge() + " synthetic=" + m.isSynthetic());
        }
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    static void callHandlerRaw(Handler handler, Object arg) {
        handler.handle(arg);
    }

    public static void main(String[] args) throws Exception {
        printMethods(Name.class);
        printMethods(StringHandler.class);

        System.out.println("declared supertype of Name : " + Arrays.toString(Name.class.getGenericInterfaces()));
        System.out.println("same class for List<String> and List<Integer>? "
                + (new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()));
        System.out.println("erased parameter of Handler.handle: "
                + Handler.class.getDeclaredMethod("handle", Object.class).getParameterTypes()[0].getName());

        System.out.println("rawCompare(Name(a), Name(b)) = " + rawCompare(new Name("a"), new Name("b")));
        try {
            rawCompare(new Name("a"), 5);
        } catch (ClassCastException e) {
            System.out.println("CCE message : " + e.getMessage());
            StackTraceElement top = e.getStackTrace()[0];
            System.out.println("CCE top frame: " + top);
        }

        try {
            callHandlerRaw(new StringHandler(), 42);
        } catch (ClassCastException e) {
            System.out.println("raw handle(42) -> " + e.getClass().getSimpleName()
                    + " thrown from " + e.getStackTrace()[0].getMethodName());
        }
    }
}
```

Run: `java ErasureBridge`

Observed output:
```text
Name declares:
  int compareTo[Name]  bridge=false synthetic=false
  int compareTo[Object]  bridge=true synthetic=true
  String toString[]  bridge=false synthetic=false
StringHandler declares:
  String handle[Object]  bridge=true synthetic=true
  String handle[String]  bridge=false synthetic=false
declared supertype of Name : [java.lang.Comparable<ErasureBridge$Name>]
same class for List<String> and List<Integer>? true
erased parameter of Handler.handle: java.lang.Object
rawCompare(Name(a), Name(b)) = -1
CCE message : class java.lang.Integer cannot be cast to class ErasureBridge$Name (java.lang.Integer is in module java.base of loader 'bootstrap'; ErasureBridge$Name is in unnamed module of loader 'app')
CCE top frame: ErasureBridge$Name.compareTo(ErasureBridge.java:8)
raw handle(42) -> ClassCastException thrown from handle
```

**Pitfall:** the `ClassCastException` from `rawCompare(new Name("a"), 5)` is thrown inside `Name.compareTo`, a method whose source you never wrote: the top frame is the compiler-generated bridge, and its line number is that of the class declaration. In a real code base this shows up as a failure inside a plain `Comparable` or `Comparator` implementation, caused by whoever passed the wrong object through a raw or unchecked call several frames up. Look for the first frame outside the bridge to find the culprit.

## Snippet 4: generic methods

A generic method declares its own type parameters before the return type, and the compiler infers them from the arguments and from the assignment target; you can override inference with an explicit type witness such as `GenericMethods.<Number>listOf2(...)`. Inside a generic method `T` is erased, so `new T[n]` is illegal and a `T...` varargs parameter is compiled as an `Object[]`. A varargs method is only safe if it does not let that array escape, which is what `@SafeVarargs` asserts.

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class GenericMethods {
    static <T> List<T> listOf2(T a, T b) {
        List<T> out = new ArrayList<>();
        out.add(a);
        out.add(b);
        return out;
    }

    static <K, V extends Comparable<V>> K argMax(Map<K, V> map) {
        K bestKey = null;
        V bestValue = null;
        for (Map.Entry<K, V> e : map.entrySet()) {
            if (bestValue == null || e.getValue().compareTo(bestValue) > 0) {
                bestKey = e.getKey();
                bestValue = e.getValue();
            }
        }
        return bestKey;
    }

    @SafeVarargs                              // safe: the array never leaves the method
    static <T> List<T> listOf(T... items) {
        List<T> out = new ArrayList<>();
        for (T item : items) {
            out.add(item);
        }
        return out;
    }

    @SuppressWarnings("unchecked")            // unsafe: returns the caller-created varargs array
    static <T> T[] toArray(T... items) {
        return items;
    }

    @SuppressWarnings("unchecked")
    static <T> T[] pick3(T a, T b, T c) {
        return toArray(a, b, c);              // here T is erased, so the array is created as Object[]
    }

    public static void main(String[] args) {
        List<Object> mixed = listOf2(1, "a");               // T inferred as Object from the target type
        System.out.println("mixed          = " + mixed);

        List<Number> witness = GenericMethods.<Number>listOf2(1, 2.5);
        System.out.println("witness        = " + witness);

        System.out.println("argMax         = " + argMax(Map.of("a", 3, "b", 9, "c", 5)));
        System.out.println("listOf(1,2,3)  = " + listOf(1, 2, 3));

        Object[] asObjects = pick3("x", "y", "z");
        System.out.println("pick3 as Object[] works, runtime array class = " + asObjects.getClass().getSimpleName());

        try {
            String[] asStrings = pick3("x", "y", "z");
            System.out.println("unreachable " + asStrings.length);
        } catch (ClassCastException e) {
            System.out.println("pick3 as String[] -> ClassCastException: " + e.getMessage());
        }
    }
}
```

Run: `java GenericMethods`

Observed output:
```text
mixed          = [1, a]
witness        = [1, 2.5]
argMax         = b
listOf(1,2,3)  = [1, 2, 3]
pick3 as Object[] works, runtime array class = Object[]
pick3 as String[] -> ClassCastException: class [Ljava.lang.Object; cannot be cast to class [Ljava.lang.String; ([Ljava.lang.Object; and [Ljava.lang.String; are in module java.base of loader 'bootstrap')
```

**Pitfall:** `pick3("x", "y", "z")` compiles without error for both `Object[]` and `String[]`, but the second assignment throws, because the array was created inside `pick3` where `T` was already erased. The compiler warns only at the declaration of `toArray` (`Possible heap pollution from parameterized vararg type`), not at the use site. Never return or store a `T...` array; copy it into a `List<T>`, or take a `Class<T>` / `IntFunction<T[]>` and create the array with the real component type.

## Snippet 5: variance

Arrays are covariant (`Dog[]` is a subtype of `Animal[]`) and check every store at run time, while generic types are invariant (`List<Dog>` is not a `List<Animal>`) and rely on wildcards for flexibility. Variance in Java is declared at the use site: `? extends` gives covariance for reading, `? super` gives contravariance for writing. That is why `List<Dog>.sort` accepts a `Comparator<Animal>`: its parameter is `Comparator<? super Dog>`.

```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.function.Function;

public class Variance {
    static class Animal {
        String sound() { return "..."; }
        Animal copy() { return new Animal(); }
    }

    static class Dog extends Animal {
        @Override String sound() { return "woof"; }
        @Override Dog copy() { return new Dog(); }          // covariant return type
    }

    static class Cat extends Animal {
        @Override String sound() { return "meow"; }
    }

    static void arrayTrap() {
        Animal[] animals = new Dog[2];                     // compiles: arrays are covariant
        animals[0] = new Dog();
        try {
            animals[1] = new Cat();                        // compiles too, fails at run time
        } catch (ArrayStoreException e) {
            System.out.println("ArrayStoreException: " + e.getMessage());
        }
    }

    static String chorus(List<? extends Animal> animals) {
        StringBuilder sb = new StringBuilder();
        for (Animal a : animals) {
            sb.append(a.sound()).append(' ');
        }
        return sb.toString().trim();
    }

    static void addPuppy(List<? super Dog> sink) {
        sink.add(new Dog());
    }

    public static void main(String[] args) {
        arrayTrap();

        List<Dog> dogs = new ArrayList<>(List.of(new Dog(), new Dog()));
        // List<Animal> asAnimals = dogs;                   // does not compile: generics are invariant
        System.out.println("chorus(dogs)    = " + chorus(dogs));

        List<Animal> animals = new ArrayList<>();
        List<Object> objects = new ArrayList<>();
        addPuppy(animals);
        addPuppy(objects);
        System.out.println("sizes after addPuppy: animals=" + animals.size() + " objects=" + objects.size());

        Comparator<Animal> bySound = Comparator.comparing(Animal::sound);
        dogs.sort(bySound);                                 // accepts Comparator<? super Dog>
        System.out.println("sorted dogs with a Comparator<Animal>, first = " + dogs.get(0).sound());

        Function<Animal, String> describe = a -> "an animal that says " + a.sound();
        Function<? super Dog, ? extends CharSequence> asDogFunction = describe;
        System.out.println(asDogFunction.apply(new Dog()));

        Dog puppy = new Dog().copy();                       // no cast needed thanks to the covariant return
        System.out.println("copy() returned " + puppy.getClass().getSimpleName());
    }
}
```

Run: `java Variance`

Observed output:
```text
ArrayStoreException: Variance$Cat
chorus(dogs)    = woof woof
sizes after addPuppy: animals=1 objects=1
sorted dogs with a Comparator<Animal>, first = woof
an animal that says woof
copy() returned Dog
```

**Pitfall:** `animals[1] = new Cat()` is legal Java and is rejected only when it executes, with an `ArrayStoreException` that names the offending class and nothing else. Because the declared type of `animals` is `Animal[]`, neither the compiler nor a code reviewer sees the problem; the same code with `List<Animal> animals = dogs` is stopped at compile time. Prefer generic collections over arrays at API boundaries; when an array is unavoidable, do not pass a `Dog[]` where an `Animal[]` is written to.

## Snippet 6: type tokens

Because `List<String>` is erased, a method cannot receive "the type" of a generic argument at run time. A `Class<T>` token carries the type for non-generic classes: `Class.cast` checks values and `Class<T>` as a map key makes a typesafe heterogeneous container. For parameterized types the workaround is a super type token: an anonymous subclass `new TypeRef<List<String>>() {}` records its type argument in the class file's `Signature` attribute, and `getGenericSuperclass()` reads it back.

```java
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class TypeTokens {
    static class Favorites {
        private final Map<Class<?>, Object> values = new HashMap<>();

        <T> void put(Class<T> type, T value) {
            values.put(Objects.requireNonNull(type), type.cast(value));   // cast() re-checks at run time
        }

        <T> T get(Class<T> type) {
            return type.cast(values.get(type));
        }
    }

    static class TypeRef<T> {
        final Type type;

        protected TypeRef() {
            Type superclass = getClass().getGenericSuperclass();
            if (!(superclass instanceof ParameterizedType parameterized)) {
                throw new IllegalStateException("not subclassed with a type argument; superclass is " + superclass);
            }
            this.type = parameterized.getActualTypeArguments()[0];
        }
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    static void putThroughRawToken(Favorites favorites, Class token, Object value) {
        favorites.put(token, value);
    }

    public static void main(String[] args) {
        Favorites favorites = new Favorites();
        favorites.put(String.class, "java");
        favorites.put(Integer.class, 21);
        String s = favorites.get(String.class);                // no cast at the call site
        int n = favorites.get(Integer.class);
        System.out.println("String favorite = " + s + ", Integer favorite = " + n);

        favorites.put(List.class, List.of("a", "b"));          // List.class is the raw List: parameters are lost
        favorites.put(List.class, List.of(1, 2, 3));           // same key, silently replaces the previous list
        System.out.println("List favorite    = " + favorites.get(List.class));

        try {
            putThroughRawToken(favorites, Integer.class, "not an int");
        } catch (ClassCastException e) {
            System.out.println("rejected by Class.cast: " + e.getMessage());
        }

        Type listOfString = new TypeRef<List<String>>() {}.type;
        Type nested = new TypeRef<Map<String, List<Integer>>>() {}.type;
        System.out.println("captured type 1 = " + listOfString.getTypeName());
        System.out.println("captured type 2 = " + nested.getTypeName());
        System.out.println("raw type of 1   = " + ((ParameterizedType) listOfString).getRawType().getTypeName());

        try {
            new TypeRef<List<String>>();                       // forgot the {}: nothing is recorded
        } catch (IllegalStateException e) {
            System.out.println("without {} -> " + e.getMessage());
        }
    }
}
```

Run: `java TypeTokens`

Observed output:
```text
String favorite = java, Integer favorite = 21
List favorite    = [1, 2, 3]
rejected by Class.cast: Cannot cast java.lang.String to java.lang.Integer
captured type 1 = java.util.List<java.lang.String>
captured type 2 = java.util.Map<java.lang.String, java.util.List<java.lang.Integer>>
raw type of 1   = java.util.List
without {} -> not subclassed with a type argument; superclass is class java.lang.Object
```

**Pitfall:** `List<String>.class` does not exist, so `Favorites` cannot distinguish a `List<String>` from a `List<Integer>`: the second `put(List.class, ...)` in the output silently replaced the first. The super type token fixes the key but has its own trap: forgetting the trailing `{}` (so no anonymous subclass is created) leaves nothing to reflect on, and the failure surfaces at run time as the `IllegalStateException` shown above. Also note that the anonymous subclass captures its enclosing instance in non-static contexts, so a token created inside a long-lived object can keep that object alive.

## Pitfalls summary

| Topic | Concrete failure | How to catch it |
|---|---|---|
| type parameters & bounds | `T extends Comparable<T>` rejects `List<Dog>` | write `Comparable<? super T>` |
| wildcards PECS | `add` on `List<? extends Number>` does not compile | decide producer vs consumer first |
| erasure & bridge methods | `ClassCastException` thrown from a synthetic bridge, line = class declaration | find the first frame outside the bridge; avoid raw calls |
| generic methods | `T...` array returned to a `String[]` variable throws at the call site | never expose a generic varargs array |
| variance | `Animal[] a = new Dog[2]; a[1] = new Cat()` throws `ArrayStoreException` | use `List` instead of arrays at API boundaries |
| type tokens | `List.class` merges every `List<X>`; missing `{}` loses the type | use a super type token with an anonymous subclass |
