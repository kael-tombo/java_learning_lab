package com.learning.annotations;

import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Elite Annotations & Reflection Training
 * 
 * This module covers advanced concepts of Java Annotations and Reflection API,
 * demonstrating how to build custom frameworks (Validation, Dependency Injection, Serialization, Test Runner).
 */
public class EliteAnnotationsTraining {

    // ============================================================================
    // SECTION 1: CUSTOM & META-ANNOTATIONS
    // ============================================================================

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface ValidateString {
        int minLength() default 0;
        int maxLength() default Integer.MAX_VALUE;
        String regex() default "";
        String message() default "Invalid string field";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface ValidateNumber {
        double min() default Double.NEGATIVE_INFINITY;
        double max() default Double.POSITIVE_INFINITY;
        String message() default "Invalid numeric field";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    @Inherited
    public @interface JsonSerializable {
        boolean formatted() default false;
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface JsonField {
        String name() default "";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface JsonIgnore {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public @interface Autowired {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    public @interface Component {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface TestMethod {
        int order() default 0;
        Class<? extends Throwable> expectedException() default None.class;
        
        class None extends Throwable {}
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    public @interface TestSuite {
        String name();
    }

    // ============================================================================
    // SECTION 2: REFLECTION INTROSPECTION UTILS
    // ============================================================================

    public static class ReflectionUtils {

        public static List<Field> getAllFields(Class<?> clazz) {
            List<Field> fields = new ArrayList<>();
            Class<?> current = clazz;
            while (current != null && current != Object.class) {
                fields.addAll(Arrays.asList(current.getDeclaredFields()));
                current = current.getSuperclass();
            }
            return fields;
        }

        public static List<Method> getAllMethods(Class<?> clazz) {
            List<Method> methods = new ArrayList<>();
            Class<?> current = clazz;
            while (current != null) {
                for (Method method : current.getDeclaredMethods()) {
                    // Skip synthetic members (compiler/JaCoCo generated, e.g. $jacocoInit, bridges)
                    if (!method.isSynthetic()) {
                        methods.add(method);
                    }
                }
                if (current == Object.class) {
                    break;
                }
                current = current.getSuperclass();
            }
            return methods;
        }

        public static void setFieldValue(Object target, String fieldName, Object value) throws Exception {
            Field field = getDeclaredField(target.getClass(), fieldName);
            if (field == null) {
                throw new NoSuchFieldException("Field " + fieldName + " not found in " + target.getClass());
            }
            boolean accessible = field.canAccess(target);
            try {
                field.setAccessible(true);
                field.set(target, value);
            } finally {
                field.setAccessible(accessible);
            }
        }

        public static Object getFieldValue(Object target, String fieldName) throws Exception {
            Field field = getDeclaredField(target.getClass(), fieldName);
            if (field == null) {
                throw new NoSuchFieldException("Field " + fieldName + " not found in " + target.getClass());
            }
            boolean accessible = field.canAccess(target);
            try {
                field.setAccessible(true);
                return field.get(target);
            } finally {
                field.setAccessible(accessible);
            }
        }

        private static Field getDeclaredField(Class<?> clazz, String fieldName) {
            Class<?> current = clazz;
            while (current != null && current != Object.class) {
                try {
                    return current.getDeclaredField(fieldName);
                } catch (NoSuchFieldException e) {
                    current = current.getSuperclass();
                }
            }
            return null;
        }
    }

    // ============================================================================
    // SECTION 3: VALIDATION ENGINE
    // ============================================================================

    public static class ValidationEngine {

        public static List<String> validate(Object obj) {
            if (obj == null) return List.of("Object cannot be null");
            List<String> errors = new ArrayList<>();
            List<Field> fields = ReflectionUtils.getAllFields(obj.getClass());

            for (Field field : fields) {
                boolean accessible = field.canAccess(obj);
                try {
                    field.setAccessible(true);
                    Object value = field.get(obj);

                    if (field.isAnnotationPresent(ValidateString.class)) {
                        ValidateString annot = field.getAnnotation(ValidateString.class);
                        if (value == null) {
                            errors.add(field.getName() + ": Cannot be null");
                        } else if (value instanceof String str) {
                            if (str.length() < annot.minLength()) {
                                errors.add(field.getName() + ": " + annot.message() + " (minimum length is " + annot.minLength() + ")");
                            }
                            if (str.length() > annot.maxLength()) {
                                errors.add(field.getName() + ": " + annot.message() + " (maximum length is " + annot.maxLength() + ")");
                            }
                            if (!annot.regex().isEmpty()) {
                                if (!Pattern.matches(annot.regex(), str)) {
                                    errors.add(field.getName() + ": " + annot.message() + " (pattern mismatch)");
                                }
                            }
                        } else {
                            errors.add(field.getName() + ": Expected String value but found " + value.getClass().getSimpleName());
                        }
                    }

                    if (field.isAnnotationPresent(ValidateNumber.class)) {
                        ValidateNumber annot = field.getAnnotation(ValidateNumber.class);
                        if (value == null) {
                            errors.add(field.getName() + ": Cannot be null");
                        } else if (value instanceof Number num) {
                            double val = num.doubleValue();
                            if (val < annot.min()) {
                                errors.add(field.getName() + ": " + annot.message() + " (minimum value is " + annot.min() + ")");
                            }
                            if (val > annot.max()) {
                                errors.add(field.getName() + ": " + annot.message() + " (maximum value is " + annot.max() + ")");
                            }
                        } else {
                            errors.add(field.getName() + ": Expected Number value but found " + value.getClass().getSimpleName());
                        }
                    }

                } catch (Exception e) {
                    errors.add(field.getName() + ": Failed to retrieve value (" + e.getMessage() + ")");
                } finally {
                    field.setAccessible(accessible);
                }
            }
            return errors;
        }
    }

    // ============================================================================
    // SECTION 4: DEPENDENCY INJECTION CONTAINER
    // ============================================================================

    public static class DiContainer {
        private final Map<Class<?>, Object> registry = new HashMap<>();

        public void register(Class<?> clazz) throws Exception {
            if (!clazz.isAnnotationPresent(Component.class)) {
                throw new IllegalArgumentException("Class must be annotated with @Component: " + clazz.getName());
            }
            Constructor<?> constructor = clazz.getDeclaredConstructor();
            boolean accessible = constructor.canAccess(null);
            try {
                constructor.setAccessible(true);
                Object instance = constructor.newInstance();
                registry.put(clazz, instance);
            } finally {
                constructor.setAccessible(accessible);
            }
        }

        public void registerInstance(Class<?> clazz, Object instance) {
            registry.put(clazz, instance);
        }

        @SuppressWarnings("unchecked")
        public <T> T getBean(Class<T> clazz) {
            return (T) registry.get(clazz);
        }

        public void wire() throws Exception {
            for (Object instance : registry.values()) {
                List<Field> fields = ReflectionUtils.getAllFields(instance.getClass());
                for (Field field : fields) {
                    if (field.isAnnotationPresent(Autowired.class)) {
                        Class<?> fieldType = field.getType();
                        Object dependency = registry.get(fieldType);
                        if (dependency == null) {
                            throw new IllegalStateException("Unsatisfied dependency of type " + fieldType.getName() + " for bean " + instance.getClass().getName());
                        }
                        boolean accessible = field.canAccess(instance);
                        try {
                            field.setAccessible(true);
                            field.set(instance, dependency);
                        } finally {
                            field.setAccessible(accessible);
                        }
                    }
                }
            }
        }
    }

    // ============================================================================
    // SECTION 5: CUSTOM SERIALIZER (JSON)
    // ============================================================================

    public static class JsonSerializer {

        public static String serialize(Object obj) throws Exception {
            if (obj == null) return "null";
            Class<?> clazz = obj.getClass();
            if (!clazz.isAnnotationPresent(JsonSerializable.class)) {
                throw new IllegalArgumentException("Class is not annotated with @JsonSerializable: " + clazz.getName());
            }

            JsonSerializable config = clazz.getAnnotation(JsonSerializable.class);
            List<Field> fields = ReflectionUtils.getAllFields(clazz);
            Map<String, String> jsonElements = new LinkedHashMap<>();

            for (Field field : fields) {
                if (field.isAnnotationPresent(JsonIgnore.class)) {
                    continue;
                }
                boolean accessible = field.canAccess(obj);
                try {
                    field.setAccessible(true);
                    Object value = field.get(obj);
                    
                    String key = field.getName();
                    if (field.isAnnotationPresent(JsonField.class)) {
                        JsonField jsonField = field.getAnnotation(JsonField.class);
                        if (!jsonField.name().isEmpty()) {
                            key = jsonField.name();
                        }
                    }

                    jsonElements.put(key, toJsonValue(value));
                } finally {
                    field.setAccessible(accessible);
                }
            }

            return formatJson(jsonElements, config.formatted());
        }

        private static String toJsonValue(Object value) throws Exception {
            if (value == null) return "null";
            if (value instanceof String || value instanceof Character) {
                return "\"" + escapeJson(value.toString()) + "\"";
            }
            if (value instanceof Number || value instanceof Boolean) {
                return value.toString();
            }
            if (value.getClass().isAnnotationPresent(JsonSerializable.class)) {
                return serialize(value);
            }
            if (value instanceof Collection<?> col) {
                List<String> elements = new ArrayList<>();
                for (Object item : col) {
                    elements.add(toJsonValue(item));
                }
                return "[" + String.join(",", elements) + "]";
            }
            if (value instanceof Map<?, ?> map) {
                List<String> pairs = new ArrayList<>();
                for (Map.Entry<?, ?> entry : map.entrySet()) {
                    pairs.add("\"" + escapeJson(entry.getKey().toString()) + "\":" + toJsonValue(entry.getValue()));
                }
                return "{" + String.join(",", pairs) + "}";
            }
            return "\"" + escapeJson(value.toString()) + "\"";
        }

        private static String escapeJson(String input) {
            return input.replace("\\", "\\\\")
                        .replace("\"", "\\\"")
                        .replace("\b", "\\b")
                        .replace("\f", "\\f")
                        .replace("\n", "\\n")
                        .replace("\r", "\\r")
                        .replace("\t", "\\t");
        }

        private static String formatJson(Map<String, String> elements, boolean formatted) {
            if (elements.isEmpty()) return "{}";
            if (!formatted) {
                return "{" + elements.entrySet().stream()
                        .map(e -> "\"" + e.getKey() + "\":" + e.getValue())
                        .collect(Collectors.joining(",")) + "}";
            }
            
            StringBuilder sb = new StringBuilder();
            sb.append("{\n");
            int size = elements.size();
            int index = 0;
            for (Map.Entry<String, String> entry : elements.entrySet()) {
                sb.append("  \"").append(entry.getKey()).append("\": ");
                String val = entry.getValue();
                if (val.contains("\n")) {
                    val = val.replace("\n", "\n  ");
                }
                sb.append(val);
                if (++index < size) {
                    sb.append(",");
                }
                sb.append("\n");
            }
            sb.append("}");
            return sb.toString();
        }
    }

    // ============================================================================
    // SECTION 6: CUSTOM ANNOTATION-BASED TEST RUNNER
    // ============================================================================

    public static class CustomTestRunner {
        
        public static class TestResult {
            private final String methodName;
            private final boolean passed;
            private final Throwable error;

            public TestResult(String methodName, boolean passed, Throwable error) {
                this.methodName = methodName;
                this.passed = passed;
                this.error = error;
            }

            public String getMethodName() { return methodName; }
            public boolean isPassed() { return passed; }
            public Throwable getError() { return error; }
        }

        public static class SuiteResult {
            private final String suiteName;
            private final List<TestResult> results = new ArrayList<>();

            public SuiteResult(String suiteName) {
                this.suiteName = suiteName;
            }

            public String getSuiteName() { return suiteName; }
            public List<TestResult> getResults() { return results; }
            public long getPassedCount() { return results.stream().filter(TestResult::isPassed).count(); }
            public long getFailedCount() { return results.stream().filter(r -> !r.isPassed()).count(); }
        }

        public static SuiteResult run(Class<?> testClass) throws Exception {
            String suiteName = testClass.getSimpleName();
            if (testClass.isAnnotationPresent(TestSuite.class)) {
                suiteName = testClass.getAnnotation(TestSuite.class).name();
            }

            SuiteResult suiteResult = new SuiteResult(suiteName);
            Constructor<?> constructor = testClass.getDeclaredConstructor();
            boolean accessible = constructor.canAccess(null);
            Object testInstance;
            try {
                constructor.setAccessible(true);
                testInstance = constructor.newInstance();
            } finally {
                constructor.setAccessible(accessible);
            }

            List<Method> testMethods = Arrays.stream(testClass.getDeclaredMethods())
                    .filter(m -> m.isAnnotationPresent(TestMethod.class))
                    .sorted(Comparator.comparingInt(m -> m.getAnnotation(TestMethod.class).order()))
                    .collect(Collectors.toList());

            for (Method method : testMethods) {
                TestMethod testAnnot = method.getAnnotation(TestMethod.class);
                Class<? extends Throwable> expected = testAnnot.expectedException();
                boolean methodAccessible = method.canAccess(testInstance);
                
                try {
                    method.setAccessible(true);
                    method.invoke(testInstance);
                    
                    if (expected == TestMethod.None.class) {
                        suiteResult.getResults().add(new TestResult(method.getName(), true, null));
                    } else {
                        suiteResult.getResults().add(new TestResult(method.getName(), false, 
                                new AssertionError("Expected exception " + expected.getName() + " but none was thrown")));
                    }
                } catch (InvocationTargetException e) {
                    Throwable cause = e.getCause();
                    if (expected != TestMethod.None.class && expected.isInstance(cause)) {
                        suiteResult.getResults().add(new TestResult(method.getName(), true, null));
                    } else {
                        suiteResult.getResults().add(new TestResult(method.getName(), false, cause));
                    }
                } catch (Exception e) {
                    suiteResult.getResults().add(new TestResult(method.getName(), false, e));
                } finally {
                    method.setAccessible(methodAccessible);
                }
            }

            return suiteResult;
        }
    }
}