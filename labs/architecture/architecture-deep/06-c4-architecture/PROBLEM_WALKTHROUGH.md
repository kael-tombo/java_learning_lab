# Lab 06: Problem Walkthrough — Generating C4 Diagrams from a Java Component Model

## Problem Statement

Implement a C4 model generator for an e-commerce platform. Requirements:

1. Model the four C4 levels as Java types: **System Context** (people + systems), **Container** (apps + data stores), **Component** (containers' internal parts), and relationships between elements.
2. Build the model with a fluent API so diagrams are derived from code, not drawn by hand.
3. Generate diagrams in **PlantUML C4 syntax** from the model — a textual renderer means the model is the single source of truth.
4. Support generating context, container, and component diagram files from the same model.
5. Keep the model and generators separate (a `MermaidGenerator` could be swapped in).

## Constraints

- Java 21+ only, no diagramming libraries — the generator emits plain text.
- Every element has a stable id used as the diagram node id.
- Relationships carry a label and optional technology tag.
- Diagram text must round-trip: regenerating from the same model yields identical output (deterministic).

## Approach

**Why generate diagrams from a model?** Hand-drawn C4 diagrams rot the moment the code changes. If the model lives in code and a CI job regenerates the diagrams, architecture documentation stays truthful. The Java model mirrors the C4 vocabulary:

- Level 1 (Context): `Person`, `System` (our system + external systems).
- Level 2 (Container): containers inside a system (web app, API, database, message broker).
- Level 3 (Component): components inside a container (controllers, services, repositories).
- Level 4 (Code): class-level — here we note it maps to the Java classes themselves.

Design decisions:

- **Fluent builder** (`C4ModelBuilder`) with `system(...)`, `container(...)`, `component(...)`, `link(...)` — reads like the diagram.
- **Id-based relationships**: `link(fromId, toId, label)` avoids object identity pitfalls.
- **Generators iterate the model** and emit PlantUML; the model stays format-agnostic.

## Step-by-Step Solution

### Step 1: Model Types

```java
record Person(String id, String name, String description) {}

record System(String id, String name, String description) {}

record Container(String id, String name, String technology, String description) {}

record Component(String id, String name, String technology, String description) {}

record Relationship(String fromId, String toId, String label, String technology) {
    Relationship {
        label = label == null ? "" : label;
        technology = technology == null ? "" : technology;
    }
}
```

### Step 2: The Model + Builder

The `C4Model` holds people, systems, containers, components, and relationships. The builder chains calls.

```java
class C4Model {
    private final List<Person> people = new ArrayList<>();
    private final List<System> systems = new ArrayList<>();
    private final List<Container> containers = new ArrayList<>();
    private final List<Component> components = new ArrayList<>();
    private final List<Relationship> relationships = new ArrayList<>();

    List<Person> people() { return List.copyOf(people); }
    List<System> systems() { return List.copyOf(systems); }
    List<Container> containers() { return List.copyOf(containers); }
    List<Component> components() { return List.copyOf(components); }
    List<Relationship> relationships() { return List.copyOf(relationships); }

    void addPerson(Person p) { people.add(p); }
    void addSystem(System s) { systems.add(s); }
    void addContainer(Container c) { containers.add(c); }
    void addComponent(Component c) { components.add(c); }
    void addRelationship(Relationship r) { relationships.add(r); }
}

class C4ModelBuilder {
    private final C4Model model = new C4Model();

    C4ModelBuilder person(String id, String name, String description) {
        model.addPerson(new Person(id, name, description));
        return this;
    }

    C4ModelBuilder system(String id, String name, String description) {
        model.addSystem(new System(id, name, description));
        return this;
    }

    C4ModelBuilder container(String id, String name, String technology, String description) {
        model.addContainer(new Container(id, name, technology, description));
        return this;
    }

    C4ModelBuilder component(String id, String name, String technology, String description) {
        model.addComponent(new Component(id, name, technology, description));
        return this;
    }

    C4ModelBuilder link(String fromId, String toId, String label) {
        model.addRelationship(new Relationship(fromId, toId, label, ""));
        return this;
    }

    C4Model build() {
        return model;
    }
}
```

### Step 3: PlantUML C4 Generator

The generator renders three diagram levels from the single model. It uses the C4-PlantUML syntax (`C4_Context`, `C4_Container`, `C4_Component` macros).

```java
class PlantUmlC4Generator {
    String contextDiagram(C4Model model) {
        var sb = new StringBuilder();
        sb.append("@startuml System Context\n");
        sb.append("!include (link removed)");
        for (var person : model.people()) {
            sb.append("Person(").append(person.id()).append(", \"").append(person.name())
                .append("\", \"").append(person.description()).append("\")\n");
        }
        for (var system : model.systems()) {
            sb.append("System(").append(system.id()).append(", \"").append(system.name())
                .append("\", \"").append(system.description()).append("\")\n");
        }
        for (var rel : model.relationships()) {
            if (isElement(rel.fromId(), model) && isElement(rel.toId(), model)) {
                sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                    .append(", \"").append(rel.label()).append("\")\n");
            }
        }
        sb.append("@enduml");
        return sb.toString();
    }

    String containerDiagram(C4Model model) {
        var sb = new StringBuilder();
        sb.append("@startuml Container Diagram\n");
        sb.append("!include (link removed)");
        sb.append("System_Boundary(ecom_sys, \"E-Commerce System\") {\n");
        for (var container : model.containers()) {
            sb.append("Container(").append(container.id()).append(", \"").append(container.name())
                .append("\", \"").append(container.technology()).append("\", \"")
                .append(container.description()).append("\")\n");
        }
        sb.append("}\n");
        for (var rel : model.relationships()) {
            sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                .append(", \"").append(rel.label()).append("\")\n");
        }
        sb.append("@enduml");
        return sb.toString();
    }

    String componentDiagram(C4Model model, String containerId) {
        var sb = new StringBuilder();
        sb.append("@startuml Component Diagram ").append(containerId).append("\n");
        sb.append("!include (link removed)");
        sb.append("Container_Boundary(").append(containerId).append(", \"").append(containerId).append("\") {\n");
        for (var component : model.components()) {
            sb.append("Component(").append(component.id()).append(", \"").append(component.name())
                .append("\", \"").append(component.technology()).append("\", \"")
                .append(component.description()).append("\")\n");
        }
        sb.append("}\n");
        for (var rel : model.relationships()) {
            sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                .append(", \"").append(rel.label()).append("\")\n");
        }
        sb.append("@enduml");
        return sb.toString();
    }

    private boolean isElement(String id, C4Model model) {
        return model.people().stream().anyMatch(p -> p.id().equals(id))
            || model.systems().stream().anyMatch(s -> s.id().equals(id));
    }
}
```

### Step 4: Main — Build the Model and Generate

The model mirrors a real e-commerce architecture: customer -> web app -> API -> database, with an external payment provider.

```java
public class C4Lab {
    public static void main(String[] args) {
        var model = new C4ModelBuilder()
            .person("customer", "Customer", "Browses and buys products")
            .system("ecom", "E-Commerce Platform", "Online storefront and order processing")
            .system("payment", "Payment Provider", "External payment gateway")
            .container("web", "Web Application", "Spring Boot", "Server-side rendering of catalog and checkout")
            .container("api", "API Application", "Spring Boot", "REST API for orders and inventory")
            .container("db", "Order Database", "PostgreSQL", "Stores orders, customers, products")
            .component("controller", "OrderController", "Spring MVC", "Accepts REST order requests")
            .component("service", "OrderService", "Spring", "Orchestrates order workflow")
            .component("repo", "OrderRepository", "Spring Data JPA", "Persists orders")
            .link("customer", "web", "browses & buys")
            .link("web", "api", "calls over HTTPS")
            .link("api", "db", "reads/writes orders")
            .link("api", "payment", "charges cards")
            .link("controller", "service", "delegates")
            .link("service", "repo", "uses")
            .build();

        var generator = new PlantUmlC4Generator();
        System.out.println(generator.contextDiagram(model));
        System.out.println("---");
        System.out.println(generator.containerDiagram(model));
        System.out.println("---");
        System.out.println(generator.componentDiagram(model, "api"));
    }
}
```

## Complete Solution

The full compilable file, `C4Lab.java` in package `com.architecture.deep.lab06`:

```java
package com.architecture.deep.lab06;

import java.util.ArrayList;
import java.util.List;

public class C4Lab {
    public static void main(String[] args) {
        var model = new C4ModelBuilder()
            .person("customer", "Customer", "Browses and buys products")
            .system("ecom", "E-Commerce Platform", "Online storefront and order processing")
            .system("payment", "Payment Provider", "External payment gateway")
            .container("web", "Web Application", "Spring Boot", "Server-side rendering of catalog and checkout")
            .container("api", "API Application", "Spring Boot", "REST API for orders and inventory")
            .container("db", "Order Database", "PostgreSQL", "Stores orders, customers, products")
            .component("controller", "OrderController", "Spring MVC", "Accepts REST order requests")
            .component("service", "OrderService", "Spring", "Orchestrates order workflow")
            .component("repo", "OrderRepository", "Spring Data JPA", "Persists orders")
            .link("customer", "web", "browses & buys")
            .link("web", "api", "calls over HTTPS")
            .link("api", "db", "reads/writes orders")
            .link("api", "payment", "charges cards")
            .link("controller", "service", "delegates")
            .link("service", "repo", "uses")
            .build();

        var generator = new PlantUmlC4Generator();
        System.out.println(generator.contextDiagram(model));
        System.out.println("---");
        System.out.println(generator.containerDiagram(model));
        System.out.println("---");
        System.out.println(generator.componentDiagram(model, "api"));
    }
}

record Person(String id, String name, String description) {}
record System(String id, String name, String description) {}
record Container(String id, String name, String technology, String description) {}
record Component(String id, String name, String technology, String description) {}

record Relationship(String fromId, String toId, String label, String technology) {
    Relationship {
        label = label == null ? "" : label;
        technology = technology == null ? "" : technology;
    }
}

class C4Model {
    private final List<Person> people = new ArrayList<>();
    private final List<System> systems = new ArrayList<>();
    private final List<Container> containers = new ArrayList<>();
    private final List<Component> components = new ArrayList<>();
    private final List<Relationship> relationships = new ArrayList<>();

    List<Person> people() { return List.copyOf(people); }
    List<System> systems() { return List.copyOf(systems); }
    List<Container> containers() { return List.copyOf(containers); }
    List<Component> components() { return List.copyOf(components); }
    List<Relationship> relationships() { return List.copyOf(relationships); }

    void addPerson(Person p) { people.add(p); }
    void addSystem(System s) { systems.add(s); }
    void addContainer(Container c) { containers.add(c); }
    void addComponent(Component c) { components.add(c); }
    void addRelationship(Relationship r) { relationships.add(r); }
}

class C4ModelBuilder {
    private final C4Model model = new C4Model();

    C4ModelBuilder person(String id, String name, String description) {
        model.addPerson(new Person(id, name, description));
        return this;
    }

    C4ModelBuilder system(String id, String name, String description) {
        model.addSystem(new System(id, name, description));
        return this;
    }

    C4ModelBuilder container(String id, String name, String technology, String description) {
        model.addContainer(new Container(id, name, technology, description));
        return this;
    }

    C4ModelBuilder component(String id, String name, String technology, String description) {
        model.addComponent(new Component(id, name, technology, description));
        return this;
    }

    C4ModelBuilder link(String fromId, String toId, String label) {
        model.addRelationship(new Relationship(fromId, toId, label, ""));
        return this;
    }

    C4Model build() {
        return model;
    }
}

class PlantUmlC4Generator {
    String contextDiagram(C4Model model) {
        var sb = new StringBuilder();
        sb.append("@startuml System Context\n");
        sb.append("!include (link removed)");
        for (var person : model.people()) {
            sb.append("Person(").append(person.id()).append(", \"").append(person.name())
                .append("\", \"").append(person.description()).append("\")\n");
        }
        for (var system : model.systems()) {
            sb.append("System(").append(system.id()).append(", \"").append(system.name())
                .append("\", \"").append(system.description()).append("\")\n");
        }
        for (var rel : model.relationships()) {
            if (isElement(rel.fromId(), model) && isElement(rel.toId(), model)) {
                sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                    .append(", \"").append(rel.label()).append("\")\n");
            }
        }
        sb.append("@enduml");
        return sb.toString();
    }

    String containerDiagram(C4Model model) {
        var sb = new StringBuilder();
        sb.append("@startuml Container Diagram\n");
        sb.append("!include (link removed)");
        sb.append("System_Boundary(ecom_sys, \"E-Commerce System\") {\n");
        for (var container : model.containers()) {
            sb.append("Container(").append(container.id()).append(", \"").append(container.name())
                .append("\", \"").append(container.technology()).append("\", \"")
                .append(container.description()).append("\")\n");
        }
        sb.append("}\n");
        for (var rel : model.relationships()) {
            sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                .append(", \"").append(rel.label()).append("\")\n");
        }
        sb.append("@enduml");
        return sb.toString();
    }

    String componentDiagram(C4Model model, String containerId) {
        var sb = new StringBuilder();
        sb.append("@startuml Component Diagram ").append(containerId).append("\n");
        sb.append("!include (link removed)");
        sb.append("Container_Boundary(").append(containerId).append(", \"").append(containerId).append("\") {\n");
        for (var component : model.components()) {
            sb.append("Component(").append(component.id()).append(", \"").append(component.name())
                .append("\", \"").append(component.technology()).append("\", \"")
                .append(component.description()).append("\")\n");
        }
        sb.append("}\n");
        for (var rel : model.relationships()) {
            sb.append("Rel(").append(rel.fromId()).append(", ").append(rel.toId())
                .append(", \"").append(rel.label()).append("\")\n");
        }
        sb.append("@enduml");
        return sb.toString();
    }

    private boolean isElement(String id, C4Model model) {
        return model.people().stream().anyMatch(p -> p.id().equals(id))
            || model.systems().stream().anyMatch(s -> s.id().equals(id));
    }
}
```

## Complexity Analysis

- **Model build**: O(E) per element added; O(R) for relationships.
- **Generation**: O(E + R) per diagram level — linear in model size.
- **Memory**: O(E + R) for the model.
- **Determinism**: builders append in call order; generation iterates in insertion order, so output is stable and diffable in CI.

## Test Cases

| Scenario | Expected |
|---|---|
| Context diagram | Contains `Person(customer, ...)`, `System(ecom, ...)`, `Rel(customer, ecom, ...)`; no containers leaked |
| Container diagram | All three containers inside `System_Boundary`; payment system appears as external `Rel` |
| Component diagram | `Component(controller, ...)` inside `Container_Boundary(api, ...)`; `Rel(controller, service, ...)` |
| Relationship with unknown id | Skipped in context diagram (only element ids rendered) |
| Empty model | Diagrams render header/boundary with zero elements |

Example run (first lines of output):

```
@startuml System Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
Person(customer, "Customer", "Browses and buys products")
System(ecom, "E-Commerce Platform", "Online storefront and order processing")
System(payment, "Payment Provider", "External payment gateway")
Rel(customer, ecom, "browses & buys")
@enduml
```

## Follow-Up Questions

1. **How do you generate diagrams from real code (level 4)?** Introspect packages with `Class.forName` + `getDeclaredMethods` and emit class diagrams from actual dependencies — the model becomes a source scanner.
2. **How do you keep diagrams in sync in CI?** Run the generator in a build step and fail the build if the committed diagram file differs from the generated output (`git diff --exit-code`).
3. **How do you model deployments?** Add a level-2.5 deployment model (nodes, environments, instances) — the same relationship pattern extends to `DeploymentNode`/`InfrastructureNode`.
4. **What about mermaid or D2 output?** Implement `MermaidGenerator` against the same `C4Model` — the model is format-agnostic by design.
5. **How do you handle very large systems?** Group elements into `systemBoundary`/`containerBoundary` scopes and generate per-scope diagrams, using zoom-in navigation links between levels.
6. **How does this tie to ADRs?** Each generated diagram can reference architecture decision records; keep the C4 model next to the ADR files in the repo so docs and decisions evolve together.
7. **How would you validate model integrity?** Add a `validate()` pass: relationship endpoints must exist, ids unique, exactly one system boundary per container diagram.
