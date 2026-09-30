package com.learning.lambda;

import java.util.*;
import java.util.function.*;
import java.util.stream.*;

public class Lab {

    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("MODULE 10: LAMBDA EXPRESSIONS & FUNCTIONAL INTERFACES");
        System.out.println("=".repeat(60));

        part1LambdaBasics();
        part2FunctionalInterfaces();
        part3BuiltInFunctionalInterfaces();
        part4MethodReferences();
        part5VariableScoping();
        part6CollectionOperations();
        part7HigherOrderFunctions();
        part8CommonPatterns();

        System.out.println("\n" + "=".repeat(60));
        System.out.println("ALL DEMOS COMPLETED SUCCESSFULLY");
        System.out.println("=".repeat(60));
    }

    static void part1LambdaBasics() {
        System.out.println("\n### PART 1: Lambda Expression Basics ###\n");

        System.out.println("Lambda expression syntax:");
        System.out.println("  (parameters) -> expression");
        System.out.println("  (parameters) -> { statements; }");

        System.out.println("\nNo parameters:");
        Runnable r1 = () -> System.out.println("Hello");
        r1.run();

        System.out.println("\nSingle parameter (parentheses optional):");
        Consumer<String> c1 = s -> System.out.println(s);
        c1.accept("Hello World");

        System.out.println("\nMultiple parameters:");
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println("  add(5, 3) = " + add.apply(5, 3));

        System.out.println("\nMulti-statement body:");
        Function<Integer, String> convert = n -> {
            String result = "Number is: " + n;
            return result.toUpperCase();
        };
        System.out.println("  " + convert.apply(42));
    }

    static void part2FunctionalInterfaces() {
        System.out.println("\n### PART 2: Functional Interfaces ###\n");

        System.out.println("Functional interface = single abstract method (SAM):");
        System.out.println("  (MathOperation is a package-level @FunctionalInterface - see MathOperation.java)");

        MathOperation add = (a, b) -> a + b;
        MathOperation multiply = (a, b) -> a * b;
        MathOperation subtract = (a, b) -> a - b;

        System.out.println("  add(10, 5) = " + add.operate(10, 5));
        System.out.println("  multiply(10, 5) = " + multiply.operate(10, 5));
        System.out.println("  subtract(10, 5) = " + subtract.operate(10, 5));

        System.out.println("\nCustom functional interface with default methods:");
        interface Greeter {
            void greet(String name);
            default void greetLouder(String name) {
                greet(name.toUpperCase() + "!!!");
            }
        }

        Greeter g = name -> System.out.println("  Hello, " + name + "!");
        g.greet("World");
        g.greetLouder("World");
    }

    static void part3BuiltInFunctionalInterfaces() {
        System.out.println("\n### PART 3: Built-in Functional Interfaces (java.util.function) ###\n");

        System.out.println("Predicate<T> - test(T) -> boolean:");
        Predicate<String> isEmpty = s -> s.isEmpty();
        Predicate<String> isLong = s -> s.length() > 5;
        System.out.println("  isEmpty(\"\") = " + isEmpty.test(""));
        System.out.println("  isLong(\"Hello\") = " + isLong.test("Hello"));

        System.out.println("\nFunction<T,R> - apply(T) -> R:");
        Function<String, Integer> stringLength = String::length;
        Function<String, String> upperCase = String::toUpperCase;
        System.out.println("  length(\"Hello\") = " + stringLength.apply("Hello"));
        System.out.println("  upperCase(\"hello\") = " + upperCase.apply("hello"));

        System.out.println("\nConsumer<T> - accept(T) -> void:");
        Consumer<String> printer = s -> System.out.println("  Printing: " + s);
        Consumer<Integer> doublePrinter = n -> System.out.println("  " + n + " -> " + (n * 2));
        printer.accept("Hello");
        doublePrinter.accept(21);

        System.out.println("\nSupplier<T> - get() -> T:");
        Supplier<Double> randomSupplier = () -> Math.random();
        Supplier<List<String>> listSupplier = () -> List.of("A", "B", "C");
        System.out.println("  Random: " + randomSupplier.get());
        System.out.println("  List: " + listSupplier.get());

        System.out.println("\nBinaryOperator<T> - apply(T,T) -> T:");
        BinaryOperator<Integer> max = Integer::max;
        BinaryOperator<String> concat = (a, b) -> a + " " + b;
        System.out.println("  max(10, 20) = " + max.apply(10, 20));
        System.out.println("  concat(\"Hello\", \"World\") = " + concat.apply("Hello", "World"));

        System.out.println("\nUnaryOperator<T> - apply(T) -> T:");
        UnaryOperator<Integer> square = n -> n * n;
        UnaryOperator<String> reverse = s -> new StringBuilder(s).reverse().toString();
        System.out.println("  square(5) = " + square.apply(5));
        System.out.println("  reverse(\"Hello\") = " + reverse.apply("Hello"));
    }

    static void part4MethodReferences() {
        System.out.println("\n### PART 4: Method References ###\n");

        System.out.println("Static method reference: ClassName::staticMethod");
        Function<String, Integer> parseInt = Integer::parseInt;
        System.out.println("  parseInt(\"42\") = " + parseInt.apply("42"));

        System.out.println("\nInstance method of particular object: object::instanceMethod");
        String prefix = "Hello, ";
        Function<String, String> concat = prefix::concat;
        System.out.println("  concat(\"World\") = " + concat.apply("World"));

        System.out.println("\nInstance method of arbitrary object: ClassName::instanceMethod");
        Function<String, String> upper = String::toUpperCase;
        System.out.println("  upper(\"hello\") = " + upper.apply("hello"));

        System.out.println("\nConstructor reference: ClassName::new");
        Supplier<ArrayList<String>> listCreator = ArrayList::new;
        Supplier<HashMap<String, Integer>> mapCreator = HashMap::new;
        System.out.println("  New list: " + listCreator.get());
        System.out.println("  New map: " + mapCreator.get());

        System.out.println("\nCombining method references:");
        List<String> names = List.of("alice", "bob", "charlie");
        List<String> upperNames = names.stream()
            .map(String::toUpperCase)
            .collect(Collectors.toList());
        System.out.println("  " + upperNames);
    }

    static void part5VariableScoping() {
        System.out.println("\n### PART 5: Lambda Variable Scoping ###\n");

        System.out.println("Effectively final variables:");
        int effectivelyFinal = 10;
        Runnable r = () -> System.out.println("  Value: " + effectivelyFinal);
        r.run();

        System.out.println("\nAccessing instance variables:");
        class Counter {
            private int count = 0;
            public Runnable increment() {
                return () -> {
                    count++;
                    System.out.println("  count = " + count);
                };
            }
        }
        Counter counter = new Counter();
        counter.increment().run();
        counter.increment().run();

        System.out.println("\nShadowing and 'this' reference:");
        class Outer {
            String name = "Outer";
            Runnable getLambda() {
                return () -> System.out.println("  this.name = " + this.name);
            }
        }
        Outer outer = new Outer();
        outer.getLambda().run();

        System.out.println("\nCannot modify effectively final variables:");
        int counter2 = 0;
        // counter2++ // This would cause compile error - can't modify captured variable
        System.out.println("  (counter2 cannot be modified inside lambda)");
    }

    static void part6CollectionOperations() {
        System.out.println("\n### PART 6: Lambda with Collections ###\n");

        List<String> names = List.of("Alice", "Bob", "Charlie", "Diana", "Eve");

        System.out.println("Filtering with Predicate:");
        names.stream()
            .filter(s -> s.length() > 4)
            .forEach(s -> System.out.println("  " + s));

        System.out.println("\nTransforming with Function:");
        names.stream()
            .map(s -> s.toUpperCase())
            .forEach(s -> System.out.println("  " + s));

        System.out.println("\nFiltering and transforming:");
        names.stream()
            .filter(s -> s.startsWith("A") || s.startsWith("E"))
            .map(String::length)
            .forEach(n -> System.out.println("  " + n));

        System.out.println("\nSorting with Comparator:");
        names.stream()
            .sorted((a, b) -> b.compareTo(a))
            .forEach(s -> System.out.println("  " + s));

        System.out.println("\nFinding with Predicate:");
        names.stream()
            .filter(s -> s.length() == 3)
            .findFirst()
            .ifPresent(s -> System.out.println("  First 3-letter name: " + s));

        System.out.println("\nGrouping:");
        Map<Integer, List<String>> grouped = names.stream()
            .collect(Collectors.groupingBy(String::length));
        System.out.println("  Grouped by length: " + grouped);
    }

    static void part7HigherOrderFunctions() {
        System.out.println("\n### PART 7: Higher-Order Functions ###\n");

        System.out.println("Functions that return functions:");
        Function<Integer, UnaryOperator<Integer>> multiplier = n ->
            value -> value * n;

        UnaryOperator<Integer> times3 = multiplier.apply(3);
        System.out.println("  times3(5) = " + times3.apply(5));

        System.out.println("\nFunctions that accept functions:");
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);
        System.out.println("  Original: " + numbers);

        Function<List<Integer>, List<Integer>> doubleList = list ->
            list.stream().map(n -> n * 2).collect(Collectors.toList());
        System.out.println("  Doubled: " + doubleList.apply(numbers));

        System.out.println("\nComposing functions:");
        Function<Integer, Integer> add5 = n -> n + 5;
        Function<Integer, Integer> square = n -> n * n;
        Function<Integer, Integer> add5ThenSquare = square.compose(add5);
        Function<Integer, Integer> squareThenAdd5 = square.andThen(add5);

        System.out.println("  add5ThenSquare(3) = " + add5ThenSquare.apply(3));
        System.out.println("  squareThenAdd5(3) = " + squareThenAdd5.apply(3));

        System.out.println("\nCurrying:");
        Function<Integer, Function<Integer, Integer>> curriedAdd = a -> b -> a + b;
        Function<Integer, Integer> add10 = curriedAdd.apply(10);
        System.out.println("  add10(5) = " + add10.apply(5));
    }

    static void part8CommonPatterns() {
        System.out.println("\n### PART 8: Common Lambda Patterns ###\n");

        System.out.println("Null-safe operations with Optional:");
        String nullString = null;
        Optional.ofNullable(nullString)
            .ifPresentOrElse(
                s -> System.out.println("  Found: " + s),
                () -> System.out.println("  Not found")
            );

        System.out.println("\nConditional evaluation with Supplier:");
        boolean condition = false;
        Supplier<String> expensive = () -> {
            System.out.println("  Computing...");
            return "Expensive result";
        };
        String result = condition ? expensive.get() : "Default";
        System.out.println("  Result: " + result);

        System.out.println("\nCollection filtering pattern:");
        List<Integer> nums = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        List<Integer> evens = nums.stream()
            .filter(n -> n % 2 == 0)
            .collect(Collectors.toList());
        List<Integer> odds = nums.stream()
            .filter(n -> n % 2 != 0)
            .collect(Collectors.toList());
        System.out.println("  Evens: " + evens);
        System.out.println("  Odds: " + odds);

        System.out.println("\nReduction pattern:");
        int sum = nums.stream().reduce(0, Integer::sum);
        int product = nums.stream().reduce(1, (a, b) -> a * b);
        System.out.println("  Sum: " + sum);
        System.out.println("  Product: " + product);

        System.out.println("\nPartitioning pattern:");
        Map<Boolean, List<Integer>> partitioned = nums.stream()
            .collect(Collectors.partitioningBy(n -> n > 5));
        System.out.println("  Partitioned (>5): " + partitioned);

        System.out.println("\nChaining consumers:");
        Consumer<String> chain = System.out::println;
        chain = chain.andThen(s -> System.out.println("  [logged]"));
        chain.accept("Test message");
    }
}