package com.learning.reflection;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite Reflection Training Tests")
class EliteReflectionTrainingTest {

    // ============================================================================
    // INTROSPECTOR
    // ============================================================================

    static class BaseBean {
        private static int counter;              // static: must be skipped
        protected String inherited = "base";
    }

    static class DerivedBean extends BaseBean {
        public String own = "derived";
        private int secret = 7;
    }

    @Nested
    @DisplayName("Introspector Tests")
    class IntrospectorTests {

        @Test
        @DisplayName("instanceFields should walk hierarchy, skip statics and synthetics")
        void instanceFieldsWalksHierarchy() {
            List<Field> fields = EliteReflectionTraining.Introspector.instanceFields(DerivedBean.class);
            assertThat(fields)
                    .extracting(Field::getName)
                    .containsExactlyInAnyOrder("inherited", "own", "secret");
        }

        @Test
        @DisplayName("annotatedMethods should find @Command methods including inherited")
        void annotatedMethodsFound() {
            List<Method> methods = EliteReflectionTraining.Introspector.annotatedMethods(
                    EliteReflectionTraining.CalculatorCommands.class, EliteReflectionTraining.Command.class);
            assertThat(methods)
                    .extracting(Method::getName)
                    .containsExactlyInAnyOrder("add", "echo", "fail");
        }

        @Test
        @DisplayName("methodSignature should format return type, name, and parameters")
        void signatureFormatting() throws Exception {
            Method add = EliteReflectionTraining.CalculatorCommands.class.getDeclaredMethod("add", int.class, int.class);
            assertThat(EliteReflectionTraining.Introspector.methodSignature(add))
                    .isEqualTo("int add(int, int)");
        }

        @Test
        @DisplayName("toFieldMap should expose private field values")
        void toFieldMapReadsPrivates() throws Exception {
            DerivedBean bean = new DerivedBean();
            Map<String, Object> map = EliteReflectionTraining.Introspector.toFieldMap(bean);
            assertThat(map)
                    .containsEntry("own", "derived")
                    .containsEntry("secret", 7)
                    .containsEntry("inherited", "base");
        }
    }

    // ============================================================================
    // COMMAND DISPATCHER
    // ============================================================================

    @Nested
    @DisplayName("CommandDispatcher Tests")
    class DispatcherTests {

        @Test
        @DisplayName("Should dispatch annotated methods by name with arguments")
        void dispatchesByName() throws Exception {
            EliteReflectionTraining.CommandDispatcher dispatcher =
                    new EliteReflectionTraining.CommandDispatcher(new EliteReflectionTraining.CalculatorCommands());

            assertThat(dispatcher.dispatch("add", 2, 3)).isEqualTo(5);
            assertThat(dispatcher.dispatch("echo", "hi")).isEqualTo("echo: hi");
        }

        @Test
        @DisplayName("commandNames should list all registered commands")
        void listsCommandNames() {
            EliteReflectionTraining.CommandDispatcher dispatcher =
                    new EliteReflectionTraining.CommandDispatcher(new EliteReflectionTraining.CalculatorCommands());

            assertThat(dispatcher.commandNames()).containsExactlyInAnyOrder("add", "echo", "fail");
        }

        @Test
        @DisplayName("Dispatch of unknown command should throw NoSuchElementException")
        void unknownCommandThrows() {
            EliteReflectionTraining.CommandDispatcher dispatcher =
                    new EliteReflectionTraining.CommandDispatcher(new EliteReflectionTraining.CalculatorCommands());

            assertThatThrownBy(() -> dispatcher.dispatch("nope"))
                    .isInstanceOf(java.util.NoSuchElementException.class)
                    .hasMessageContaining("Unknown command");
        }

        @Test
        @DisplayName("Business exceptions thrown in commands should propagate unwrapped")
        void businessExceptionsPropagate() {
            EliteReflectionTraining.CommandDispatcher dispatcher =
                    new EliteReflectionTraining.CommandDispatcher(new EliteReflectionTraining.CalculatorCommands());

            assertThatThrownBy(() -> dispatcher.dispatch("fail"))
                    .isInstanceOf(ArithmeticException.class)
                    .hasMessageContaining("intentional failure");
        }

        @Test
        @DisplayName("Handler with no @Command methods should be rejected")
        void emptyHandlerRejected() {
            assertThatThrownBy(() -> new EliteReflectionTraining.CommandDispatcher(new Object()))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("no @Command");
        }

        @Test
        @DisplayName("Duplicate command names should be rejected at construction")
        void duplicateNamesRejected() {
            class Dup {
                @EliteReflectionTraining.Command(name = "same")
                public void one() {}
                @EliteReflectionTraining.Command(name = "same")
                public void two() {}
            }
            assertThatThrownBy(() -> new EliteReflectionTraining.CommandDispatcher(new Dup()))
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("Duplicate command");
        }
    }

    // ============================================================================
    // OBJECT MAPPER
    // ============================================================================

    static class SourceEntity {
        public String name = "Ada";
        public int age = 36;
        public String nickname = "ada-l";
        public String internal = "must-not-copy";
    }

    static class TargetDto {
        @EliteReflectionTraining.MappedFrom("name")
        public String fullName;

        public long age;                       // int -> long conversion

        public String nickname;                // identity copy

        @EliteReflectionTraining.IgnoreMapping
        public String internal;                // must stay null
    }

    @Nested
    @DisplayName("ObjectMapper Tests")
    class MapperTests {

        @Test
        @DisplayName("Should map fields with rename and numeric conversion")
        void mapsWithConversion() throws Exception {
            TargetDto dto =
                    EliteReflectionTraining.ObjectMapper.map(new SourceEntity(), TargetDto.class);

            assertThat(dto.fullName).isEqualTo("Ada");
            assertThat(dto.age).isEqualTo(36L);
            assertThat(dto.nickname).isEqualTo("ada-l");
        }

        @Test
        @DisplayName("Fields annotated @IgnoreMapping should never be populated")
        void ignoreMappingHonored() throws Exception {
            TargetDto dto =
                    EliteReflectionTraining.ObjectMapper.map(new SourceEntity(), TargetDto.class);
            assertThat(dto.internal).isNull();
        }

        @Test
        @DisplayName("Missing source fields should leave target defaults untouched")
        void missingSourceLeavesDefault() throws Exception {
            record Minimal(String name) {}
            TargetDto dto =
                    EliteReflectionTraining.ObjectMapper.map(new Minimal("Bo"), TargetDto.class);

            assertThat(dto.fullName).isEqualTo("Bo");
            assertThat(dto.age).isZero();
        }

        @Test
        @DisplayName("String to number conversion should work")
        void stringToNumber() {
            assertThat(EliteReflectionTraining.ObjectMapper.convert("42", int.class)).isEqualTo(42);
            assertThat(EliteReflectionTraining.ObjectMapper.convert("3.5", double.class)).isEqualTo(3.5);
            assertThat(EliteReflectionTraining.ObjectMapper.convert("true", boolean.class)).isEqualTo(true);
        }

        @Test
        @DisplayName("Impossible conversions should throw with a clear message")
        void impossibleConversionThrows() {
            assertThatThrownBy(() -> EliteReflectionTraining.ObjectMapper.convert(new Object(), int.class))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Cannot convert");
            assertThatThrownBy(() -> EliteReflectionTraining.ObjectMapper.convert("abc", int.class))
                    .isInstanceOf(NumberFormatException.class);
        }
    }

    // ============================================================================
    // DYNAMIC PROXY
    // ============================================================================

    @Nested
    @DisplayName("Dynamic Proxy Tests")
    class ProxyTests {

        @Test
        @DisplayName("Proxy should delegate calls to the target")
        void proxyDelegates() {
            EliteReflectionTraining.Greeter proxy = EliteReflectionTraining.LoggingProxy.create(
                    EliteReflectionTraining.Greeter.class, new EliteReflectionTraining.SimpleGreeter());

            assertThat(proxy.greet("Ada")).isEqualTo("Hello, Ada!");
            assertThat(proxy.farewell("Ada")).isEqualTo("Goodbye, Ada.");
        }

        @Test
        @DisplayName("Proxy should record every interface call")
        void proxyLogsCalls() {
            EliteReflectionTraining.Greeter proxy = EliteReflectionTraining.LoggingProxy.create(
                    EliteReflectionTraining.Greeter.class, new EliteReflectionTraining.SimpleGreeter());

            proxy.greet("X");
            proxy.farewell("Y");

            List<String> log = ((EliteReflectionTraining.LoggingProxy) java.lang.reflect.Proxy.getInvocationHandler(proxy)).getCallLog();
            assertThat(log).hasSize(2);
            assertThat(log.get(0)).startsWith("greet");
            assertThat(log.get(1)).startsWith("farewell");
            assertThat(log.get(0)).contains("->"); // timing suffix present
        }

        @Test
        @DisplayName("Proxy should be an instance of the requested interface")
        void proxyImplementsInterface() {
            EliteReflectionTraining.Greeter proxy = EliteReflectionTraining.LoggingProxy.create(
                    EliteReflectionTraining.Greeter.class, new EliteReflectionTraining.SimpleGreeter());

            assertThat(proxy).isInstanceOf(EliteReflectionTraining.Greeter.class);
        }

        @Test
        @DisplayName("Object methods (toString/hashCode) should delegate without logging")
        void objectMethodsDelegate() {
            EliteReflectionTraining.Greeter proxy = EliteReflectionTraining.LoggingProxy.create(
                    EliteReflectionTraining.Greeter.class, new EliteReflectionTraining.SimpleGreeter());

            assertThat(proxy.toString()).isNotBlank();

            List<String> log = ((EliteReflectionTraining.LoggingProxy) java.lang.reflect.Proxy.getInvocationHandler(proxy)).getCallLog();
            assertThat(log).isEmpty();
        }
    }

    // ============================================================================
    // DEMO SMOKE TEST
    // ============================================================================

    @Test
    @DisplayName("demonstrate() should run all reflection demos without throwing")
    void demoRunsCleanly() {
        assertThatCode(EliteReflectionTraining::demonstrate).doesNotThrowAnyException();
    }
}
