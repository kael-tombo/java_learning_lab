package com.learning.annotations;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite Annotations & Reflection Training Tests")
class EliteAnnotationsTrainingTest {

    // ============================================================================
    // SECTION 1: REFLECTION INTROSPECTION UTILS TESTS
    // ============================================================================

    static class BaseClass {
        public String basePublic;
        private String basePrivate;
    }

    static class SubClass extends BaseClass {
        public int subPublic;
        private int subPrivate;
    }

    @Nested
    @DisplayName("ReflectionUtils Introspection Tests")
    class ReflectionUtilsTests {

        @Test
        @DisplayName("Should retrieve all fields including inherited and private ones")
        void shouldRetrieveAllFields() {
            List<Field> fields = EliteAnnotationsTraining.ReflectionUtils.getAllFields(SubClass.class);
            assertThat(fields)
                    .extracting(Field::getName)
                    .containsExactlyInAnyOrder("basePublic", "basePrivate", "subPublic", "subPrivate");
        }

        @Test
        @DisplayName("Should retrieve all methods including inherited ones")
        void shouldRetrieveAllMethods() {
            List<Method> methods = EliteAnnotationsTraining.ReflectionUtils.getAllMethods(SubClass.class);
            assertThat(methods)
                    .extracting(Method::getName)
                    .contains("toString", "equals", "hashCode");
        }

        @Test
        @DisplayName("Should set and get private field values successfully")
        void shouldSetAndGetPrivateField() throws Exception {
            SubClass instance = new SubClass();
            
            EliteAnnotationsTraining.ReflectionUtils.setFieldValue(instance, "subPrivate", 42);
            Object val = EliteAnnotationsTraining.ReflectionUtils.getFieldValue(instance, "subPrivate");
            
            assertThat(val).isEqualTo(42);
        }

        @Test
        @DisplayName("Should set and get inherited private field values successfully")
        void shouldSetAndGetInheritedPrivateField() throws Exception {
            SubClass instance = new SubClass();
            
            EliteAnnotationsTraining.ReflectionUtils.setFieldValue(instance, "basePrivate", "secret");
            Object val = EliteAnnotationsTraining.ReflectionUtils.getFieldValue(instance, "basePrivate");
            
            assertThat(val).isEqualTo("secret");
        }

        @Test
        @DisplayName("Should throw NoSuchFieldException for non-existent fields")
        void shouldThrowNoSuchFieldException() {
            SubClass instance = new SubClass();
            assertThatThrownBy(() -> EliteAnnotationsTraining.ReflectionUtils.getFieldValue(instance, "nonExistent"))
                    .isInstanceOf(NoSuchFieldException.class);
            assertThatThrownBy(() -> EliteAnnotationsTraining.ReflectionUtils.setFieldValue(instance, "nonExistent", "val"))
                    .isInstanceOf(NoSuchFieldException.class);
        }
    }

    // ============================================================================
    // SECTION 2: VALIDATION ENGINE TESTS
    // ============================================================================

    static class ValidatedUser {
        @EliteAnnotationsTraining.ValidateString(minLength = 3, maxLength = 10, regex = "^[a-zA-Z]+$", message = "Username must be alphabetic")
        private String username;

        @EliteAnnotationsTraining.ValidateString(regex = "^[A-Za-z0-9+_.-]+@(.+)$", message = "Invalid email format")
        private String email;

        @EliteAnnotationsTraining.ValidateNumber(min = 18, max = 120, message = "Age must be between 18 and 120")
        private int age;

        public ValidatedUser(String username, String email, int age) {
            this.username = username;
            this.email = email;
            this.age = age;
        }
    }

    @Nested
    @DisplayName("ValidationEngine Tests")
    class ValidationEngineTests {

        @Test
        @DisplayName("Should pass validation with valid user data")
        void shouldPassValidation() {
            ValidatedUser user = new ValidatedUser("john", "john@test.com", 25);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).isEmpty();
        }

        @Test
        @DisplayName("Should detect null fields when annotated with validation")
        void shouldDetectNullFields() {
            ValidatedUser user = new ValidatedUser(null, "john@test.com", 25);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("username: Cannot be null");
        }

        @Test
        @DisplayName("Should fail when string length is too short")
        void shouldFailWhenStringTooShort() {
            ValidatedUser user = new ValidatedUser("jo", "john@test.com", 25);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("username: Username must be alphabetic (minimum length is 3)");
        }

        @Test
        @DisplayName("Should fail when string length is too long")
        void shouldFailWhenStringTooLong() {
            ValidatedUser user = new ValidatedUser("johnnyboymax", "john@test.com", 25);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("username: Username must be alphabetic (maximum length is 10)");
        }

        @Test
        @DisplayName("Should fail when string regex does not match")
        void shouldFailWhenRegexMismatch() {
            ValidatedUser user = new ValidatedUser("john123", "john@test.com", 25);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("username: Username must be alphabetic (pattern mismatch)");
        }

        @Test
        @DisplayName("Should fail when number is below minimum")
        void shouldFailWhenNumberBelowMin() {
            ValidatedUser user = new ValidatedUser("john", "john@test.com", 15);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("age: Age must be between 18 and 120 (minimum value is 18.0)");
        }

        @Test
        @DisplayName("Should fail when number is above maximum")
        void shouldFailWhenNumberAboveMax() {
            ValidatedUser user = new ValidatedUser("john", "john@test.com", 150);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactly("age: Age must be between 18 and 120 (maximum value is 120.0)");
        }

        @Test
        @DisplayName("Should collect multiple validation errors")
        void shouldCollectMultipleErrors() {
            ValidatedUser user = new ValidatedUser("jo", "invalid-email", 10);
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(user);
            assertThat(errors).containsExactlyInAnyOrder(
                    "username: Username must be alphabetic (minimum length is 3)",
                    "email: Invalid email format (pattern mismatch)",
                    "age: Age must be between 18 and 120 (minimum value is 18.0)"
            );
        }

        @Test
        @DisplayName("Should return error message when object is null")
        void shouldHandleNullObject() {
            List<String> errors = EliteAnnotationsTraining.ValidationEngine.validate(null);
            assertThat(errors).containsExactly("Object cannot be null");
        }
    }

    // ============================================================================
    // SECTION 3: DEPENDENCY INJECTION CONTAINER TESTS
    // ============================================================================

    @EliteAnnotationsTraining.Component
    static class DatabaseService {
        public String query() { return "data"; }
    }

    @EliteAnnotationsTraining.Component
    static class UserService {
        @EliteAnnotationsTraining.Autowired
        private DatabaseService dbService;

        public String getUserData() {
            return "User: " + dbService.query();
        }
    }

    static class UnannotatedService {}

    @EliteAnnotationsTraining.Component
    static class BrokenService {
        @EliteAnnotationsTraining.Autowired
        private UnannotatedService missingDependency;
    }

    @Nested
    @DisplayName("DiContainer Tests")
    class DiContainerTests {

        @Test
        @DisplayName("Should register components successfully")
        void shouldRegisterComponents() throws Exception {
            EliteAnnotationsTraining.DiContainer container = new EliteAnnotationsTraining.DiContainer();
            container.register(DatabaseService.class);
            
            DatabaseService service = container.getBean(DatabaseService.class);
            assertThat(service).isNotNull();
        }

        @Test
        @DisplayName("Should throw IllegalArgumentException when registering unannotated class")
        void shouldThrowForUnannotatedClass() {
            EliteAnnotationsTraining.DiContainer container = new EliteAnnotationsTraining.DiContainer();
            assertThatThrownBy(() -> container.register(UnannotatedService.class))
                    .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        @DisplayName("Should wire dependencies successfully using @Autowired")
        void shouldWireDependencies() throws Exception {
            EliteAnnotationsTraining.DiContainer container = new EliteAnnotationsTraining.DiContainer();
            container.register(DatabaseService.class);
            container.register(UserService.class);
            
            container.wire();
            
            UserService userService = container.getBean(UserService.class);
            assertThat(userService).isNotNull();
            assertThat(userService.getUserData()).isEqualTo("User: data");
        }

        @Test
        @DisplayName("Should throw IllegalStateException when dependency is missing from container")
        void shouldThrowForMissingDependency() throws Exception {
            EliteAnnotationsTraining.DiContainer container = new EliteAnnotationsTraining.DiContainer();
            container.register(UserService.class); // DatabaseService not registered
            
            assertThatThrownBy(container::wire)
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("Unsatisfied dependency");
        }

        @Test
        @DisplayName("Should register external instances manually")
        void shouldRegisterExternalInstance() throws Exception {
            EliteAnnotationsTraining.DiContainer container = new EliteAnnotationsTraining.DiContainer();
            DatabaseService externalDb = new DatabaseService();
            container.registerInstance(DatabaseService.class, externalDb);
            container.register(UserService.class);
            
            container.wire();
            
            UserService userService = container.getBean(UserService.class);
            assertThat(userService.getUserData()).isEqualTo("User: data");
        }
    }

    // ============================================================================
    // SECTION 4: JSON SERIALIZER TESTS
    // ============================================================================

    @EliteAnnotationsTraining.JsonSerializable
    static class SimpleProduct {
        @EliteAnnotationsTraining.JsonField(name = "product_id")
        private int id;

        private String name;

        @EliteAnnotationsTraining.JsonIgnore
        private double internalCost;

        public SimpleProduct(int id, String name, double internalCost) {
            this.id = id;
            this.name = name;
            this.internalCost = internalCost;
        }
    }

    @EliteAnnotationsTraining.JsonSerializable(formatted = true)
    static class FormattedProduct {
        @EliteAnnotationsTraining.JsonField(name = "product_id")
        private int id;
        private String name;

        public FormattedProduct(int id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    @EliteAnnotationsTraining.JsonSerializable
    static class NestedOrder {
        private String orderId;
        private SimpleProduct product;
        private List<String> tags;
        private Map<String, Integer> items;

        public NestedOrder(String orderId, SimpleProduct product, List<String> tags, Map<String, Integer> items) {
            this.orderId = orderId;
            this.product = product;
            this.tags = tags;
            this.items = items;
        }
    }

    static class UnserializableClass {}

    @Nested
    @DisplayName("JsonSerializer Tests")
    class JsonSerializerTests {

        @Test
        @DisplayName("Should serialize simple object with custom field names and ignored fields")
        void shouldSerializeSimpleObject() throws Exception {
            SimpleProduct product = new SimpleProduct(101, "Laptop", 800.0);
            String json = EliteAnnotationsTraining.JsonSerializer.serialize(product);
            
            assertThat(json).isEqualTo("{\"product_id\":101,\"name\":\"Laptop\"}");
        }

        @Test
        @DisplayName("Should serialize with formatted pretty-printing")
        void shouldSerializeWithFormatting() throws Exception {
            FormattedProduct product = new FormattedProduct(202, "Phone");
            String json = EliteAnnotationsTraining.JsonSerializer.serialize(product);
            
            String expected = "{\n" +
                    "  \"product_id\": 202,\n" +
                    "  \"name\": \"Phone\"\n" +
                    "}";
            assertThat(json).isEqualTo(expected);
        }

        @Test
        @DisplayName("Should serialize complex nested objects, lists, and maps")
        void shouldSerializeNestedObject() throws Exception {
            SimpleProduct product = new SimpleProduct(101, "Laptop", 800.0);
            NestedOrder order = new NestedOrder("ORD-001", product, List.of("tech", "work"), Map.of("qty", 2));
            
            String json = EliteAnnotationsTraining.JsonSerializer.serialize(order);
            
            assertThat(json)
                    .contains("\"orderId\":\"ORD-001\"")
                    .contains("\"product\":{\"product_id\":101,\"name\":\"Laptop\"}")
                    .contains("\"tags\":[\"tech\",\"work\"]")
                    .contains("\"items\":{\"qty\":2}");
        }

        @Test
        @DisplayName("Should throw IllegalArgumentException when class is not annotated with @JsonSerializable")
        void shouldThrowForUnannotatedClass() {
            UnserializableClass obj = new UnserializableClass();
            assertThatThrownBy(() -> EliteAnnotationsTraining.JsonSerializer.serialize(obj))
                    .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        @DisplayName("Should handle null values gracefully in serialization")
        void shouldHandleNullValues() throws Exception {
            SimpleProduct product = new SimpleProduct(101, null, 800.0);
            String json = EliteAnnotationsTraining.JsonSerializer.serialize(product);
            
            assertThat(json).isEqualTo("{\"product_id\":101,\"name\":null}");
        }
    }

    // ============================================================================
    // SECTION 5: CUSTOM TEST RUNNER TESTS
    // ============================================================================

    @EliteAnnotationsTraining.TestSuite(name = "Sample Math Tests")
    public static class SampleMathTests {
        private int value = 0;

        @EliteAnnotationsTraining.TestMethod(order = 1)
        public void testInit() {
            value = 5;
        }

        @EliteAnnotationsTraining.TestMethod(order = 2)
        public void testAdd() {
            if (value != 5) {
                throw new IllegalStateException("Not initialized!");
            }
            value += 10;
        }

        @EliteAnnotationsTraining.TestMethod(order = 3, expectedException = IllegalArgumentException.class)
        public void testExceptionExpected() {
            throw new IllegalArgumentException("Expected exception");
        }

        @EliteAnnotationsTraining.TestMethod(order = 4, expectedException = NullPointerException.class)
        public void testExceptionExpectedButFailed() {
            // Throws wrong exception
            throw new IllegalArgumentException("Wrong exception");
        }
    }

    @Nested
    @DisplayName("CustomTestRunner Tests")
    class CustomTestRunnerTests {

        @Test
        @DisplayName("Should run test suite and return correct results including orders and expected exceptions")
        void shouldRunTestSuite() throws Exception {
            EliteAnnotationsTraining.CustomTestRunner.SuiteResult result = 
                    EliteAnnotationsTraining.CustomTestRunner.run(SampleMathTests.class);

            assertThat(result.getSuiteName()).isEqualTo("Sample Math Tests");
            assertThat(result.getPassedCount()).isEqualTo(3);
            assertThat(result.getFailedCount()).isEqualTo(1);

            List<EliteAnnotationsTraining.CustomTestRunner.TestResult> testResults = result.getResults();
            assertThat(testResults).hasSize(4);

            assertThat(testResults.get(0).getMethodName()).isEqualTo("testInit");
            assertThat(testResults.get(0).isPassed()).isTrue();

            assertThat(testResults.get(1).getMethodName()).isEqualTo("testAdd");
            assertThat(testResults.get(1).isPassed()).isTrue();

            assertThat(testResults.get(2).getMethodName()).isEqualTo("testExceptionExpected");
            assertThat(testResults.get(2).isPassed()).isTrue();

            assertThat(testResults.get(3).getMethodName()).isEqualTo("testExceptionExpectedButFailed");
            assertThat(testResults.get(3).isPassed()).isFalse();
            assertThat(testResults.get(3).getError()).isInstanceOf(IllegalArgumentException.class);
        }
    }
}