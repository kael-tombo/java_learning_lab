package com.learning.reflection;

import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;

/**
 * Elite Reflection & Introspection Training
 *
 * Builds three classic reflection-powered "mini frameworks":
 * - Command dispatch (method-level annotations + invocation)
 * - Object mappers (field copying with type conversion)
 * - A null-safe proxy (java.lang.reflect.Proxy)
 *
 * Deliberate teaching points: accessibility restore, handling of
 * InvocationTargetException, primitive boxing in conversion, and
 * synthetic/bridge member filtering.
 */
public class EliteReflectionTraining {

    // ============================================================================
    // SECTION 1: ANNOTATIONS USED BY THE TRAINING FRAMEWORKS
    // ============================================================================

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface Command {
        String name();
        String description() default "";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface MappedFrom {
        String value();
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface IgnoreMapping {}

    // ============================================================================
    // SECTION 2: INTROSPECTION UTILITIES
    // ============================================================================

    public static class Introspector {

        public static List<Field> instanceFields(Class<?> clazz) {
            List<Field> fields = new ArrayList<>();
            for (Class<?> c = clazz; c != null && c != Object.class; c = c.getSuperclass()) {
                for (Field f : c.getDeclaredFields()) {
                    if (!f.isSynthetic() && !Modifier.isStatic(f.getModifiers())) {
                        fields.add(f);
                    }
                }
            }
            return fields;
        }

        public static List<Method> annotatedMethods(Class<?> clazz, Class<? extends Annotation> annotation) {
            List<Method> found = new ArrayList<>();
            for (Class<?> c = clazz; c != null && c != Object.class; c = c.getSuperclass()) {
                for (Method m : c.getDeclaredMethods()) {
                    if (m.isSynthetic() || m.isBridge()) continue;
                    if (m.isAnnotationPresent(annotation)) {
                        found.add(m);
                    }
                }
            }
            return found;
        }

        public static String methodSignature(Method m) {
            String params = Arrays.stream(m.getParameterTypes())
                    .map(Class::getSimpleName)
                    .collect(java.util.stream.Collectors.joining(", "));
            return "%s %s(%s)".formatted(m.getReturnType().getSimpleName(), m.getName(), params);
        }

        public static Map<String, Object> toFieldMap(Object target) throws Exception {
            Map<String, Object> map = new LinkedHashMap<>();
            for (Field f : instanceFields(target.getClass())) {
                boolean accessible = f.canAccess(target);
                try {
                    f.setAccessible(true);
                    map.put(f.getName(), f.get(target));
                } finally {
                    f.setAccessible(accessible);
                }
            }
            return map;
        }
    }

    // ============================================================================
    // SECTION 3: COMMAND DISPATCHER (annotation-driven method routing)
    // ============================================================================

    public static class CommandDispatcher {
        private final Map<String, Method> commands = new LinkedHashMap<>();
        private final Object handler;

        public CommandDispatcher(Object handler) {
            this.handler = handler;
            for (Method method : Introspector.annotatedMethods(handler.getClass(), Command.class)) {
                Command annotation = method.getAnnotation(Command.class);
                Method previous = commands.putIfAbsent(annotation.name(), method);
                if (previous != null) {
                    throw new IllegalStateException("Duplicate command name: " + annotation.name());
                }
            }
            if (commands.isEmpty()) {
                throw new IllegalArgumentException("Handler exposes no @Command methods");
            }
        }

        public Set<String> commandNames() {
            return Collections.unmodifiableSet(commands.keySet());
        }

        public Object dispatch(String name, Object... args) throws Exception {
            Method method = commands.get(name);
            if (method == null) {
                throw new NoSuchElementException("Unknown command: " + name);
            }
            boolean accessible = method.canAccess(handler);
            try {
                method.setAccessible(true);
                return method.invoke(handler, args);
            } catch (InvocationTargetException e) {
                throw (e.getCause() instanceof Exception ex) ? ex : e;
            } finally {
                method.setAccessible(accessible);
            }
        }
    }

    // ============================================================================
    // SECTION 4: OBJECT MAPPER (field-level mapping with conversion)
    // ============================================================================

    public static class ObjectMapper {

        public static <D> D map(Object source, Class<D> targetClass) throws Exception {
            Constructor<D> ctor = targetClass.getDeclaredConstructor();
            boolean ctorAccessible = ctor.canAccess(null);
            try {
                ctor.setAccessible(true);
                D target = ctor.newInstance();

                for (Field targetField : Introspector.instanceFields(targetClass)) {
                    if (targetField.isAnnotationPresent(IgnoreMapping.class)) continue;
                    boolean accessible = targetField.canAccess(target);
                    try {
                        targetField.setAccessible(true);
                        String sourceName = targetField.isAnnotationPresent(MappedFrom.class)
                                ? targetField.getAnnotation(MappedFrom.class).value()
                                : targetField.getName();
                        Object value = readSourceField(source, sourceName);
                        if (value != null) {
                            targetField.set(target, convert(value, targetField.getType()));
                        }
                    } finally {
                        targetField.setAccessible(accessible);
                    }
                }
                return target;
            } finally {
                ctor.setAccessible(ctorAccessible);
            }
        }

        private static Object readSourceField(Object source, String name) throws Exception {
            for (Field f : Introspector.instanceFields(source.getClass())) {
                if (f.getName().equals(name)) {
                    boolean accessible = f.canAccess(source);
                    try {
                        f.setAccessible(true);
                        return f.get(source);
                    } finally {
                        f.setAccessible(accessible);
                    }
                }
            }
            return null; // unmatched source field stays at target default
        }

        /** Minimal converter: identity for reference types, boxing-aware for primitives. */
        static Object convert(Object value, Class<?> targetType) {
            if (targetType.isInstance(value)) return value;
            if (value instanceof Number n) {
                if (targetType == int.class || targetType == Integer.class) return n.intValue();
                if (targetType == long.class || targetType == Long.class) return n.longValue();
                if (targetType == double.class || targetType == Double.class) return n.doubleValue();
                if (targetType == float.class || targetType == Float.class) return n.floatValue();
            }
            if (value instanceof String s) {
                if (targetType == int.class || targetType == Integer.class) return Integer.parseInt(s);
                if (targetType == long.class || targetType == Long.class) return Long.parseLong(s);
                if (targetType == double.class || targetType == Double.class) return Double.parseDouble(s);
                if (targetType == boolean.class || targetType == Boolean.class) return Boolean.parseBoolean(s);
            }
            throw new IllegalArgumentException("Cannot convert " + value.getClass().getSimpleName()
                    + " to " + targetType.getSimpleName());
        }
    }

    // ============================================================================
    // SECTION 5: DYNAMIC PROXY (logging wrapper)
    // ============================================================================

    public interface Greeter {
        String greet(String name);
        String farewell(String name);
    }

    public static class SimpleGreeter implements Greeter {
        @Override public String greet(String name) { return "Hello, " + name + "!"; }
        @Override public String farewell(String name) { return "Goodbye, " + name + "."; }
    }

    public static class LoggingProxy implements InvocationHandler {
        private final Object target;
        private final List<String> callLog = new ArrayList<>();

        private LoggingProxy(Object target) {
            this.target = target;
        }

        @SuppressWarnings("unchecked")
        public static <T> T create(Class<T> iface, T target) {
            return (T) Proxy.newProxyInstance(
                    iface.getClassLoader(),
                    new Class<?>[]{iface},
                    new LoggingProxy(target));
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            if (method.getDeclaringClass() == Object.class) {
                return method.invoke(target, args);
            }
            callLog.add(method.getName() + Arrays.toString(args));
            long start = System.nanoTime();
            try {
                return method.invoke(target, args);
            } finally {
                callLog.set(callLog.size() - 1,
                        callLog.getLast() + " -> " + (System.nanoTime() - start) + "ns");
            }
        }

        public List<String> getCallLog() {
            return List.copyOf(callLog);
        }
    }

    // ============================================================================
    // SECTION 6: INVOCATION TARGET DEMO HANDLER
    // ============================================================================

    public static class CalculatorCommands {
        @Command(name = "add", description = "Adds two integers")
        public int add(int a, int b) {
            return a + b;
        }

        @Command(name = "echo", description = "Repeats a message")
        public String echo(String message) {
            return "echo: " + message;
        }

        @Command(name = "fail", description = "Always throws")
        public void fail() {
            throw new ArithmeticException("intentional failure");
        }
    }

    // ============================================================================
    // DEMO
    // ============================================================================

    public static void main(String[] args) throws Exception {
        System.out.println("=".repeat(60));
        System.out.println("ELITE REFLECTION & INTROSPECTION TRAINING");
        System.out.println("=".repeat(60));
        demonstrate();
        System.out.println("\nALL REFLECTION DEMOS COMPLETED SUCCESSFULLY");
    }

    public static void demonstrate() throws Exception {
        System.out.println("\n### Introspection ###");
        for (Method m : Introspector.annotatedMethods(CalculatorCommands.class, Command.class)) {
            System.out.println("  " + methodSignatureHelper(m));
        }

        System.out.println("\n### Command Dispatcher ###");
        CommandDispatcher dispatcher = new CommandDispatcher(new CalculatorCommands());
        System.out.println("  commands: " + dispatcher.commandNames());
        System.out.println("  add(2,3) = " + dispatcher.dispatch("add", 2, 3));
        System.out.println("  echo('hi') = " + dispatcher.dispatch("echo", "hi"));

        System.out.println("\n### Object Mapper ###");
        record CustomerEntity(String name, int age, String internalState) {}
        var entity = new CustomerEntity("Ada", 36, "secret");
        CustomerDto dto = ObjectMapper.map(entity, CustomerDto.class);
        System.out.println("  dto = " + dto);

        System.out.println("\n### Dynamic Proxy ###");
        Greeter proxy = LoggingProxy.create(Greeter.class, new SimpleGreeter());
        proxy.greet("Ada");
        proxy.farewell("Ada");
        LoggingProxy handler = (LoggingProxy) Proxy.getInvocationHandler(proxy);
        System.out.println("  call log: " + handler.getCallLog());
    }

    private static String methodSignatureHelper(Method m) {
        return Introspector.methodSignature(m) + " [@Command]";
    }

    /** DTO used by the mapper demo. */
    public static class CustomerDto {
        @MappedFrom("name")
        private String fullName;

        private int age;

        @IgnoreMapping
        private String internalState;

        @Override
        public String toString() {
            return "CustomerDto{fullName='%s', age=%d, internalState=%s}"
                    .formatted(fullName, age, internalState);
        }
    }
}
