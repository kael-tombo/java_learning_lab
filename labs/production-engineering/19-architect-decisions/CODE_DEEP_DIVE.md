# CODE DEEP DIVE: Architectural Governance & Fitness Functions
## Lab 19 | Production Engineering Academy

---

## Pattern 1: Production ArchUnit Architectural Fitness Function (CI Gate)

Fitness functions enforce architectural boundaries in automated tests, preventing architectural decay over time.

```java
package com.learning.production.lab19;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

public class ArchitectureFitnessFunctionTest {

    private static JavaClasses importedClasses;

    @BeforeAll
    public static void setup() {
        importedClasses = new ClassFileImporter().importPackages("com.learning.production");
    }

    /**
     * Fitness Rule 1: Layered Architecture Invariant
     * Domain layer must NEVER depend on Infrastructure, Web, or DB layers.
     */
    @Test
    public void domainLayerMustBeIndependent() {
        ArchRule rule = noClasses().that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAnyPackage("..web..", "..infrastructure..", "..persistence..");

        rule.check(importedClasses);
    }

    /**
     * Fitness Rule 2: Persistence Layer Invariant
     * Only Repositories may access EntityManager or JPA annotations.
     */
    @Test
    public void controllersMustNeverAccessRepositoriesDirectly() {
        ArchRule rule = noClasses().that().resideInAPackage("..web..")
                .should().dependOnClassesThat().resideInAPackage("..persistence..");

        rule.check(importedClasses);
    }

    /**
     * Fitness Rule 3: Thread Safety
     * Spring Controllers and Services must be stateless (no mutable instance fields).
     */
    @Test
    public void servicesMustBeStateless() {
        ArchRule rule = classes().that().resideInAPackage("..service..")
                .and().areAnnotatedWith("org.springframework.stereotype.Service")
                .should().haveOnlyFinalFields();

        rule.check(importedClasses);
    }
}
```

---

## Pattern 2: Production ADR Markdown Template (Michael Nygard Standard)

```markdown
# ADR-[NUMBER]: [SHORT TITLE OF DECISION]

* **Status**: [PROPOSED | ACCEPTED | REJECTED | DEPRECATED | SUPERSEDED by ADR-xxx]
* **Deciders**: [Architect Name, Lead Engineer Name]
* **Date**: [YYYY-MM-DD]
* **Decision Type**: [Type 1: Irreversible | Type 2: Reversible]

## Context & Problem Statement
[Describe the context, business forces, and technical problem requiring a decision. Include relevant background metrics, constraints, and non-negotiable requirements.]

## Decision Drivers
* [Driver 1: e.g. p99 latency < 25ms under 50,000 req/s]
* [Driver 2: Zero data loss guarantee (financial auditability)]
* [Driver 3: Operational overhead on current team size]

## Considered Options
* **Option 1**: [Description]
* **Option 2**: [Description]
* **Option 3**: [Description]

## Pros and Cons of the Options

### Option 1: [Name]
* Good, because [positive consequence]
* Bad, because [drawback / trade-off]

### Option 2: [Name]
* Good, because [positive consequence]
* Bad, because [drawback / trade-off]

## Decision Outcome
Chosen option: **[Option Name]**, because [justification linking to Decision Drivers].

### Positive Consequences
* [Benefit 1]
* [Benefit 2]

### Negative Consequences / Accepted Trade-offs
* [Accepted technical debt or complexity]
* [Mitigation planned for drawbacks]

## Compliance & Enforcement
[How this decision will be validated: e.g. ArchUnit fitness function in CI, linters, pre-commit checks.]
```
