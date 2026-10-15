# Quiz - Java Fundamentals (fundamentals)

20 questions on syntax, types, OOP, exceptions, generics, collections, streams, JVM. Aim 16/20. Key at end.
Q1: What does `7 / 2` evaluate to in Java?
- A) 3.5 B) 3 C) 4 D) compile error
Q2: What is the value of `Integer.MAX_VALUE + 1`?
- A) 2147483648 B) 0 C) it wraps to -2147483648 D) it throws ArithmeticException
Q3: What does `"ab" == new String("ab")` evaluate to?
- A) compile error B) true C) false D) true only on JDK 21+
Q4: Which is true of a switch expression using `->` arms, like `switch (s / 10) { case 10, 9 -> "A"; ... }`?
- A) each arm needs `break` B) it produces a value with no `break` needed C) it cannot have a `default` arm D) it only accepts String selectors
Q5: Which design best demonstrates encapsulation?
- A) all fields public B) all methods static C) no constructors allowed D) private state exposed only through methods
Q6: Given `Shape s = new Circle(1.0); s.area();` where Circle overrides area, what runs?
- A) Circle.area, chosen by runtime dispatch B) Shape.area directly C) it fails to compile D) whichever method was written first
Q7: Which declaration correctly gives class C the members of class Shape?
- A) `class C implements Shape` where Shape is a class B) `class C imports Shape` C) `class C extends Shape` D) `class C inherits Shape`
Q8: A class implementing an interface with a default method:
- A) must redeclare every Object method B) cannot be instantiated C) must be abstract D) inherits the default method unless it overrides it
Q9: Which statement about `IOException` is true?
- A) it is checked: must be caught or declared with throws B) it is unchecked like NullPointerException C) it can never be caught D) it is an Error, not an Exception
Q10: `Integer.parseInt("x9")` throws NumberFormatException. How must callers handle it?
- A) declare `throws` or the code will not compile B) catching is optional: it is unchecked C) it cannot be caught D) only test code may catch it
Q11: What does try-with-resources guarantee for `try (Scanner sc = new Scanner("7"))`?
- A) the Scanner is never created B) sc stays open for reuse C) sc.close() runs automatically D) exceptions are silently swallowed
Q12: After erasure, what does `new Box<String>("x").getClass() == new Box<Integer>(1).getClass()` yield?
- A) false: each type argument gets its own class B) compile error C) true: one Box class at runtime D) true only with reflection
Q13: What happens with raw types: `List xs = new ArrayList<String>(); xs.add(42);`?
- A) compiles with an unchecked warning; the Integer corrupts String expectations B) compile error C) throws at the add call D) the 42 is auto-converted to "42"
Q14: What is the time cost of `ArrayList.get(i)` by index?
- A) O(n) B) O(1) C) O(log n) D) O(n log n)
Q15: What is the average time cost of HashMap get/put with a good hash function?
- A) O(n) B) O(log n) C) O(1) average, O(n) worst case D) O(n log n)
Q16: `List.of(1,2,3,4,5).stream().filter(n -> n % 2 == 0).map(n -> n * 10).toList()` gives:
- A) [1, 2, 3, 4, 5] B) [2, 4] C) [20, 40] D) an empty list
Q17: Sorting `["pear","fig","kiwi"]` with `(x, y) -> Integer.compare(x.length(), y.length())` gives:
- A) [fig, kiwi, pear] B) [kiwi, pear, fig] C) [pear, fig, kiwi] D) [fig, pear, kiwi]
Q18: Which `var` usage compiles?
- A) `var x;` B) `var x = null;` C) `var y = 1; y = "s";` D) `var x = 5;`
Q19: For `record Point(int x, int y)`, which is true?
- A) fields are mutable B) equals/compare must be hand-written C) it cannot have methods D) it auto-provides equals, hashCode, toString, accessors
Q20: What does `java -cp out Main hi` do?
- A) compiles Main.java B) runs Main.main with args ["hi"] using out as classpath C) prints the bytecode D) starts jshell
## Answer key
1. B - int division truncates: 7/2 is 3
2. C - int overflow wraps to Integer.MIN_VALUE
3. C - == compares references; use equals for content
4. B - arrow switch expressions yield values, no break
5. D - private state plus methods is encapsulation
6. A - overridden methods dispatch at runtime
7. C - extends inherits from one superclass
8. D - default methods are inherited unless overridden
9. A - IOException is checked
10. B - NumberFormatException is an unchecked RuntimeException
11. C - AutoCloseable resources close automatically
12. C - erasure leaves a single Box class at runtime
13. A - raw types compile with warnings and defer failure to runtime
14. B - array-backed index access is O(1)
15. C - hashing gives O(1) average
16. C - evens doubled by ten: [20, 40]
17. D - stable sort by length: fig(3), pear(4), kiwi(4)
18. D - var needs an initializer with an inferable type; its type is then fixed
19. D - records derive value semantics and accessors
20. B - java launches with classpath out and argument hi
