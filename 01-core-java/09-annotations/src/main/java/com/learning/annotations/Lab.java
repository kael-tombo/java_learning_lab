package com.learning.annotations;

import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;

public class Lab {

    public static void main(String[] args) throws Exception {
        System.out.println("=".repeat(60));
        System.out.println("MODULE 09: ANNOTATIONS & REFLECTION");
        System.out.println("=".repeat(60));

        part1BuiltInAnnotations();
        part2CustomAnnotations();
        part3MetaAnnotations();
        part4ReflectionBasics();
        part5ReflectionIntrospection();
        part6AnnotationProcessing();
        part7RealWorldExamples();

        System.out.println("\n" + "=".repeat(60));
        System.out.println("ALL DEMOS COMPLETED SUCCESSFULLY");
        System.out.println("=".repeat(60));
    }

    static void part1BuiltInAnnotations() {
        System.out.println("\n### PART 1: Built-in Annotations ###\n");

        System.out.println("@Override - Ensures method overrides parent:");
        System.out.println("  class Dog extends Animal { @Override void speak() {} }");

        System.out.println("\n@Deprecated - Marks code as obsolete:");
        System.out.println("  @Deprecated String getOldMethod() { ... }");

        System.out.println("\n@SuppressWarnings - Suppresses compiler warnings:");
        System.out.println("  @SuppressWarnings(\"unchecked\") List rawList = getList();");

        System.out.println("\n@FunctionalInterface - Ensures single abstract method:");
        System.out.println("  @FunctionalInterface interface Calculator { int calc(int a, int b); }");

        System.out.println("\n@SafeVarargs - Java 7+ suppresses heap pollution warnings:");
        System.out.println("  @SafeVarargs final <T> void printAll(T... items) { ... }");
    }

    static void part2CustomAnnotations() {
        System.out.println("\n### PART 2: Custom Annotations ###\n");

        System.out.println("Defining a custom annotation:");
        System.out.println("""
            @Retention(RetentionPolicy.RUNTIME)
            @Target(ElementType.METHOD)
            public @interface Test {
                String description() default "";
                int priority() default 5;
            }
            """);

        System.out.println("Using custom annotation:");
        System.out.println("""
            @Test(description = \"Login test\", priority = 1)
            public void testLogin() { ... }
            """);

        System.out.println("Accessing annotation at runtime via reflection:");
        demonstrateCustomAnnotationUsage();
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface Test {
        String description() default "";
        int priority() default 5;
    }

    @Test(description = "This is a test method", priority = 1)
    public static void sampleTestMethod() {
        System.out.println("  Running test method");
    }

    static void demonstrateCustomAnnotationUsage() {
        try {
            Method method = Lab.class.getMethod("sampleTestMethod");
            Test test = method.getAnnotation(Test.class);
            if (test != null) {
                System.out.println("  Found @Test: description='" + test.description() + "', priority=" + test.priority());
            }
        } catch (NoSuchMethodException e) {
            System.out.println("  Error: " + e.getMessage());
        }
    }

    static void part3MetaAnnotations() {
        System.out.println("\n### PART 3: Meta-Annotations (Annotations on Annotations) ###\n");

        System.out.println("@Retention - When annotation is available:");
        System.out.println("  SOURCE   - Compile-time only, not in bytecode");
        System.out.println("  CLASS    - In bytecode, not at runtime");
        System.out.println("  RUNTIME  - Available at runtime via reflection");

        System.out.println("\n@Target - Where annotation can be used:");
        System.out.println("  TYPE, FIELD, METHOD, PARAMETER, CONSTRUCTOR, LOCAL_VARIABLE, PACKAGE, ANNOTATION_TYPE, TYPE_USE, TYPE_PARAMETER");

        System.out.println("\n@Inherited - Subclasses inherit annotation:");
        System.out.println("  @Inherited @MyAnnotation class Parent {}");
        System.out.println("  class Child extends Parent {} // Child has @MyAnnotation");

        System.out.println("\n@Documented - Include in Javadoc:");
        System.out.println("  @Documented @MyAnnotation class Annotated {}");

        System.out.println("\n@Repeatable - Apply same annotation multiple times:");
        System.out.println("  @Repeatable(Languages.class) @interface Language { String value(); }");
    }

    static void part4ReflectionBasics() {
        System.out.println("\n### PART 4: Reflection API Basics ###\n");

        System.out.println("Obtaining Class object:");
        System.out.println("  Class<?> c1 = String.class;");
        System.out.println("  Class<?> c2 = \"hello\".getClass();");
        System.out.println("  Class<?> c3 = Class.forName(\"java.lang.String\");");

        System.out.println("\nGetting class name:");
        Class<?> c = String.class;
        System.out.println("  getName(): " + c.getName());
        System.out.println("  getSimpleName(): " + c.getSimpleName());
        System.out.println("  getCanonicalName(): " + c.getCanonicalName());

        System.out.println("\nChecking class modifiers:");
        System.out.println("  Note: Class has no isPublic/isAbstract/isFinal - use Modifier flags:");
        System.out.println("  isPublic:    " + Modifier.isPublic(c.getModifiers()));
        System.out.println("  isFinal:     " + Modifier.isFinal(c.getModifiers()));
        System.out.println("  isInterface: " + c.isInterface());

        System.out.println("\nGetting package and superclass:");
        System.out.println("  getPackage(): " + c.getPackage());
        System.out.println("  getSuperclass(): " + c.getSuperclass());

        System.out.println("\nGetting implemented interfaces:");
        for (Class<?> iface : c.getInterfaces()) {
            System.out.println("  " + iface.getSimpleName());
        }
    }

    static void part5ReflectionIntrospection() {
        System.out.println("\n### PART 5: Reflection Introspection ###\n");

        Class<?> personClass = Person.class;

        System.out.println("Getting all fields:");
        for (Field field : personClass.getDeclaredFields()) {
            System.out.println("  " + Modifier.toString(field.getModifiers()) + " " +
                field.getType().getSimpleName() + " " + field.getName());
        }

        System.out.println("\nGetting all methods:");
        for (Method method : personClass.getDeclaredMethods()) {
            System.out.println("  " + method.getName() + "()");
        }

        System.out.println("\nGetting all constructors:");
        for (Constructor<?> cons : personClass.getDeclaredConstructors()) {
            System.out.println("  " + cons.getName() + "(" +
                Arrays.toString(cons.getParameterTypes()) + ")");
        }

        System.out.println("\nInvoking method via reflection:");
        try {
            Person p = new Person("John", 30);
            Method getName = personClass.getMethod("getName");
            Object result = getName.invoke(p);
            System.out.println("  getName() returned: " + result);
        } catch (Exception e) {
            System.out.println("  Error: " + e.getMessage());
        }

        System.out.println("\nAccessing private field:");
        try {
            Person p = new Person("Jane", 25);
            Field nameField = personClass.getDeclaredField("name");
            nameField.setAccessible(true);
            Object value = nameField.get(p);
            System.out.println("  Private field 'name' value: " + value);
        } catch (Exception e) {
            System.out.println("  Error: " + e.getMessage());
        }
    }

    static void part6AnnotationProcessing() {
        System.out.println("\n### PART 6: Annotation Processing ###\n");

        System.out.println("Processing annotations at runtime:");

        Class<?>[] classes = {SampleService.class, AnotherService.class};
        for (Class<?> cls : classes) {
            if (cls.isAnnotationPresent(ServiceInfo.class)) {
                ServiceInfo info = cls.getAnnotation(ServiceInfo.class);
                System.out.println("  Found @ServiceInfo: name='" + info.name() +
                    "', version=" + info.version());
            }
        }

        System.out.println("\nProcessing method annotations:");
        for (Method method : SampleService.class.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Execute.class)) {
                Execute exec = method.getAnnotation(Execute.class);
                System.out.println("  Found @Execute: order=" + exec.order() +
                    ", description='" + exec.description() + "'");
            }
        }

        System.out.println("\nProcessing field annotations:");
        for (Field field : Config.class.getDeclaredFields()) {
            if (field.isAnnotationPresent(Property.class)) {
                Property prop = field.getAnnotation(Property.class);
                System.out.println("  Found @Property: key='" + prop.key() +
                    "', defaultValue='" + prop.defaultValue() + "'");
            }
        }
    }

    static void part7RealWorldExamples() {
        System.out.println("\n### PART 7: Real-World Examples ###\n");

        System.out.println("Example 1: Validation Framework");
        System.out.println("  Using reflection to validate object fields");
        validateUser();

        System.out.println("\nExample 2: Dependency Injection");
        System.out.println("  Using reflection to inject dependencies");
        demonstrateDI();

        System.out.println("\nExample 3: Serialization Mapping");
        System.out.println("  Using annotations to define serialization rules");
    }

    static void validateUser() {
        User user = new User("John", "john@email.com", 15);
        Class<?> userClass = user.getClass();

        for (Field field : userClass.getDeclaredFields()) {
            if (field.isAnnotationPresent(Validate.class)) {
                Validate validate = field.getAnnotation(Validate.class);
                field.setAccessible(true);
                try {
                    Object value = field.get(user);
                    boolean valid = validateValue(value, validate);
                    System.out.println("  Field '" + field.getName() + "': " +
                        (valid ? "VALID" : "INVALID"));
                } catch (Exception e) {
                    System.out.println("  Error: " + e.getMessage());
                }
            }
        }
    }

    static boolean validateValue(Object value, Validate validate) {
        if (value instanceof String str) {
            if (validate.minLength() > 0 && str.length() < validate.minLength()) {
                return false;
            }
            if (validate.maxLength() > 0 && str.length() > validate.maxLength()) {
                return false;
            }
            if (!validate.pattern().isEmpty() && !str.matches(validate.pattern())) {
                return false;
            }
        }
        if (value instanceof Integer num) {
            if (num < validate.minValue()) return false;
            if (num > validate.maxValue()) return false;
        }
        return true;
    }

    static void demonstrateDI() {
        System.out.println("  Simulating dependency injection...");
        try {
            InjectMe injectMe = InjectMe.class.getDeclaredConstructor().newInstance();
            for (Field field : injectMe.getClass().getDeclaredFields()) {
                if (field.isAnnotationPresent(Autowired.class)) {
                    field.setAccessible(true);
                    Class<?> fieldType = field.getType();
                    Object dependency = fieldType.getDeclaredConstructor().newInstance();
                    field.set(injectMe, dependency);
                    System.out.println("  Injected " + fieldType.getSimpleName() +
                        " into " + field.getName());
                }
            }
        } catch (Exception e) {
            System.out.println("  Error: " + e.getMessage());
        }
    }

    // Supporting classes for demonstration

    static class Person {
        private String name;
        private int age;

        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        public String getName() { return name; }
        public int getAge() { return age; }
        public void setName(String name) { this.name = name; }
        public void setAge(int age) { this.age = age; }
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    @interface ServiceInfo {
        String name() default "";
        String version() default "1.0";
    }

    @ServiceInfo(name = "SampleService", version = "2.0")
    static class SampleService {}

    @ServiceInfo(name = "AnotherService")
    static class AnotherService {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface Execute {
        int order() default 0;
        String description() default "";
    }

    static class SampleService2 {
        @Execute(order = 1, description = "Initialize")
        public void init() {}

        @Execute(order = 2, description = "Process")
        public void process() {}
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    @interface Property {
        String key();
        String defaultValue() default "";
    }

    static class Config {
        @Property(key = "db.url", defaultValue = "localhost")
        private String dbUrl;

        @Property(key = "db.port", defaultValue = "3306")
        private int dbPort;
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    @interface Validate {
        int minLength() default 0;
        int maxLength() default Integer.MAX_VALUE;
        String pattern() default "";
        int minValue() default Integer.MIN_VALUE;
        int maxValue() default Integer.MAX_VALUE;
    }

    static class User {
        @Validate(minLength = 2, maxLength = 50)
        private String name;

        @Validate(pattern = "^[A-Za-z0-9+_.-]+@(.+)$")
        private String email;

        @Validate(minValue = 18, maxValue = 150)
        private int age;

        public User(String name, String email, int age) {
            this.name = name;
            this.email = email;
            this.age = age;
        }
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    @interface Autowired {}

    static class InjectMe {
        @Autowired
        private SomeDependency dependency;
    }

    static class SomeDependency {
        public SomeDependency() {}
    }
}