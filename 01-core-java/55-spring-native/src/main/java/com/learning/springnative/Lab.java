package com.learning.springnative;

import java.util.*;
import java.util.function.*;
import java.lang.reflect.*;

public class Lab {

    static class NativeAwareBean {
        private final String name;
        private final Map<String, Object> properties = new LinkedHashMap<>();

        NativeAwareBean(String name) { this.name = name; }
        void setProperty(String key, Object value) { properties.put(key, value); }
        Object getProperty(String key) { return properties.get(key); }
        public String toString() { return name + properties; }
    }

    static class SimpleApplicationContext {
        private final Map<String, NativeAwareBean> beans = new LinkedHashMap<>();

        void registerBean(String name, NativeAwareBean bean) {
            beans.put(name, bean);
        }

        <T> T getBean(String name, Class<T> type) {
            return type.cast(beans.get(name));
        }

        void refresh() {
            System.out.println("  Context refreshed with " + beans.size() + " beans");
            beans.forEach((k, v) -> System.out.println("    " + k + " -> " + v));
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("=== Spring Native Lab ===\n");

        nativeImageConcepts();
        graalVmVsJvm();
        aheadOfTimeCompilation();
        reflectionConfiguration();
        resourceConfiguration();
        springNativeFeatures();
    }

    static void nativeImageConcepts() {
        System.out.println("--- Native Image Concepts ---");
        var ctx = new SimpleApplicationContext();
        var bean = new NativeAwareBean("userService");
        bean.setProperty("url", "http://localhost:8080");
        bean.setProperty("timeout", 5000);
        ctx.registerBean("userService", bean);
        ctx.refresh();

        System.out.println("""
  GraalVM Native Image: AOT compilation of bytecode -> native binary
  Benefits:
  - Fast startup (<100ms vs 2-5s for JVM)
  - Low memory (20-50MB vs 200-500MB for JVM)
  - No JIT warmup needed
  - Smaller container images (distroless compatible)

  Trade-offs:
  - Slower peak performance (no JIT optimization)
  - Longer build time (minutes vs seconds)
  - Limited runtime reflection/proxy
    """);
    }

    static void graalVmVsJvm() {
        System.out.println("\n--- GraalVM vs Traditional JVM ---");
        System.out.println("""
  | Aspect            | Traditional JVM      | GraalVM Native Image |
  |-------------------|---------------------|----------------------|
  | Startup time      | 2-5s                | <100ms               |
  | Memory (hello w.) | ~200MB              | ~20MB                |
  | Peak throughput   | JIT optimizes       | AOT limited          |
  | Build time        | Instant             | 2-5 minutes          |
  | Reflection        | Full support        | Needs config         |
  | Debugging         | Standard            | GDB / native debug   |

  Spring Boot 3 + GraalVM:
  - @Configuration with proxyBeanMethods=false
  - No dynamic class loading / CGLIB proxies
  - No log4j2 (logback preferred)
    """);
    }

    static void aheadOfTimeCompilation() {
        System.out.println("\n--- AOT Compilation ---");
        System.out.println("""
  AOT processing pipeline:
  1. Analyze reachable code (closed-world assumption)
  2. Static initialization: run class initializers at build time
  3. Compile bytecode to machine code
  4. Create native executable

  Spring AOT:
  - SpringApplication converted to .aot sources
  - Bean definitions processed at build time
  - Proxy configurations pre-generated
  - No runtime bean definition parsing

  Maven plugin:
  <plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
    <configuration><imageName>my-app</imageName></configuration>
  </plugin>
    """);
    }

    static void reflectionConfiguration() throws Exception {
        System.out.println("\n--- Reflection Configuration ---");
        var target = new NativeAwareBean("reflective");

        var method = NativeAwareBean.class.getDeclaredMethod("setProperty", String.class, Object.class);
        method.setAccessible(true);
        method.invoke(target, "key1", "value1");

        var field = NativeAwareBean.class.getDeclaredField("properties");
        field.setAccessible(true);
        @SuppressWarnings("unchecked")
        var props = (Map<String, Object>) field.get(target);
        System.out.println("  Reflective access: " + props);

        System.out.println("""
  For native-image, register reflection:
  --reflect-config:
  [{
    "name":"com.example.MyClass",
    "methods":[{"name":"myMethod","parameterTypes":["java.lang.String"]}]
  }]

  Or use @RegisterReflectionForBinding in Spring
  Or GraalVM tracing agent: -agentlib:native-image-agent=config-output-dir=config/
    """);
    }

    static void resourceConfiguration() {
        System.out.println("\n--- Resource Configuration ---");
        System.out.println("""
  Native image bundles resources into the binary:
  --resource-config:
  {
    "pattern":"\\\\Qapplication.yml\\\\E"
  }

  Spring Boot resources:
  - application.yml/properties -> included automatically
  - Static files (public/, templates/) -> need config
  - i18n messages -> need config

  GraalVM reachability metadata:
  - Central repo: https://github.com/graalvm/native-build-tools
  - Pre-built configs for common libraries
  - Spring Boot starter automatically includes metadata
    """);
    }

    static void springNativeFeatures() {
        System.out.println("--- Spring Native Features (Spring Boot 3 + AOT) ---");
        System.out.println("""
  Key features:
  - @Configuration(proxyBeanMethods = false) - avoid CGLIB
  - Constructor injection preferred over field injection
  - @EnableConfigurationProperties with @ConstructorBinding
  - No persistence.xml / orm.xml (use Spring config)
  - No embedded scripting (Groovy, etc.)

  Supported:
  - Spring MVC / WebFlux
  - Spring Data JPA (Hibernate)
  - Spring Security
  - Spring Cloud Function
  - Kafka / RabbitMQ clients

  Not supported:
  - Many dynamic features (Groovy, JRuby)
  - Java Agents (except at build time)
  - Arbitrary reflection/proxy without config
    """);
    }
}
